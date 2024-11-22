from flask import Flask, redirect, request, session, url_for, jsonify, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os
import openai
import re
import json
import asyncio
from sambanova_utils import *
from github_utils import *
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

    repos_url = 'https://api.github.com/user/repos?visibility=all'
    repos = []
    while repos_url:
        headers = {'Authorization': f'token {access_token}'}
        response = requests.get(repos_url, headers=headers)
        
        if response.status_code != 200:
            print(f"Failed to fetch repos: {response.text}")
            break
        
        repos.extend(response.json())
        
        # Check for the next page using the Link header
        if 'link' in response.headers:
            links = response.headers['link']
            next_repos_url = None
            for link in links.split(','):
                if 'rel="next"' in link:
                    next_repos_url = link[link.find('<') + 1:link.find('>')]
                    break
            repos_url = next_repos_url
        else:
            repos_url = None

    filtered_repo = [{'name': repo['name'], 'full_name': repo['full_name']} for repo in repos]
    session["filtered_repo"] = filtered_repo
    session["avatar_url"] =  user_data.get('avatar_url')
    session["userName"] = user_data.get('login')

    return render_template('dashboard.html', userName=user_data.get('login'), avatar_url = user_data.get('avatar_url'), repos = filtered_repo)


@app.route('/code-review', methods=['POST'])
def code_review():
    data = request.json
    print(data)
    repo_name = data.get('repo_name')
    commit_sha = data.get('commit_sha')
    owner = data.get('owner')
    github_token = session.get('github_access_token') # Pass user's GitHub token securely
    print(github_token, owner, repo_name, commit_sha)

    if not repo_name or not commit_sha or not github_token:
        return jsonify({"error": "repo_name, commit_sha, and github_token are required"}), 400

    # Step 1: Fetch commit details from GitHub
    commit_url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}/commits/{commit_sha}"
    print(commit_url)

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
 
        language = get_language_from_extension(file_path)
        fileresponse = testai(file_content[:2000] if len(file_content) > 2000 else file_content, language=language)

        file_reviews.append({
            "filename": file_path,
            "code_review": fileresponse
        })
    return jsonify({"review_comments": file_reviews})

@app.route('/story-telling/<repo_name>/<owner>')
def story_telling(repo_name, owner):

    github_token = session.get('github_access_token') 

    if not repo_name or not github_token:
        return jsonify({"error": "repo_name and github_token are required"}), 400

    # Step 1: Fetch commit details from GitHub
    commit_url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}/commits"

    headers = {'Authorization': f'Bearer {github_token}'}
    commit_response = requests.get(commit_url, headers=headers)

    if commit_response.status_code == 200:
        commits = commit_response.json()
        # Format and return commit details
        commit_list = [
            {
                "sha": commit["sha"],
                "message": commit["commit"]["message"],
                "author": commit["commit"]["author"]["name"],
                "date": commit["commit"]["author"]["date"],
                "url": commit["html_url"]
            }
            for commit in commits
        ]

        # send message to ai
        isImagePresent = False
        response = get_story_from_commit_history(repo_name=repo_name, commits_list=commit_list, owner=owner)
        if (len(response["image_urls"]) > 0):
            isImagePresent = True
            pages = list(zip(response["image_urls"][::-1], response["paragraphs"][::-1]))
        else:
            pages = response["paragraphs"][::-1]
        return render_template('book.html', pages = pages, isImagePresent= isImagePresent, repo=repo_name)

        # return response["paragraphs"]
    return jsonify({"error": f"Failed to fetch commits: {commit_response.status_code}"}), commit_response.status_code

@app.route('/logout')
def logout():
    session.pop('github_access_token')
    return redirect(url_for("index"))

@app.route('/debug')
def debug():
    github_token = session.get('github_access_token')
    res = fetch_profile_info("aakzsh", github_token)
    return jsonify(res)

