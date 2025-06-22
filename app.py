from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

DATA_PATH = "data/skip_data.csv"
ANNOUNCEMENT_PATH = "data/notice.csv"
ALL_NAMES = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

@app.route("/")
def index():
    today = datetime.today().strftime('%Y-%m-%d')
    df = load_data()
    today_records = df[df['date'] == today].to_dict(orient='records')
    notices = load_notice().to_dict(orient='records')
    return render_template("form.html", names=ALL_NAMES, date=today, records=today_records, notices=notices)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    date = request.form.get("date")
    meals = request.form.getlist("meal")
    df = load_data()

    for meal in meals:
        df.loc[len(df)] = [name, date, meal]
    save_csv(df, DATA_PATH)

    notice_text = request.form.get("notice")
    notice_author = request.form.get("notice_author")
    if notice_text:
        notices = load_notice()
        notices.loc[len(notices)] = [notice_author, notice_text, date]
        save_csv(notices, ANNOUNCEMENT_PATH)

    return redirect(url_for("index"))

@app.route("/list")
def list_today():
    today = datetime.today().strftime('%Y-%m-%d')
    df = load_data()
    today_records = df[df['date'] == today].to_dict(orient='records')
    return render_template("list.html", date=today, records=today_records)

@app.route("/future")
def future():
    today = datetime.today().strftime('%Y-%m-%d')
    df = load_data()
    future_records = df[df['date'] > today].sort_values(by="date").to_dict(orient='records')
    return render_template("future.html", records=future_records)

@app.route("/past")
def past():
    today = datetime.today().strftime('%Y-%m-%d')
    df = load_data()
    past_records = df[df['date'] < today].sort_values(by="date", ascending=False).to_dict(orient='records')
    return render_template("past.html", records=past_records)

@app.route("/announcement")
def announcement():
    notices = load_notice().to_dict(orient='records')
    return render_template("announcement.html", notices=notices)

@app.route("/delete_meal/<int:index>", methods=["POST"])
def delete_meal(index):
    df = load_data()
    if index < len(df):
        df = df.drop(index).reset_index(drop=True)
        save_csv(df, DATA_PATH)
    return redirect(request.referrer or url_for("index"))

# ===== 共通関数 =====
def load_data():
    if not os.path.exists(DATA_PATH):
        return pd.DataFrame(columns=["name", "date", "meal"])
    return pd.read_csv(DATA_PATH)

def load_notice():
    if not os.path.exists(ANNOUNCEMENT_PATH):
        return pd.DataFrame(columns=["author", "notice", "date"])
    return pd.read_csv(ANNOUNCEMENT_PATH)

def save_csv(df, path):
    with open(path, 'w') as f:
        df.to_csv(f, index=False)
        f.flush()
        os.fsync(f.fileno())

if __name__ == '__main__':
    app.run(debug=True)
