
from flask import Flask, render_template, request, redirect, session, url_for
import os
import sqlite3
from datetime import datetime

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
            week_start_date TEXT,
            day TEXT,
            content TEXT,
            last_update TEXT
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

@app.route("/")
def home():
    return "접속 성공! /teacher/login 또는 /parent/반이름 으로 이동하세요."

@app.route("/teacher/login", methods=["GET", "POST"])
def teacher_login():
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]

        user = teachers.get(username)
        if user and user["password"] == password:
            session["username"] = username
            session["class_name"] = user["class_name"]
            return redirect(url_for("teacher", class_name=user["class_name"]))
        else:
            return "로그인 실패"

    return render_template("teacher_login.html")

@app.route("/teacher/logout")
def logout():
    session.clear()
    return redirect(url_for("teacher_login"))

@app.route("/teacher/<class_name>", methods=["GET", "POST"])
def teacher(class_name):
    if "username" not in session or session["class_name"] != class_name:
        return redirect(url_for("teacher_login"))

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()

    if request.method == "POST":
        week_start_date = request.form["week_start_date"]
        for day in ["월", "화", "수", "목", "금"]:
            content = request.form.get(day, "")
            c.execute("INSERT INTO schedules (class_name, week_start_date, day, content, last_update) VALUES (?, ?, ?, ?, ?)", 
                      (class_name, week_start_date, day, content, datetime.now()))
        conn.commit()
        return redirect(f"/teacher/{class_name}")

    c.execute("SELECT week_start_date, day, content FROM schedules WHERE class_name = ? ORDER BY id DESC", (class_name,))
    schedules = c.fetchall()
    conn.close()
    return render_template("teacher_page.html", class_name=class_name, schedules=schedules)

@app.route("/parent/<class_name>", methods=["GET", "POST"])
def parent(class_name):
    if session.get(f"parent_access_{class_name}") != True:
        if request.method == "POST":
            code = request.form["class_code"]
            if code == class_codes.get(class_name):
                session[f"parent_access_{class_name}"] = True
                return redirect(url_for("parent", class_name=class_name))
            else:
                return "학급코드가 틀렸습니다"

        return render_template("parent_code.html", class_name=class_name)

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT week_start_date, day, content FROM schedules WHERE class_name = ? ORDER BY id DESC", (class_name,))
    schedules = c.fetchall()
    conn.close()
    return render_template("parent_page.html", class_name=class_name, schedules=schedules)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