@app.route('/chat', methods=['POST'])
def chat():
    github_token = session.get('github_access_token') 
    data = request.json
    username = data.get('username')
    question = data.get('question')
    info = fetch_profile_info(username=username, access_token=github_token)
    res = aichat(info, question)
    print(res)
    return str(res)


@app.route('/readme', methods=['POST'])
def readme():
    data = request.json
    repo_name = data.get('repo_name')
    owner = data.get('owner')

    github_token = session.get('github_access_token')

    if not repo_name or not github_token:
        return jsonify({"error": "repo_name and github_token are required"}), 400

    # Step 1: Fetch commit details from GitHub
    commit_url = f"{GITHUB_API_BASE_URL}/repos/{owner}/{repo_name}/contents"

    headers = {'Authorization': f'Bearer {github_token}'}

    def get_file_names_recursively(owner, repo, path):
        url = f"https://api.github.com/repos/{owner}/{repo}/contents/{path}"

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            contents = response.json()
            for item in contents:
                if item['type'] == 'file':
                    print(item['path'])   

                elif item['type'] == 'dir':
                    get_file_names_recursively(owner, repo, item['path'])
    try:
        all_files = get_file_names_recursively(owner=owner, repo=repo_name, path="")
        
        response = get_readme_from_files_list(owner=owner,repo_name=repo_name, file_list=all_files)
        return jsonify({"readMe": response})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

 
@app.route('/profile-review')

def get_github_profile_stats():
    
    access_token = session.get('github_access_token')
    username = session.get('userName')

    headers = {
        "Authorization": f"Bearer {access_token}" if access_token else None,
        "Accept": "application/vnd.github.v3+json"
    }
    
    base_url = "https://api.github.com"
    
    # Fetch user information
    user_response = requests.get(f"{base_url}/users/{username}", headers=headers)
    if user_response.status_code != 200:
        return {"error": f"Unable to fetch user data. Status code: {user_response.status_code}"}
    user_data = user_response.json()
    
    # Fetch user repositories
    repos_response = requests.get(f"{base_url}/users/{username}/repos?per_page=100", headers=headers)
    if repos_response.status_code != 200:
        return {"error": f"Unable to fetch repositories. Status code: {repos_response.status_code}"}
    repos_data = repos_response.json()
    
    # Compute repository stats
    total_stars = sum(repo.get('stargazers_count', 0) for repo in repos_data)
    total_forks = sum(repo.get('forks_count', 0) for repo in repos_data)
    total_open_issues = sum(repo.get('open_issues_count', 0) for repo in repos_data)
    top_repo = max(repos_data, key=lambda repo: repo.get('stargazers_count', 0), default=None)
    
    # Fetch contributions (requires authenticated access)
    contributions_response = requests.get(f"{base_url}/users/{username}/events", headers=headers)
    contributions_count = len(contributions_response.json()) if contributions_response.status_code == 200 else "N/A"
    
    # Compile stats
    profile_stats = {
        "username": user_data.get("login"),
        "name": user_data.get("name"),
        "bio": user_data.get("bio"),
        "followers": user_data.get("followers"),
        "following": user_data.get("following"),
        "public_repos": user_data.get("public_repos"),
        "total_stars": total_stars,
        "total_forks": total_forks,
        "total_open_issues": total_open_issues,
        "top_repo": {
            "name": top_repo.get("name") if top_repo else None,
            "stars": top_repo.get("stargazers_count") if top_repo else None,
            "forks": top_repo.get("forks_count") if top_repo else None,
        },
        "recent_contributions_count": contributions_count
    }
    response = get_profile_analysis_from_stats(username, profile_stats=profile_stats)
    return jsonify({"analysis": response})

@app.route('/get-code-review')
def get_code_review():
    userName = session.get('userName')
    avatar_url = session.get('avatar_url')
    repos = session.get('filtered_repo')
    return render_template('code-review.html', userName=userName, avatar_url = avatar_url, repos = repos)

@app.route('/book')
def book():
    return render_template('book.html')

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)