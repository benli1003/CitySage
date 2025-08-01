import os
import psycopg2
from datetime import datetime, timedelta
from dotenv import load_dotenv
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import SystemMessage, UserMessage
from azure.core.credentials import AzureKeyCredential

load_dotenv()

# database
DB_HOST = os.getenv("DB_HOST")
DB_NAME = os.getenv("DB_NAME")
DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")

# open ai client
OPENAI_ENDPOINT = os.getenv("OPENAI_ENDPOINT")
OPENAI_KEY = os.getenv("OPENAI_KEY")
MODEL = "openai/gpt-4.1"

client = ChatCompletionsClient(
    endpoint = OPENAI_ENDPOINT,
    credential = AzureKeyCredential(OPENAI_KEY),
)

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
        "and any overall trends you observe."
    )
    return "\n".join(lines)

# generates a summary
def generate_summary(stats, start: datetime, end: datetime) -> str:
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
    
    response = client.complete(
        model = MODEL,
        messages = [
            SystemMessage(content = system_prompt),
            UserMessage(content = user_prompt),
        ],
        temperature = 0.7,
        top_p =0.9,
    )
    return response.choices[0].message.content.strip()

if __name__ == "__main__":
    end   = datetime.now()
    start = end - timedelta(hours=1)
    stats = get_counts(start, end)
    print(generate_summary(stats, start, end))
