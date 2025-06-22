from flask import Flask, render_template, request, redirect, send_file
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

DATA_PATH = "data/skip_data.csv"
ANNOUNCE_PATH = "data/announce.csv"

NAMES = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

@app.route("/")
def index():
    df_announce = pd.read_csv(ANNOUNCE_PATH) if os.path.exists(ANNOUNCE_PATH) else pd.DataFrame(columns=["name", "content", "start_date"])
    return render_template("form.html", names=NAMES, announcements=df_announce.to_dict(orient="records"))

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    date = request.form.get("date")
    morning = "morning" in request.form
    night = "night" in request.form

    if not name or not date:
        return "情報が足りません"

    df = pd.read_csv(DATA_PATH) if os.path.exists(DATA_PATH) else pd.DataFrame(columns=["name", "date", "morning", "night"])
    df = df[~((df["name"] == name) & (df["date"] == date))]  # 重複削除
    df.loc[len(df)] = [name, date, morning, night]
    df.to_csv(DATA_PATH, index=False)
    return redirect("/list")

@app.route("/list")
def today_list():
    today = datetime.today().strftime('%Y-%m-%d')
    df = pd.read_csv(DATA_PATH)
    df_today = df[df["date"] == today]
    return render_template("list.html", records=df_today.to_dict(orient="records"), date_label="本日の欠食者")

@app.route("/past")
def past():
    today = datetime.today().strftime('%Y-%m-%d')
    df = pd.read_csv(DATA_PATH)
    df_past = df[df["date"] < today].sort_values(by="date", ascending=False)
    return render_template("past.html", records=df_past.to_dict(orient="records"))

@app.route("/future")
def future():
    today = datetime.today().strftime('%Y-%m-%d')
    df = pd.read_csv(DATA_PATH)
    df_future = df[df["date"] > today].sort_values(by="date")
    return render_template("future.html", records=df_future.to_dict(orient="records"))

@app.route("/delete", methods=["POST"])
def delete():
    name = request.form.get("name")
    date = request.form.get("date")
    df = pd.read_csv(DATA_PATH)
    df = df[~((df["name"] == name) & (df["date"] == date))]
    df.to_csv(DATA_PATH, index=False)
    return redirect("/future")

@app.route("/announcement", methods=["GET", "POST"])
def announcement():
    if request.method == "POST":
        name = request.form.get("name") or "匿名"
        content = request.form.get("content")
        if content:
            df = pd.read_csv(ANNOUNCE_PATH) if os.path.exists(ANNOUNCE_PATH) else pd.DataFrame(columns=["name", "content", "start_date"])
            df.loc[len(df)] = [name, content, datetime.today().strftime('%Y-%m-%d')]
            df.to_csv(ANNOUNCE_PATH, index=False)
        return redirect("/")
    return render_template("announcement.html")

@app.route("/download")
def download():
    return send_file(DATA_PATH, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
