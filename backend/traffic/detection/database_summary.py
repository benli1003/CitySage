import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv()

# database
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# OpenAI API configuration
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_KEY")
MODEL = "gpt-4.1-nano"

# Initialize OpenAI client
try:
    client = OpenAI(
        base_url=OPENAI_ENDPOINT,
        api_key=OPENAI_API_KEY
    ) if OPENAI_API_KEY else None
    if client:
        print("OpenAI client initialized successfully")
except Exception as e:
    print(f"Warning: OpenAI client initialization failed: {e}")
    client = None

# query vehicle_counts from a specified interval
def get_counts(start: datetime, end: datetime):
    sql = """
      SELECT camera_id,
             COUNT(*)    AS events,
             AVG(count)  AS avg_per_min
      FROM vehicle_counts
      WHERE timestamp >= %s
        AND timestamp <  %s
      GROUP BY camera_id
      ORDER BY events DESC;
    """
    conn = psycopg2.connect(
        host = DB_HOST,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
    )
    with conn, conn.cursor() as cur:
        cur.execute(sql, (start, end))
        return cur.fetchall()

# Cameras are sampled in a round-robin (only some run at any moment), so a
# camera is observed for only part of the window. `events` from get_counts is
# the number of minutes actually OBSERVED, and `avg_per_min` is the crossing
# rate DURING those observed minutes. We extrapolate the rate across the full
# window here, deterministically, rather than asking the LLM to do arithmetic
# (gpt-4.1-nano is unreliable at math and non-deterministic at temp>0).
def compute_camera_estimates(stats, start: datetime, end: datetime):
    """
    Turn raw (camera_id, observed_minutes, avg_per_min) rows into estimates.

    Returns a list of dicts with observed minutes, the observed rate, and an
    extrapolated full-window total, sorted busiest-first by rate.
    """
    window_minutes = max(1.0, (end - start).total_seconds() / 60.0)
    rows = []
    for cam_id, observed_minutes, avg_per_min in stats:
        rate = float(avg_per_min or 0.0)
        rows.append({
            "camera_id": cam_id,
            "observed_minutes": int(observed_minutes or 0),
            "rate_per_min": rate,
            "estimated_total": int(round(rate * window_minutes)),
        })
    rows.sort(key=lambda r: r["rate_per_min"], reverse=True)
    return rows, window_minutes


# builds the user prompt
def build_summary_prompt(stats, start: datetime, end: datetime) -> str:
    estimates, window_minutes = compute_camera_estimates(stats, start, end)
    header = (
        f"Traffic summary from {start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M} "
        f"(~{int(round(window_minutes))} min window).\n"
        "Cameras are sampled part of the time, so totals below are ESTIMATES "
        "extrapolated from the observed crossing rate. Present them as estimates.\n"
    )
    lines = [header]
    for e in estimates:
        lines.append(
            f"• {e['camera_id']}: ~{e['estimated_total']} vehicles estimated "
            f"({e['rate_per_min']:.1f}/min observed over {e['observed_minutes']} min)"
        )
    lines.append(
        "\nPlease provide a concise paragraph highlighting the busiest cameras "
        "and any overall trends you observe. Refer to the totals as estimates. "
        "Do not invent or recompute numbers; use the figures given. Do not use emojis."
    )
    return "\n".join(lines)

# generates a summary
def generate_summary(stats, start: datetime, end: datetime) -> str:
    if client is None:
        return generate_fallback_summary(stats, start, end)
    
    system_prompt = (
        "You are CitySage, a friendly traffic-monitoring assistant.  "
        "Your job is to explain vehicle-count data in simple, everyday language—"
        "no jargon, no long statistics tables.  "
        "Write as if you're telling a colleague over Slack what happened on the roads."
    )
    user_prompt = build_summary_prompt(stats, start, end) + """

    In a couple of sentences, describe in plain English:

    • Which intersections had the heaviest traffic  
    • Whether traffic was steady or spiky  
    • Anything surprising or worth knowing  

    Make it sound like you're giving a quick update to a city manager.
    """
    
    try:
        response = client.chat.completions.create(
            model=MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.7,
            top_p=0.9,
            max_tokens=250,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"OpenAI API error: {e}")
        
        return generate_fallback_summary(stats, start, end)

def generate_fallback_summary(stats, start: datetime, end: datetime) -> str:
    if not stats:
        return "No traffic activity detected during this period."

    estimates, _ = compute_camera_estimates(stats, start, end)
    estimated_total = sum(e["estimated_total"] for e in estimates)
    busiest = estimates[0] if estimates else None

    period_desc = f"{start:%H:%M} to {end:%H:%M}"
    if start.date() != end.date():
        period_desc = f"{start:%m/%d %H:%M} to {end:%m/%d %H:%M}"

    summary = (
        f"Traffic summary for {period_desc}: ~{estimated_total} vehicle crossings "
        f"estimated (extrapolated from sampled observations). "
    )

    if busiest and len(estimates) > 1:
        summary += (
            f"Busiest location was {busiest['camera_id']} at ~{busiest['rate_per_min']:.1f}/min "
            f"(~{busiest['estimated_total']} estimated). "
            f"Activity recorded at {len(estimates)} camera locations."
        )
    elif busiest:
        summary += f"All activity at {busiest['camera_id']}."

    return summary

if __name__ == "__main__":
    end   = datetime.now()
    start = end - timedelta(hours=1)
    stats = get_counts(start, end)
    print(generate_summary(stats, start, end))
