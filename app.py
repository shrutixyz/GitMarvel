from flask import Flask, redirect, request, session, url_for, jsonify, render_template
from flask_cors import CORS
import requests
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY')


CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
GITHUB_AUTH_URL = "https://github.com/login/oauth/authorize"
GITHUB_TOKEN_URL = "https://github.com/login/oauth/access_token"
GITHUB_USER_URL = "https://api.github.com/user"
GITHUB_REPOS_URL = "https://api.github.com/user/repos"
CORS(app)  # This will allow all origins by default


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


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001, debug=True)