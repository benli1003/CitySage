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

# GitHub Models configuration
GITHUB_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
GITHUB_TOKEN = os.getenv("OPENAI_KEY")
MODEL = "gpt-4o"

try:
    client = OpenAI(
        base_url = GITHUB_ENDPOINT,
        api_key = GITHUB_TOKEN
    )
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

# builds the user prompt
def build_summary_prompt(stats, start: datetime, end: datetime) -> str:
    header = f"Traffic summary from {start:%Y-%m-%d %H:%M} to {end:%Y-%m-%d %H:%M}:\n"
    lines = [header]
    for cam_id, total, avg in stats:
        lines.append(f"• {cam_id}: {total} total crossings, avg {avg:.1f}/min")
    lines.append(
        "\nPlease provide a concise paragraph highlighting the busiest cameras "
        "and any overall trends you observe. Do not use emojis."
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
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        print(f"AI service error: {e}")
        return generate_fallback_summary(stats, start, end)

def generate_fallback_summary(stats, start: datetime, end: datetime) -> str:
    if not stats:
        return "No traffic activity detected during this period."
    
    total_events = sum(events for _, events, _ in stats)
    busiest_camera = stats[0][0] if stats else "Unknown"
    busiest_count = stats[0][1] if stats else 0
    
    period_desc = f"{start:%H:%M} to {end:%H:%M}"
    if start.date() != end.date():
        period_desc = f"{start:%m/%d %H:%M} to {end:%m/%d %H:%M}"
    
    summary = f"Traffic summary for {period_desc}: {total_events} total vehicle crossings detected. "
    
    if len(stats) > 1:
        summary += f"Busiest location was {busiest_camera} with {busiest_count} crossings. "
        summary += f"Activity recorded at {len(stats)} camera locations."
    else:
        summary += f"All activity at {busiest_camera}."
    
    return summary

if __name__ == "__main__":
    end   = datetime.now()
    start = end - timedelta(hours=1)
    stats = get_counts(start, end)
    print(generate_summary(stats, start, end))
