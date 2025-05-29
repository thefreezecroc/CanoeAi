from flask import Flask, render_template, jsonify

app = Flask(__name__)

# In-memory placeholder for latest stroke quality
latest_score = {"quality": None, "status": "Waiting for data..."}

@app.route("/")
def index():
    return render_template("index.html", score=latest_score)

@app.route("/get_score")
def get_score():
    return jsonify(latest_score)

# Call this function from your BLE handler after evaluating stroke
def update_score(new_score):
    latest_score["quality"] = round(new_score, 2)
    latest_score["status"] = "👍 Good stroke" if new_score > 0.5 else "👎 Bad stroke"
