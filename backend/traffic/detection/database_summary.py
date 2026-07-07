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
DB_PORT = os.getenv("DB_PORT")

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
        port = DB_PORT,
    )
    with conn, conn.cursor() as cur:
        cur.execute(sql, (start, end))
        return cur.fetchall()


# Per-hour totals across the window, so summaries can describe how traffic
# changes through the day (rush-hour peaks, overnight lulls) instead of
# assuming a single flat rate.
def get_hourly_counts(start: datetime, end: datetime, camera_id: str = None):
    sql = """
      SELECT date_trunc('hour', timestamp) AS hour,
             SUM(count) AS crossings
      FROM vehicle_counts
      WHERE timestamp >= %s
        AND timestamp <  %s
        {cam_filter}
      GROUP BY hour
      ORDER BY hour;
    """.format(cam_filter="AND camera_id = %s" if camera_id else "")
    params = (start, end, camera_id) if camera_id else (start, end)
    conn = psycopg2.connect(
        host = DB_HOST,
        dbname = DB_NAME,
        user = DB_USER,
        password = DB_PASSWORD,
        port = DB_PORT,
    )
    with conn, conn.cursor() as cur:
        cur.execute(sql, params)
        return cur.fetchall()

# Cameras are sampled in a round-robin, so `events` from get_counts is the
# number of minutes actually OBSERVED and `avg_per_min` is the crossing rate
# during those minutes. We report OBSERVED actuals (rate x observed minutes) —
# no projecting to the full window — so the summary never overstates precision.
def compute_camera_stats(stats):
    """
    Turn raw (camera_id, observed_minutes, avg_per_min) rows into observed
    per-camera figures, sorted busiest-first by rate. No extrapolation.
    """
    rows = []
    for cam_id, observed_minutes, avg_per_min in stats:
        rate = float(avg_per_min or 0.0)
        obs = int(observed_minutes or 0)
        rows.append({
            "camera_id": cam_id,
            "observed_minutes": obs,
            "rate_per_min": rate,
            "observed_crossings": int(round(rate * obs)),
        })
    rows.sort(key=lambda r: r["rate_per_min"], reverse=True)
    return rows


# builds the user prompt
def build_summary_prompt(stats, start: datetime, end: datetime, hourly=None) -> str:
    cams = compute_camera_stats(stats)
    header = (
        f"Traffic report from {start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M}.\n"
        "Figures are observed vehicle crossings from live camera detection.\n"
    )
    lines = [header, "Per camera (busiest first):"]
    for c in cams:
        lines.append(
            f"• {c['camera_id']}: {c['observed_crossings']} crossings "
            f"({c['rate_per_min']:.1f}/min over {c['observed_minutes']} min observed)"
        )

    # Hourly shape: lets the model describe how traffic changed through the
    # day instead of assuming one flat rate across the whole window.
    if hourly:
        lines.append("\nCrossings by hour (shows how traffic varied over time):")
        for hour, crossings in hourly:
            lines.append(f"• {hour:%a %H:%M}: {int(crossings or 0)} crossings")

    lines.append(
        "\nWrite a concise paragraph on the busiest cameras and how traffic "
        "changed over time (e.g. rush-hour peaks vs quieter periods). Traffic "
        "volume varies throughout the day, so describe the pattern across the "
        "hours shown rather than assuming a constant rate. Use only the numbers "
        "given; do not invent or recompute figures. Do not describe the numbers "
        "as estimates. Do not use emojis."
    )
    return "\n".join(lines)

# generates a summary
def generate_summary(stats, start: datetime, end: datetime, hourly=None) -> str:
    if client is None:
        return generate_fallback_summary(stats, start, end, hourly)

    system_prompt = (
        "You are CitySage, a friendly traffic-monitoring assistant.  "
        "Your job is to explain vehicle-count data in simple, everyday language—"
        "no jargon, no long statistics tables.  "
        "Write as if you're telling a colleague over Slack what happened on the roads. "
        "Traffic volume changes throughout the day, so describe how it rose and fell "
        "across the hours shown. Report the counts as observed facts, never as estimates."
    )
    user_prompt = build_summary_prompt(stats, start, end, hourly) + """

    In a couple of sentences, describe in plain English:

    • Which intersections had the heaviest traffic
    • How traffic changed over the day — when it peaked and when it was quiet
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

        return generate_fallback_summary(stats, start, end, hourly)

def generate_fallback_summary(stats, start: datetime, end: datetime, hourly=None) -> str:
    if not stats:
        return "No traffic activity detected during this period."

    cams = compute_camera_stats(stats)
    total = sum(c["observed_crossings"] for c in cams)
    busiest = cams[0] if cams else None

    period_desc = f"{start:%H:%M} to {end:%H:%M}"
    if start.date() != end.date():
        period_desc = f"{start:%m/%d %H:%M} to {end:%m/%d %H:%M}"

    summary = f"Traffic report for {period_desc}: {total} vehicle crossings observed. "

    if busiest and len(cams) > 1:
        summary += (
            f"Busiest location was {busiest['camera_id']} at {busiest['rate_per_min']:.1f}/min "
            f"({busiest['observed_crossings']} crossings). "
            f"Activity recorded at {len(cams)} camera locations. "
        )
    elif busiest:
        summary += f"All activity at {busiest['camera_id']}. "

    # Describe the daily pattern from the hourly data (peak vs quiet hour).
    if hourly:
        valid = [(h, int(c or 0)) for h, c in hourly]
        if valid:
            peak = max(valid, key=lambda x: x[1])
            quiet = min(valid, key=lambda x: x[1])
            summary += (
                f"Traffic peaked around {peak[0]:%H:%M} ({peak[1]} crossings) "
                f"and was quietest around {quiet[0]:%H:%M} ({quiet[1]} crossings)."
            )

    return summary

if __name__ == "__main__":
    end   = datetime.now()
    start = end - timedelta(hours=1)
    stats = get_counts(start, end)
    hourly = get_hourly_counts(start, end)
    print(generate_summary(stats, start, end, hourly))
