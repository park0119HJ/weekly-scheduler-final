
from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = "your_secret_key"

DB_NAME = "weekly_schedule.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS schedules (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            class_name TEXT,
            week TEXT,
            day TEXT,
            date TEXT,
            homework TEXT,
            material TEXT,
            published INTEGER DEFAULT 0
        )
    """)
    conn.commit()
    conn.close()

init_db()

teachers = {
    "teacher_isak": {"password": "1234", "class_name": "이삭반"},
    "teacher_yoel": {"password": "1234", "class_name": "요엘반"},
    "teacher_joseph": {"password": "1234", "class_name": "요셉반"},
    "teacher_daniel": {"password": "1234", "class_name": "다니엘반"},
    "teacher_joshua": {"password": "1234", "class_name": "여호수아반"},
}

class_codes = {
    "이삭반": "isak2024",
    "요엘반": "yoel2024",
    "요셉반": "joseph2024",
    "다니엘반": "daniel2024",
    "여호수아반": "joshua2024",
}

def get_weeks():
    today = datetime.today()
    weeks = []
    for i in range(-2, 5):
        monday = (today + timedelta(weeks=i)).replace(day=1)
        monday += timedelta(days=(7 - monday.weekday()) % 7)
        weeks.append(monday.strftime("%Y-%m-%d"))
    return weeks

@app.route("/")
def home():
    return "접속 성공! /teacher/login 또는 /parent/이삭반 으로 접속하세요."

@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        user = teachers.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["class_name"] = user["class_name"]
            return redirect(url_for("teacher_write", class_name=user["class_name"]))
        else:
            return "로그인 실패"
    return render_template("teacher_login.html")

@app.route("/teacher/logout")
def logout():
    session.clear()
    return redirect(url_for("teacher_login"))

@app.route("/teacher/<class_name>", methods=["GET", "POST"])
def teacher_write(class_name):
    if "username" not in session or session["class_name"] != class_name:
        return redirect(url_for("teacher_login"))

    weeks = get_weeks()
    selected_week = request.args.get("week", weeks[0])

    if request.method == "POST":
        selected_week = request.form["week"]
        action = request.form["action"]
        conn = sqlite3.connect(DB_NAME)
        c = conn.cursor()
        for i, day in enumerate(["월", "화", "수", "목", "금"]):
            homework = request.form.get(f"homework_{i}", "")
            material = request.form.get(f"material_{i}", "")
            date = (datetime.strptime(selected_week, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d")
            c.execute("INSERT INTO schedules (class_name, week, day, date, homework, material, published) VALUES (?, ?, ?, ?, ?, ?, ?)",
                      (class_name, selected_week, day, date, homework, material, 1 if action == "publish" else 0))
        conn.commit()
        conn.close()
        return redirect(url_for("teacher_write", class_name=class_name, week=selected_week))

    dates = [(datetime.strptime(selected_week, "%Y-%m-%d") + timedelta(days=i)).strftime("%Y-%m-%d") for i in range(5)]
    return render_template("teacher_write_table.html", weeks=weeks, selected_week=selected_week, dates=dates)

@app.route("/parent/<class_name>", methods=["GET"])
def parent(class_name):
    if session.get(f"parent_access_{class_name}") != True:
        if request.args.get("code"):
            if request.args.get("code") == class_codes.get(class_name):
                session[f"parent_access_{class_name}"] = True
                return redirect(url_for("parent", class_name=class_name))
            else:
                return "학급코드가 틀렸습니다"
        return render_template("parent_code.html", class_name=class_name)

    weeks = get_weeks()
    selected_week = request.args.get("week", weeks[0])
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT day, date, homework, material FROM schedules WHERE class_name = ? AND week = ? AND published = 1 ORDER BY id",
              (class_name, selected_week))
    data = c.fetchall()
    conn.close()
    return render_template("parent_page.html", class_name=class_name, weeks=weeks, selected_week=selected_week, schedule_data=data)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
