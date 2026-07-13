import os
import psycopg2
from flask import Flask

app = Flask(__name__)

def get_db_connection():
    return psycopg2.connect(
        host=os.environ.get("DB_HOST"),
        database=os.environ.get("DB_NAME", "postgres"),
        user=os.environ.get("DB_USER"),
        password=os.environ.get("DB_PASSWORD"),
        port=os.environ.get("DB_PORT", "5432"),
    )

@app.route("/")
def index():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE visitor_counter
        SET count = count + 1
        WHERE id = 1
        RETURNING count;
    """)
    count = cur.fetchone()[0]

    conn.commit()
    cur.close()
    conn.close()

    return f"Hello world! Visitor count: {count}"

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
