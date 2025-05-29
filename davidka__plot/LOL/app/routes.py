from flask import Flask, render_template, jsonify

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/get_score")
def get_score():
    latest_score = update_score()
    print("IN GETSCORE", latest_score)
    return jsonify(latest_score)

def update_score():
    try:
        f = open("data/states.txt", "r", encoding="UTF-8")
        new_score = float(f.readline().strip())
    except:
        f = open("data/states.txt", "w", encoding="UTF-8")
        return {"quality": None, "status": "No data"}

    latest_score = {}
    latest_score["quality"] = round(new_score, 5)
    latest_score["status"] = "👍 Good stroke" if new_score > 0.5 else "👎 Bad stroke"
    print(f"✅ Stroke quality score: {new_score:.2f}")
    print(latest_score["status"])
    return latest_score