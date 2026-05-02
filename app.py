from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'leaderboard.db'

LEVELS = [
    {
        "q": "Learns from data",
        "ans": "machine learning",
        "altAns": ["ml", "machine learnings", "machine-learning"],
        "loc": "2+3=row,5-1=col",
        "pos": [5, 4],
        "hints": ["Used in Netflix", "AI subset", "Machine ___"]
    },
    {
        "q": "Search algo",
        "ans": "a* algorithm",
        "altAns": ["a star", "a*", "a star algorithm", "a* algo"],
        "loc": "Center",
        "pos": [2, 2],
        "hints": ["Used in maps", "Graph search", "A star"]
    },
    {
        "q": "Brain-inspired model",
        "ans": "neural network",
        "altAns": ["neural networks", "nn", "artificial neural network", "ann"],
        "loc": "1+0=row,3+2=col",
        "pos": [1, 5],
        "hints": ["Has layers", "Deep learning base", "Artificial ___"]
    },
    {
        "q": "Text generator AI",
        "ans": "chatgpt",
        "altAns": ["chat gpt", "gpt", "chat-gpt", "chat gpt-3"],
        "loc": "4+0=row,1+0=col",
        "pos": [4, 1],
        "hints": ["Made by OpenAI", "LLM", "Generative Pre-trained Transformer"]
    },
    {
        "q": "AI that sees",
        "ans": "computer vision",
        "altAns": ["cv", "computer visions"],
        "loc": "3+0=row,2+1=col",
        "pos": [3, 3],
        "hints": ["Used in self-driving cars", "Image processing", "Computer ___"]
    }
]

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS scores
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, score INTEGER)''')
    conn.commit()
    conn.close()

init_db()

def levenshtein_distance(s1, s2):
    if len(s1) < len(s2):
        return levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    
    previous_row = range(len(s2) + 1)
    for i, c1 in enumerate(s1):
        current_row = [i + 1]
        for j, c2 in enumerate(s2):
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (c1 != c2)
            current_row.append(min(insertions, deletions, substitutions))
        previous_row = current_row
    
    return previous_row[-1]

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/api/get_level", methods=["GET"])
def get_level():
    level_index = request.args.get('index', default=0, type=int)
    if level_index >= len(LEVELS):
        return jsonify({"error": "Level not found", "completed": True})
    
    lvl = LEVELS[level_index]
    # Do not send the answers to the frontend!
    safe_lvl = {
        "q": lvl["q"],
        "loc": lvl["loc"],
        "pos": lvl["pos"],
        "hints": lvl["hints"],
        "total_levels": len(LEVELS)
    }
    return jsonify(safe_lvl)

@app.route("/api/get_answer", methods=["GET"])
def get_answer():
    level_index = request.args.get('index', default=0, type=int)
    if level_index >= len(LEVELS):
        return jsonify({"error": "Level not found"})
    return jsonify({"answer": LEVELS[level_index]["ans"]})

@app.route("/api/verify_answer", methods=["POST"])
def verify_answer():
    data = request.json
    level_index = data.get('level_index', 0)
    user_input = data.get('answer', '').lower().strip()
    
    if level_index >= len(LEVELS):
        return jsonify({"correct": False, "error": "Invalid level"})
        
    lvl = LEVELS[level_index]
    is_correct = False
    
    if user_input == lvl["ans"] or (user_input in lvl["altAns"]):
        is_correct = True
    else:
        dist = levenshtein_distance(user_input, lvl["ans"])
        threshold = 2 if len(lvl["ans"]) > 5 else 1
        if dist <= threshold:
            is_correct = True
        else:
            for alt in lvl["altAns"]:
                alt_dist = levenshtein_distance(user_input, alt)
                alt_threshold = 2 if len(alt) > 5 else 1
                if alt_dist <= alt_threshold:
                    is_correct = True
                    break
                    
    return jsonify({"correct": is_correct})

@app.route("/api/submit_score", methods=["POST"])
def submit_score():
    data = request.json
    name = data.get('name', 'Anonymous')
    score = data.get('score', 0)
    
    if name.strip() == '':
        name = 'Anonymous'
        
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("INSERT INTO scores (name, score) VALUES (?, ?)", (name, score))
    conn.commit()
    conn.close()
    
    return jsonify({"success": True})

@app.route("/api/get_scores", methods=["GET"])
def get_scores():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("SELECT name, score FROM scores ORDER BY score DESC LIMIT 5")
    scores = [{"name": row[0], "score": row[1]} for row in c.fetchall()]
    conn.close()
    
    return jsonify(scores)

if __name__ == "__main__":
    app.run(debug=True)