
def testai(code_content):
    response = sambanovaClient.chat.completions.create(
    model="Meta-Llama-3.1-8B-Instruct",
    messages=[
        {
            "role": "system",
            "content": "You are a highly skilled code reviewer. Your task is to analyze the following React + TypeScript code and suggest detailed improvements."
        },
        {
            "role": "user",
            "content": """ Please review the following React TypeScript code and suggest improvements. 
            ```code : {code_content} ```
            Ensure your feedback is returned in JSON format with the following fields:- {section, code, feedback} 
            """ } ],
    temperature=0.1,
    top_p=0.1)
    result = response.choices[0].message.content
    # Parse the JSON string into a Python dictionary
    # parsed_feedback = json.loads(result)

    # Print parsed feedback
    # print("Parsed Feedback:", parsed_feedback)
    return jsonify(result)
