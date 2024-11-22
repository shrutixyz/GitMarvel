import re
import json
from dotenv import load_dotenv
import openai
import os

load_dotenv()

sambanovaClient = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

def testai(code_content, language):
    print(code_content[:100], language)
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": f"You are a highly skilled code reviewer. Your task is to analyze the following {language} code and suggest detailed improvements."
        },
        {
            "role": "user",
            "content": f""" Please review the following {language} code and suggest improvements. 
            ```code : {code_content} ```
            Ensure your feedback is returned in html string with the following fields:- (section, code, feedback) 
            """ } ],

    temperature=0.1,
    top_p=0.1)
    result = parse_markdown(response.choices[0].message.content)
    
    return result

def get_language_from_extension(file_name):
    # Dictionary mapping file extensions to programming languages
    file_extension_to_language = {
        '.py': 'Python',
        '.js': 'JavaScript',
        '.ts': 'TypeScript',
        '.tsx': 'TypeScript',
        '.java': 'Java',
        '.c': 'C',
        '.cpp': 'C++',
        '.go': 'Go',
        '.rb': 'Ruby',
        '.php': 'PHP',
        '.html': 'HTML',
        '.css': 'CSS',
        '.json': 'JSON',
        '.xml': 'XML',
        '.sql': 'SQL',
        '.swift': 'Swift',
        '.kt': 'Kotlin',
        '.sh': 'Shell Script',
        '.bash': 'Bash',
        '.r': 'R',
        '.pl': 'Perl',
        '.md': 'Markdown',
        '.dart': 'Dart',
        '.lua': 'Lua',
        '.scss': 'Sass',
        '.v': 'Verilog',
        '.vhdl': 'VHDL',
        '.scala': 'Scala',
        '.h': 'C Header',
        '.hpp': 'C++ Header',
    }

    # Extract the file extension
    extension = file_name.split('.')[-1] 
    file_ext = f'.{extension.lower()}'  

    return file_extension_to_language.get(file_ext, 'Unknown')

def get_story_from_commit_history(repo_name, commits_list, owner):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": "You are an award winning author. Your task is to create an engaging story from the commit history of a github repo. Use date parameter to establish chronology"
        },
        {
            "role": "user",
            "content": f""" Using the following commit list for repository {repo_name} owned by {owner}, create an interesting story. 
            commit list:  ``` json  {commits_list}```
            """ } ],
    temperature=0.1,
    top_p=0.1)

    result = response.choices[0].message.content
    return result

def get_readme_from_files_list(repo_name, file_list, owner):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": "You are 5 star open source maintainer. Your task is to generate README file from the file list"
        },
        {
            "role": "user",
            "content": f""" Using the following file list for repository {repo_name} owned by {owner}, create a README file. 
            commit list:  ``` json  {file_list}```
            """ } ],
    temperature=0.1,
    top_p=0.1)

    result = response.choices[0].message.content
    return result


def get_profile_analysis_from_stats(username, profile_stats):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": "You are a professional github profile critic. Your task is to do swot analysis of the given github profile from its user stats"
        },
        {
            "role": "user",
            "content": f""" Using the following user stats for repository {username}, create a swot analysis in html string. 
            profile stats:  ``` json  {profile_stats}```
            """ } ],
    temperature=0.1,
    top_p=0.1)

    result = response.choices[0].message.content
    return result

def parse_markdown(content):
    content = content.replace("\n", "<br/>")
    return content


def aichat(info, question):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": f"You are a highly skilled github profile reviewer. Your task is to analyze the following profile info: {info}."
        },
        {
            "role": "user",
            "content": f""" Please review the following question: "{question}" and answer it in the best way possible.
            Ensure your feedback is returned in plain text format 
            """ } ],
    temperature=0.1,
    top_p=0.1)
    result = parse_markdown(response.choices[0].message.content)
    
    return result