from flask import Flask, request, jsonify
import psycopg
import os

app = Flask(__name__)

# Получаем URL базы данных из переменной окружения Render (DATABASE_URL)
DATABASE_URL = os.environ.get("DATABASE_URL")

# Подключаемся к базе данных
conn = None
if DATABASE_URL:
    try:
        conn = psycopg.connect(DATABASE_URL)
        with conn.cursor() as cur:
            cur.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id SERIAL PRIMARY KEY,
                    content TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT NOW()
                )
            """)
            conn.commit()
        print("✅ Database connected and table ready.")
    except Exception as e:
        print("❌ DB connection error:", e)
else:
    print("⚠️ DATABASE_URL not set, running without DB.")


@app.route("/")
def index():
    return "🚀 Flask + Render + PostgreSQL works!"


@app.route("/save", methods=["POST"])
def save_message():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    data = request.get_json(silent=True)
    message = (data or {}).get("message", "")

    with conn.cursor() as cur:
        cur.execute("INSERT INTO messages (content) VALUES (%s)", (message,))
        conn.commit()

    return jsonify({"status": "saved", "message": message})


@app.route("/messages")
def get_messages():
    if not conn:
        return jsonify({"error": "DB not connected"}), 500

    with conn.cursor() as cur:
        cur.execute("SELECT id, content, created_at FROM messages ORDER BY id DESC LIMIT 10")
        rows = cur.fetchall()

    messages = [{"id": r[0], "text": r[1], "time": r[2].isoformat()} for r in rows]
    return jsonify(messages)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)