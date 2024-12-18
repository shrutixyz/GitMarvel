import re
import json
from dotenv import load_dotenv
import openai
import os
import requests
from flask import  jsonify
import ast

load_dotenv()

sambanovaClient = openai.OpenAI(
    api_key=os.environ.get("SAMBANOVA_API_KEY"),
    base_url="https://api.sambanova.ai/v1",
)

pixabay_api_key=os.environ.get("PIXABAY_API_KEY")

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
            Ensure your feedback is returned in html string with the following fields:- (section, code, feedback). Make bg #1f1f1f, text white and font sans-serif
            """ } ],

    temperature=0.1,
    top_p=0.1)
    result = extract_between_brackets(response.choices[0].message.content)
    
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
            "content": f""" Using the following commit list for repository {repo_name} owned by {owner}, create an interesting story within 300-400 words in paragraphs. Use single quotes for dialogues
            commit list:  ``` json  {commits_list}```
            """ } ],
    temperature=0.1,
    top_p=0.1)

    result = response.choices[0].message.content.split("\n\n")
    image_urls = []
    try:
        keywords_list = ast.literal_eval(generate_keywords_for_images(result))

        if len(keywords_list) > len(result):
            keywords_list = keywords_list[:len(result)]
        for keyword in keywords_list:
     
            output = get_image_url(keyword)
            image_urls.append(output)
    except Exception as e:
        print(f"exception {e}")
        return {
            "paragraphs": result,
            "image_urls": []
        }
    return {
            "paragraphs": result,
            "image_urls": image_urls
        }

def generate_keywords_for_images(storyPoints):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
                    # "content": f"You are an efficient keyword generator machine. Your task is to analyze the following paragraphs list and generate a one word keyword for each item in paragraph. Keep it simple and make use of everyday objects, as i need to download images based on keywords"

        {
            "role": "system",
            "content": f"You are a keyword generator. Your task is to analyze the following paragraphs list and generate a one word keyword for each item in paragraph. Keep it simple and make use of everyday objects"
        },
        {
            "role": "user",
            "content": f""" Using the paragraphs as input, generate a one word keyword for list item. 
            ```story paragraphs list : {storyPoints} ```
            Ensure your keyword list is returned in simple array format with just the desired output
            """ } ],
    temperature=0.1,
    top_p=0.1)
    result = response.choices[0].message.content

    return result

def get_image_url(keyword):
    url = f'https://pixabay.com/api/?key={pixabay_api_key}&q={keyword}&image_type=photo&per_page=3'
    response = requests.get(url)
    # print(response)
    data = response.json()
    # print(data['hits'][0])
    return data['hits'][0]['webformatURL']

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

def extract_between_brackets(input_str):
    # Find the first occurrence of '<' and the last occurrence of '>'
    start = input_str.find('<')
    end = input_str.rfind('>')
    
    # If both are found, slice the string; otherwise, return an empty string
    if start != -1 and end != -1 and start < end:
        res = str(input_str[start: end+1])
        res.replace("<br/>", "")
        return res
    return ""

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
            "content": f""" Using the following user stats for repository {username}, create a swot analysis in html string. Add #1f1f1f bg color, white text color and sans serif font
            profile stats:  ``` json  {profile_stats}```
            """ } ],
    temperature=0.1,
    top_p=0.1)

    result = response.choices[0].message.content
    return extract_between_brackets(result)

def parse_markdown(content):
    content = content.replace("\n", "<br/>")
    return content

models_list = ["Meta-Llama-3.2-1B-Instruct", "Meta-Llama-3.2-3B-Instruct", "Llama-3.2-11B-Vision-Instruct", "Llama-3.2-90B-Vision-Instruct", "Meta-Llama-3.1-8B-Instruct", "Meta-Llama-3.1-70B-Instruct", "Meta-Llama-3.1-405B-Instruct"]
def determine_model(question):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": f"Your task is to return the perfect model to use for the given question, out of {models_list}"
        },
        {
            "role": "user",
            "content": f""" Please review the following question: "{question}" and return the model which will best answer this query. Just return the string with model name and nothing else.
            """ } ],
            temperature=0.1,
    top_p=0.1)
    print(response)
    res = response.choices[0].message.content  
    if res not in models_list:
        return models_list[0]
    return res



def aichat(info, question, prev):
    model_to_use = determine_model(question)
    response = sambanovaClient.chat.completions.create(
    model = model_to_use,
    messages=[
        {
            "role": "system",
            "content": f"You are a highly skilled github profile reviewer. Your task is to analyze the following profile info: {info}."
        },
        {
            "role": "user",
            "content": f""" Please review the following question: "{question}" and answer it in the best way possible within 50 words please. Earlier question was {prev}, incase you need this info
            Ensure your feedback is returned in plain text format
            """ } ],
    temperature=0.1,
    top_p=0.1)
    result = parse_markdown(response.choices[0].message.content)
    
    return [result, model_to_use]
