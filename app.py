from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import sqlite3
import calendar

app = Flask(__name__)

def init_db():
    conn = sqlite3.connect('weekly_schedule.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS schedule
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, 
                 class_name TEXT, 
                 year INTEGER,
                 month INTEGER,
                 week INTEGER,
                 day_of_week TEXT,
                 date TEXT,
                 homework TEXT,
                 items TEXT)''')
    conn.commit()
    conn.close()

def calculate_week_dates(year, month, week):
    first_day = datetime(year, month, 1)
    first_weekday = first_day.weekday()
    
    # 주차 시작일 계산 (월요일 기준)
    if first_weekday <= 3:  # 목요일 포함 이전은 1주차 시작
        start_date = first_day - timedelta(days=first_weekday)
    else:
        start_date = first_day + timedelta(days=(7 - first_weekday))
    
    start_date += timedelta(weeks=week - 1)

    dates = []
    for i in range(5):  # 월~금
        day = start_date + timedelta(days=i)
        dates.append(day)
    return dates

@app.route('/')
def index():
    return redirect(url_for('teacher_write'))

@app.route('/teacher_write', methods=['GET', 'POST'])
def teacher_write():
    if request.method == 'POST':
        class_name = request.form['class_name']
        year = int(request.form['year'])
        month = int(request.form['month'])
        week = int(request.form['week'])

        for i in range(5):
            day_of_week = ['월', '화', '수', '목', '금'][i]
            date = request.form.get(f'date_{i}')
            homework = request.form.get(f'homework_{i}')
            items = request.form.get(f'items_{i}')

            conn = sqlite3.connect('weekly_schedule.db')
            c = conn.cursor()
            c.execute("INSERT INTO schedule (class_name, year, month, week, day_of_week, date, homework, items) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                      (class_name, year, month, week, day_of_week, date, homework, items))
            conn.commit()
            conn.close()
        
        return redirect(url_for('teacher_write'))

    # GET 요청 처리
    today = datetime.today()
    year = today.year
    month = today.month

    # 주차 구하기 (최대 5주차까지 가정)
    weeks = list(range(1, 6))

    selected_week = request.args.get('week')
    selected_dates = []

    if selected_week:
        selected_week = int(selected_week)
        selected_dates = calculate_week_dates(year, month, selected_week)

    return render_template('teacher_write_table.html', year=year, month=month, weeks=weeks, selected_week=selected_week, selected_dates=selected_dates)

if __name__ == '__main__':
    init_db()
    app.run(host='0.0.0.0')
