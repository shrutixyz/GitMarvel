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
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": "You are a highly skilled code reviewer. Your task is to analyze the following React + TypeScript code and suggest detailed improvements."
        },
        {
            "role": "user",
            "content": """ Please review the following {language} code and suggest improvements. 
            ```code : {code_content} ```
            Ensure your feedback is returned in JSON format with the following fields:- {section, code, feedback} 
            """ } ],
    temperature=0.1,
    top_p=0.1)
    result = response.choices[0].message.content
    jsonified_response = complex_json_parse(result)

    return jsonified_response

def complex_json_parse(content):
    # Extract the JSON block from the input content using regex
    json_match = re.search(r'```json\n(.*?)\n```', content, re.DOTALL)
    
    if json_match:
        # Extract the JSON data part
        json_data = json_match.group(1)
        
        # Parse the JSON data
        try:
            parsed_json = json.loads(json_data)
        except json.JSONDecodeError:
            raise ValueError("Invalid JSON format in the input")
        
        # Extract the remaining feedback after the JSON block
        feedback_start = content.find('Here are some general suggestions for improvement:')
        if feedback_start != -1:
            feedback = content[feedback_start:].strip()
        else:
            feedback = "No general feedback provided."

        # Return both the parsed JSON and the extracted feedback
        return {
            "json_data": parsed_json,
            "final_feedback": feedback
        }
    else:
        raise ValueError("No JSON block found in the input")

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
