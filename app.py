from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)
DATA_PATH = "data/skip_data.csv"
ANNOUNCE_PATH = "data/announcements.csv"

NAMES = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

def read_data():
    if os.path.exists(DATA_PATH):
        return pd.read_csv(DATA_PATH)
    else:
        return pd.DataFrame(columns=["name", "date", "breakfast", "dinner"])

def read_announcements():
    if os.path.exists(ANNOUNCE_PATH):
        return pd.read_csv(ANNOUNCE_PATH)
    else:
        return pd.DataFrame(columns=["writer", "message", "date"])

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        name = request.form.get("name")
        date = request.form.get("date")
        breakfast = "breakfast" in request.form
        dinner = "dinner" in request.form

        if not name or not date or (not breakfast and not dinner):
            return "情報が足りません"

        df = read_data()
        new_row = {"name": name, "date": date, "breakfast": breakfast, "dinner": dinner}
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
        df.to_csv(DATA_PATH, index=False)
        return redirect("/list")

    announcements = read_announcements()
    today = datetime.today().strftime('%Y-%m-%d')
    announcements = announcements[announcements["date"] >= today]
    return render_template("form.html", names=NAMES, announcements=announcements.to_dict(orient="records"))

@app.route("/list")
def list_today():
    today = datetime.today().strftime('%Y-%m-%d')
    df = read_data()
    df_today = df[df["date"] == today]
    return render_template("list.html", records=df_today.to_dict(orient="records"))

@app.route("/past")
def past():
    today = datetime.today().strftime('%Y-%m-%d')
    df = read_data()
    df_past = df[df["date"] < today].sort_values(by="date", ascending=False)
    return render_template("past.html", records=df_past.to_dict(orient="records"))

@app.route("/future")
def future():
    today = datetime.today().strftime('%Y-%m-%d')
    df = read_data()
    df_future = df[df["date"] > today].sort_values(by="date", ascending=True)
    return render_template("future.html", records=df_future.to_dict(orient="records"))

@app.route("/announcement", methods=["POST"])
def announcement():
    writer = request.form.get("writer", "")
    message = request.form.get("message", "")
    date = datetime.today().strftime('%Y-%m-%d')
    if not message:
        return redirect("/")

    df = read_announcements()
    new_row = {"writer": writer, "message": message, "date": date}
    df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.to_csv(ANNOUNCE_PATH, index=False)
    return redirect("/")

@app.route("/delete", methods=["POST"])
def delete():
    name = request.form.get("name")
    date = request.form.get("date")

    df = read_data()
    df = df[~((df["name"] == name) & (df["date"] == date))]
    df.to_csv(DATA_PATH, index=False)
    return redirect("/future")
