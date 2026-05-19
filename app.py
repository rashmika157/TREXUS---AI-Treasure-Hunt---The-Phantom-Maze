from flask import Flask, render_template, request, jsonify
import sqlite3
import os

app = Flask(__name__)

DB_FILE = 'leaderboard.db'

import random

ALL_QUESTIONS = [
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
    },
    {
        "q": "Understands human language",
        "ans": "natural language processing",
        "altAns": ["nlp"],
        "loc": "0+0=row,0+1=col",
        "pos": [0, 1],
        "hints": ["Text analysis", "Siri uses this", "N L P"]
    },
    {
        "q": "Learns by trial and error",
        "ans": "reinforcement learning",
        "altAns": ["rl", "reinforcement"],
        "loc": "5-1=row,2+3=col",
        "pos": [4, 5],
        "hints": ["Rewards and punishments", "Used in game playing AI", "AlphaGo uses this"]
    },
    {
        "q": "Grouping unlabelled data",
        "ans": "clustering",
        "altAns": ["cluster analysis", "clusters"],
        "loc": "1+1=row,4-4=col",
        "pos": [2, 0],
        "hints": ["K-Means is an example", "Finding hidden patterns", "Grouping similar things"]
    },
    {
        "q": "Learning from labelled data",
        "ans": "supervised learning",
        "altAns": ["supervised", "supervised machine learning"],
        "loc": "5-4=row,3+0=col",
        "pos": [1, 3],
        "hints": ["Needs a teacher", "Data has tags/labels", "Predicting known outcomes"]
    },
    {
        "q": "Learning from unlabelled data",
        "ans": "unsupervised learning",
        "altAns": ["unsupervised", "unsupervised machine learning"],
        "loc": "0+5=row,2+0=col",
        "pos": [5, 2],
        "hints": ["No teacher needed", "Finding hidden structures", "Opposite of supervised"]
    },
    {
        "q": "Network with many layers",
        "ans": "deep learning",
        "altAns": ["dl", "deep neural network"],
        "loc": "3-2=row,4+1=col",
        "pos": [1, 5],
        "hints": ["Subset of ML", "Uses deep neural networks", "Deep ___"]
    },
    {
        "q": "AI creating images or text",
        "ans": "generative ai",
        "altAns": ["gen ai", "generative artificial intelligence"],
        "loc": "2+2=row,0+0=col",
        "pos": [4, 0],
        "hints": ["Creates new content", "Midjourney is an example", "Generative ___"]
    },
    {
        "q": "Identifying people in photos",
        "ans": "facial recognition",
        "altAns": ["face recognition", "face detection"],
        "loc": "1+2=row,5-1=col",
        "pos": [3, 4],
        "hints": ["Unlocks your phone", "Biometric AI", "Facial ___"]
    },
    {
        "q": "Predicting numerical values",
        "ans": "regression",
        "altAns": ["linear regression", "regression analysis"],
        "loc": "5-5=row,1+2=col",
        "pos": [0, 3],
        "hints": ["Predicting house prices", "Statistical ML method", "Linear ___"]
    },
    {
        "q": "AI playing board games",
        "ans": "game ai",
        "altAns": ["game artificial intelligence", "gaming ai"],
        "loc": "4-2=row,4-2=col",
        "pos": [2, 2],
        "hints": ["Used in chess", "NPC behavior", "Game ___"]
    },
    {
        "q": "Converting text to audio",
        "ans": "text to speech",
        "altAns": ["tts", "text-to-speech"],
        "loc": "3+2=row,1+0=col",
        "pos": [5, 1],
        "hints": ["Voice assistants use this", "Reading text aloud", "T T S"]
    },
    {
        "q": "Algorithm for optimization",
        "ans": "gradient descent",
        "altAns": ["stochastic gradient descent", "sgd"],
        "loc": "1+0=row,1+1=col",
        "pos": [1, 2],
        "hints": ["Finding the minimum", "Used in training neural nets", "Moving down the slope"]
    },
    {
        "q": "Categorizing items",
        "ans": "classification",
        "altAns": ["classifier", "classifying"],
        "loc": "4-1=row,5-2=col",
        "pos": [3, 3],
        "hints": ["Spam or not spam", "Sorting into buckets", "Supervised ML task"]
    },
    {
        "q": "Famous AI test",
        "ans": "turing test",
        "altAns": ["the turing test"],
        "loc": "0+2=row,0+4=col",
        "pos": [2, 4],
        "hints": ["Proposed by Alan Turing", "Imitation game", "Testing machine intelligence"]
    },
    {
        "q": "Data representing text",
        "ans": "word embedding",
        "altAns": ["embeddings", "word2vec", "embedding"],
        "loc": "4-4=row,4-4=col",
        "pos": [0, 0],
        "hints": ["Vectors for words", "Word2Vec is one", "Captures semantic meaning"]
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

@app.route("/api/start_game", methods=["GET"])
def start_game():
    count = request.args.get('count', default=5, type=int)
    if count > len(ALL_QUESTIONS):
        count = len(ALL_QUESTIONS)
    level_ids = random.sample(range(len(ALL_QUESTIONS)), count)
    return jsonify({"level_ids": level_ids})

@app.route("/api/get_level", methods=["GET"])
def get_level():
    level_id = request.args.get('id', default=0, type=int)
    if level_id >= len(ALL_QUESTIONS) or level_id < 0:
        return jsonify({"error": "Level not found", "completed": True})
    
    lvl = ALL_QUESTIONS[level_id]
    # Do not send the answers to the frontend!
    safe_lvl = {
        "q": lvl["q"],
        "loc": lvl["loc"],
        "pos": lvl["pos"],
        "hints": lvl["hints"]
    }
    return jsonify(safe_lvl)

@app.route("/api/get_answer", methods=["GET"])
def get_answer():
    level_id = request.args.get('id', default=0, type=int)
    if level_id >= len(ALL_QUESTIONS) or level_id < 0:
        return jsonify({"error": "Level not found"})
    return jsonify({"answer": ALL_QUESTIONS[level_id]["ans"]})

@app.route("/api/verify_answer", methods=["POST"])
def verify_answer():
    data = request.json
    level_id = data.get('level_id', 0)
    user_input = data.get('answer', '').lower().strip()
    
    if level_id >= len(ALL_QUESTIONS) or level_id < 0:
        return jsonify({"correct": False, "error": "Invalid level"})
        
    lvl = ALL_QUESTIONS[level_id]
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