from flask import Flask, render_template, jsonify
from app import state

app = Flask(__name__)

@app.route("/")
def index():
    return render_template("index.html", score=state.latest_score)

@app.route("/get_score")
def get_score():
    return jsonify(state.latest_score)

def update_score(new_score):
    state.latest_score["quality"] = round(new_score, 2)
    state.latest_score["status"] = "👍 Good stroke" if new_score > 0.5 else "👎 Bad stroke"
    print(f"✅ Stroke quality score: {new_score:.2f}")
    print(state.latest_score["status"])
    return state.latest_score
