# GitMarvel

GitMarvel is a Flask-based web application that integrates with GitHub and Sambanova AI to provide users with useful insights, code reviews, and more. It allows users to log in with their GitHub account and access various features, such as generating README files, analyzing their GitHub profiles, and chatting with an AI to review their code.

## Features

- **GitHub Integration**: Login with GitHub, view repositories, and get code reviews.
- **Profile Analysis**: Receive insights and recommendations based on your GitHub profile.
- **Code Review**: Automatically generate detailed code reviews for your repositories.
- **AI-Powered Conversations**: Chat with an AI to get insights on your code, ask questions, and more.
- **README Generation**: Let GitMarvel generate a structured README file for your project.

## Prerequisites

Before running the app, ensure you have the following installed:

- Python 3.7+ (recommended)
- Flask
- Required Python libraries (can be installed via `requirements.txt`)

## Setup Instructions

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/gitmarvel.git
   cd gitmarvel
   ```

2. Create a virtual environment and activate it:

   - **For Linux/macOS**:
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```

   - **For Windows**:
     ```bash
     python -m venv venv
     venv\Scripts\activate
     ```

3. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Set up your environment variables:
   Create a `.env` file in the root of the project directory and add the following values:

   ```bash
   export FLASK_SECRET_KEY='your_secret_key'
   export CLIENT_ID='your_github_client_id'
   export CLIENT_SECRET='your_github_client_secret'
   export SAMBANOVA_API_KEY='your_sambanova_api_key'
   ```

   Replace the placeholders (`your_secret_key`, `your_github_client_id`, `your_github_client_secret`, `your_sambanova_api_key`) with your actual credentials.

5. Initialize the Flask app:
   ```bash
   export FLASK_APP=app.py
   export FLASK_ENV=development
   ```

6. Run the Flask app:
   ```bash
   flask run
   ```

   By default, the app will be available at `http://127.0.0.1:5001`.