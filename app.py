# app.py
from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
import os
from datetime import datetime

app = Flask(__name__)

# ファイル名
SKIP_FILE = "skip_meals.csv"
NOTICE_FILE = "notices.csv"
ANNOUNCEMENT_FILE = "announcements.csv"

# 名前のリスト
NAME_LIST = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

# 初期化関数
def init_csv(file, columns):
    if not os.path.exists(file):
        pd.DataFrame(columns=columns).to_csv(file, index=False)

init_csv(SKIP_FILE, ["名前", "日付", "朝", "夜"])
init_csv(NOTICE_FILE, ["名前", "内容", "投稿時刻"])
init_csv(ANNOUNCEMENT_FILE, ["名前", "内容", "開始日", "終了日"])

# CSV読み書き関数
def load_csv(file, columns):
    if not os.path.exists(file):
        return pd.DataFrame(columns=columns)
    return pd.read_csv(file)

def save_csv(df, file):
    df.to_csv(file, index=False)

@app.route("/")
def index():
    skips = load_csv(SKIP_FILE, ["名前", "日付", "朝", "夜"])
    notices = load_csv(NOTICE_FILE, ["名前", "内容", "投稿時刻"])
    announcements = load_csv(ANNOUNCEMENT_FILE, ["名前", "内容", "開始日", "終了日"])
    return render_template("form.html", names=NAME_LIST, skips=skips, notices=notices, announcements=announcements)

@app.route("/submit", methods=["POST"])
def submit():
    name = request.form.get("name")
    date = request.form.get("date")
    morning = "朝" if request.form.get("morning") else ""
    night = "夜" if request.form.get("night") else ""
    if not (name and date):
        return "情報が足りません", 400
    df = load_csv(SKIP_FILE, ["名前", "日付", "朝", "夜"])
    df.loc[len(df)] = [name, date, morning, night]
    save_csv(df, SKIP_FILE)
    return redirect("/")

@app.route("/announcement", methods=["GET", "POST"])
def announcement():
    if request.method == "POST":
        writer = request.form.get("writer")
        content = request.form.get("content")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")
        if content:
            df = load_csv(ANNOUNCEMENT_FILE, ["名前", "内容", "開始日", "終了日"])
            df.loc[len(df)] = [writer or "匿名", content, start_date, end_date]
            save_csv(df, ANNOUNCEMENT_FILE)
        return redirect("/")
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    index = int(request.form.get("index", -1))
    df = load_csv(SKIP_FILE, ["名前", "日付", "朝", "夜"])
    if 0 <= index < len(df):
        df = df.drop(index).reset_index(drop=True)
        save_csv(df, SKIP_FILE)
    return redirect("/")

@app.route("/delete_announcement", methods=["POST"])
def delete_announcement():
    index = int(request.form.get("index", -1))
    df = load_csv(ANNOUNCEMENT_FILE, ["名前", "内容", "開始日", "終了日"])
    if 0 <= index < len(df):
        df = df.drop(index).reset_index(drop=True)
        save_csv(df, ANNOUNCEMENT_FILE)
    return redirect("/")

if __name__ == "__main__":
    app.run(debug=True)
