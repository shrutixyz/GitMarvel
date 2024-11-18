from flask import Flask, redirect, request, session, url_for, jsonify, render_template
from flask_cors import CORS
import requests
import os

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Secure the session
CORS(app)  # This will allow all origins by default

REDIRECT_URI = "http://localhost:5001/auth/github/callback"

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-started/')
def getstarted():
    return render_template('get-started.html')

@app.route('/dashboard/')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)