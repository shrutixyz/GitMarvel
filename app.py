from flask import Flask, redirect, request, session, url_for, jsonify, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import openai
import re
import json

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')

CORS(app)  # This will allow all origins by default

CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_REPOS_URL = "https://api.github.com/user/repos"
GITHUB_API_BASE_URL = "https://api.github.com"

sambanovaClient = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/get-started/')
def getstarted():
    access_token = session.get('github_access_token')

    if access_token:
        return redirect(url_for('dashboard'))
    
    github_login_url = f"{GITHUB_AUTH_URL}?client_id={CLIENT_ID}&scope=read:user"
    return render_template('get-started.html', github_login_url=github_login_url)

@app.route('/auth/github/callback')
def callback():
    
    code = request.args.get('code')

    # Exchange the code for an access token
    token_response = requests.post(
        GITHUB_TOKEN_URL,
        headers={'Accept': 'application/json'},
        data={
            'client_id': CLIENT_ID,
            'client_secret': CLIENT_SECRET,
            'code': code
        }
    )
    token_response_json = token_response.json()
    access_token = token_response_json.get('access_token')

    if access_token:
        session['github_access_token'] = access_token
        return redirect(url_for('dashboard'))
    else:
        return "Authorization failed", 400
    
@app.route('/dashboard')
def dashboard():
    access_token = session.get('github_access_token')
    if not access_token:
        return redirect(url_for('get-started'))
    print(access_token)

    user_response = requests.get(
        GITHUB_USER_URL,
        headers={'Authorization': f'Bearer {access_token}'}
    )
    user_data = user_response.json()

    repos_response = requests.get(GITHUB_REPOS_URL, headers={'Authorization': f'Bearer {access_token}'})

    if repos_response.status_code == 200:
        repos = repos_response.json()  # List of repository objects
    else:
        print( f"Error: {repos_response.status_code}", 500)
    return render_template('dashboard.html', userName=user_data.get('login'), avatar_url = user_data.get('avatar_url'), repos = repos)


@app.route('/code-review', methods=['POST'])
def code_review():
    data = request.json
    repo_name = data.get('repo_name')
    commit_sha = data.get('commit_sha')
    owner = data.get('owner')
    github_token = session.get('github_access_token') # Pass user's GitHub token securely

    if not repo_name or not commit_sha or not github_token:
        return jsonify({"error": "repo_name, commit_sha, and github_token are required"}), 400

    # Step 1: Fetch commit details from GitHub
    commit_url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}/commits/{commit_sha}"
    headers = {'Authorization': f'Bearer {github_token}'}
    commit_response = requests.get(commit_url, headers=headers)

    if commit_response.status_code != 200:
        return jsonify({"error": "Failed to fetch commit details", "details": commit_response.text}), 500

    commit_data = commit_response.json()
    files = commit_data.get('files', [])

    # Step 2: Fetch file contents and prepare for AI review
    file_reviews = []
    for file in files:
        file_path = file['filename']
        raw_url = file['raw_url']

        # Fetch file content
        file_response = requests.get(raw_url, headers=headers)
        if file_response.status_code != 200:
            return jsonify({"error": f"Failed to fetch file content for {file_path}"}), 500

        file_content = file_response.text

        # Prepare data for AI agent
        file_reviews.append({
            "filename": file_path,
            "content": file_content
        })

    # todo: send data to ai agent
    return jsonify({"review_comments": file_reviews})


@app.route('/logout')
def logout():
    session.pop('github_access_token')
    return redirect(url_for("index"))

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)