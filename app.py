from flask import Flask, render_template, request, redirect, url_for
import pandas as pd
from datetime import datetime
import os

app = Flask(__name__)

DATA_PATH = "data/skip_data.csv"
ANNOUNCEMENT_PATH = "data/announcements.csv"

if not os.path.exists(DATA_PATH):
    pd.DataFrame(columns=["name", "date", "meal"]).to_csv(DATA_PATH, index=False)

if not os.path.exists(ANNOUNCEMENT_PATH):
    pd.DataFrame(columns=["name", "message", "start_date", "end_date"]).to_csv(ANNOUNCEMENT_PATH, index=False)

ALL_NAMES = [
    "徳本監督", "岡田コーチ", "内山壽頼", "大森隼人", "菊池笙", "國井優仁", "佐竹響", "長谷川琉斗", "本田伊吹", "横尾皓",
    "石井達也", "植田航生", "宇野利希", "小坂悠太", "澤田悠斗", "塩崎浩貴", "新城陽", "丹野暁翔", "永田覇人", "米原大祐",
    "上原駿希", "太田直希", "熊井康太", "小林圭吾", "酒井忠久", "高橋柊", "中川成弥", "水戸瑛太", "宮本大心",
    "赤繁咲多", "岩瀬駿介", "大沼亮太", "奥村心", "後藤秀波", "高松桜太", "竹中友規", "森尻悠翔", "渡邊義仁"
]

@app.route('/')
def form():
    today = datetime.today().strftime('%Y-%m-%d')
    ann_df = pd.read_csv(ANNOUNCEMENT_PATH)
    ann_df = ann_df[(ann_df["start_date"] <= today) & (ann_df["end_date"] >= today)]
    return render_template("form.html", names=ALL_NAMES, announcements=ann_df.to_dict(orient="records"))

@app.route('/submit', methods=["POST"])
def submit():
    name = request.form.get("name")
    date = request.form.get("date")
    meal = request.form.getlist("meal")

    if not name or not date or not meal:
        return "情報が足りません", 400

    df = pd.read_csv(DATA_PATH)
    for m in meal:
        df = pd.concat([df, pd.DataFrame([{"name": name, "date": date, "meal": m}])], ignore_index=True)
    df.to_csv(DATA_PATH, index=False)

    return redirect(url_for('today'))

@app.route('/today')
def today():
    today = datetime.today().strftime('%Y-%m-%d')
    df = pd.read_csv(DATA_PATH)
    df_today = df[df["date"] == today]
    return render_template("list.html", records=df_today.to_dict(orient="records"), date=today)

@app.route('/future')
def future():
    today = datetime.today().strftime('%Y-%m-%d')
    df = pd.read_csv(DATA_PATH)
    df["date"] = pd.to_datetime(df["date"]).dt.strftime('%Y-%m-%d')
    df_future = df[df["date"] > today].sort_values(by="date")
    return render_template("future.html", records=df_future.to_dict(orient="records"))

@app.route('/delete_meal/<int:index>', methods=['GET', 'POST'])
def delete_meal(index):
    df = pd.read_csv(DATA_PATH)
    if index < len(df):
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(DATA_PATH, index=False)
    return redirect(url_for("form"))

@app.route('/past')
def past():
    today = datetime.today().strftime('%Y-%m-%d')
    try:
        df = pd.read_csv(DATA_PATH)
        df["date"] = pd.to_datetime(df["date"]).dt.strftime('%Y-%m-%d')
        df_past = df[df["date"] < today].sort_values(by="date", ascending=False)
    except Exception as e:
        df_past = pd.DataFrame()
    return render_template("past.html", records=df_past.to_dict(orient="records"))

@app.route('/announcement', methods=["GET", "POST"])
def announcement():
    if request.method == "POST":
        name = request.form.get("name")
        message = request.form.get("message")
        start_date = request.form.get("start_date")
        end_date = request.form.get("end_date")

        if not all([name, message, start_date, end_date]):
            return "入力不足", 400

        df = pd.read_csv(ANNOUNCEMENT_PATH)
        df = pd.concat([df, pd.DataFrame([{
            "name": name,
            "message": message,
            "start_date": start_date,
            "end_date": end_date
        }])], ignore_index=True)
        df.to_csv(ANNOUNCEMENT_PATH, index=False)
        return redirect(url_for("form"))

    return render_template("announcement.html")

@app.route('/delete_announcement/<int:index>', methods=["POST"])
def delete_announcement(index):
    df = pd.read_csv(ANNOUNCEMENT_PATH)
    if index < len(df):
        df = df.drop(index).reset_index(drop=True)
        df.to_csv(ANNOUNCEMENT_PATH, index=False)
    return redirect(url_for("form"))

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host='0.0.0.0', port=port)
