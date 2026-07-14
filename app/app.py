import os
import psycopg2
from flask import Flask, request, make_response

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
    already_visited = request.cookies.get("visited")

    conn = get_db_connection()
    cur = conn.cursor()

    if already_visited:
        # Returning visitor: bump total count only
        cur.execute("""
            UPDATE visitor_counter
            SET count = count + 1
            WHERE id = 1
            RETURNING count, unique_count;
        """)
    else:
        # New visitor: bump both total and unique counts
        cur.execute("""
            UPDATE visitor_counter
            SET count = count + 1, unique_count = unique_count + 1
            WHERE id = 1
            RETURNING count, unique_count;
        """)

    count, unique_count = cur.fetchone()
    conn.commit()
    cur.close()
    conn.close()

    html = f"""
    <html>
        <body style="font-family: sans-serif; text-align: center; margin-top: 100px;">
            <h1>Hello world!</h1>
            <h2>Total visits: {count}</h2>
            <h3>Unique visitors: {unique_count}</h3>
        </body>
    </html>
    """

    resp = make_response(html)
    if not already_visited:
        resp.set_cookie("visited", "true", max_age=60 * 60 * 24 * 365)  # 1 year
    return resp

@app.route("/health")
def health():
    return "OK", 200

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=80)
