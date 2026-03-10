from flask import Flask, request, jsonify
from flask_jwt_extended import(
    JWTManager, create_access_token,
    jwt_required, get_jwt_identity
)
import sqlite3

app = Flask(__name__)
app.config["JWT_SECRET_KEY"] = "secretkey123"
jwt = JWTManager(app)

def get_db():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn

# Create table
conn = get_db()
conn.execute("""
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    password TEXT,
    role TEXT
)
""")
conn.commit()
conn.close()

@app.route("/register", methods=["POST"])
def register():
    data = request.json
    conn = get_db()
    conn.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (data["username"], data["password"], data["role"])
    )
    conn.commit()
    conn.close()
    return jsonify({"message": "User registered successfully"})

@app.route("/login", methods=["POST"])
def login():
    data = request.json
    conn = get_db()
    user = conn.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (data["username"], data["password"])
    ).fetchone()
    conn.close()

    if user:
        token = create_access_token(identity={"username": user["username"], "role": user["role"]})
        return jsonify(access_token=token)
    return jsonify({"message": "Invalid credentials"}), 401

@app.route("/admin", methods=["GET"])
@jwt_required()
def admin():
    user = get_jwt_identity()
    if user["role"] != "admin":
        return jsonify({"message": "Access denied"}), 403
    return jsonify({"message": "Welcome Admin"})

@app.route("/user", methods=["GET"])
@jwt_required()
def user():
    return jsonify({"message": "Welcome User"})

if __name__ == "__main__":
    app.run(debug=True)
