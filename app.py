from flask import Flask, render_template, request, redirect, url_for
from datetime import datetime, timedelta
import os
import csv

app = Flask(__name__)

# 欠食記録とお知らせの保存先
SKIP_FILE = "skip_meals.csv"
ANNOUNCE_FILE = "announcements.csv"

# メンバーリスト
MEMBER_LIST = [
    "徳本監督", "岡田コーチ",
    "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

@app.route("/", methods=["GET", "POST"])
def index():
    today = datetime.now().date()
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        morning = "morning" in request.form
        night = "night" in request.form
        announce_writer = request.form.get("announce_writer")
        announce_content = request.form.get("announce_content")
        announce_start = request.form.get("announce_start")
        announce_end = request.form.get("announce_end")

        # 欠食データ保存
        if name and date and (morning or night):
            with open(SKIP_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([name, date, morning, night])

        # お知らせ保存
        if announce_writer and announce_content and announce_start and announce_end:
            with open(ANNOUNCE_FILE, "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([announce_writer, announce_content, announce_start, announce_end])

        return redirect(url_for("index"))

    # 有効なお知らせ表示（終了日が今日以降）
    announcements = []
    if os.path.exists(ANNOUNCE_FILE):
        with open(ANNOUNCE_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4:
                    start, end = row[2], row[3]
                    if start <= str(today) <= end:
                        announcements.append(row)

    return render_template("form.html", members=MEMBER_LIST, announcements=announcements)

@app.route("/today")
def today():
    today = datetime.now().date()
    skips = []
    if os.path.exists(SKIP_FILE):
        with open(SKIP_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and row[1] == str(today):
                    skips.append(row)
    return render_template("today.html", skips=skips)

@app.route("/future")
def future():
    today = datetime.now().date()
    skips = []
    if os.path.exists(SKIP_FILE):
        with open(SKIP_FILE, newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            for row in reader:
                if len(row) >= 4 and datetime.strptime(row[1], "%Y-%m-%d").date() > today:
                    skips.append(row)
    return render_template("future.html", skips=skips)

@app.route("/delete", methods=["POST"])
def delete():
    name = request.form.get("name")
    date = request.form.get("date")
    if not (name and date):
        return "データが足りません", 400
    new_rows = []
    with open(SKIP_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        new_rows = [row for row in reader if not (row[0] == name and row[1] == date)]
    with open(SKIP_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_rows)
    return redirect(url_for("index"))

@app.route("/delete_announcement", methods=["POST"])
def delete_announcement():
    writer = request.form.get("announce_writer")
    content = request.form.get("announce_content")
    if not (writer and content):
        return "情報が足りません", 400
    new_announcements = []
    with open(ANNOUNCE_FILE, newline="", encoding="utf-8") as f:
        reader = csv.reader(f)
        for row in reader:
            if row[0] != writer or row[1] != content:
                new_announcements.append(row)
    with open(ANNOUNCE_FILE, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerows(new_announcements)
    return redirect(url_for("index"))

if __name__ == '__main__':
    app.run(debug=True, port=int(os.environ.get("PORT", 5000)))
