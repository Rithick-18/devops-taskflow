from flask import Flask, jsonify, request
import psycopg2

app = Flask(__name__)


def get_db_connection():
    return psycopg2.connect(
        host="localhost",
        database="taskflow",
        user="taskflow_user",
        password="Taskflow@123"
    )


@app.route("/")
def home():
    return jsonify({
        "message": "DevOps TaskFlow Backend is running"
    })


@app.route("/api/health")
def health():
    return jsonify({
        "status": "healthy"
    })


@app.route("/api/tasks", methods=["GET"])
def get_tasks():
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, title, status, created_at
        FROM tasks
        ORDER BY id;
    """)

    rows = cur.fetchall()

    tasks = []

    for row in rows:
        tasks.append({
            "id": row[0],
            "title": row[1],
            "status": row[2],
            "created_at": row[3].isoformat()
        })

    cur.close()
    conn.close()

    return jsonify(tasks)


@app.route("/api/tasks", methods=["POST"])
def create_task():
    data = request.get_json()

    title = data.get("title")

    if not title:
        return jsonify({
            "error": "Task title is required"
        }), 400

    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO tasks (title)
        VALUES (%s)
        RETURNING id, title, status, created_at;
        """,
        (title,)
    )

    row = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    return jsonify({
        "id": row[0],
        "title": row[1],
        "status": row[2],
        "created_at": row[3].isoformat()
    }), 201


@app.route("/api/tasks/<int:task_id>", methods=["DELETE"])
def delete_task(task_id):
    conn = get_db_connection()
    cur = conn.cursor()

    cur.execute(
        "DELETE FROM tasks WHERE id = %s RETURNING id;",
        (task_id,)
    )

    deleted = cur.fetchone()

    conn.commit()

    cur.close()
    conn.close()

    if not deleted:
        return jsonify({
            "error": "Task not found"
        }), 404

    return jsonify({
        "message": "Task deleted successfully"
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
