from flask import Flask, render_template, request
from prompt_template import PROMPT_TEMPLATE  # Importing the prompt template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

import openai

# Set your OpenAI API key
openai.api_key = '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'

def generate_biomimicry_solution(user_input):
    # Construct the prompt using the provided template and user input
    prompt = PROMPT_TEMPLATE.format(user_input=user_input)

    # Send prompt to OpenAI API
    response = openai.Completion.create(
        engine="text-davinci-003",  # Choose the model you want to use
        prompt=prompt,
        max_tokens=1500  # Adjust based on the length of your prompt
    )

    # Process the response
    return response.choices[0].text.strip()

@app.route('/submit', methods=['POST'])
def submit():
    # Retrieve user input from the form
    problem_statement = request.form['problem_statement']
    context = request.form['context']
    systems_view = request.form['systems_view']
    challenge_question = request.form['challenge_question']

    # Example user input
    user_input = {
        "problem_statement": problem_statement,
        "context": context,
        "systems_view": systems_view,
        "challenge_question": challenge_question,
        "function": "Keep food fresh for longer periods.",
        "form": "Optimal shape and structure for food packaging.",
        "material": "Environmentally friendly materials that can be recycled or composted.",
        "surface": "Surface properties that prevent moisture or air from entering the packaging.",
        "architecture": "Internal structure that supports the form and function of the packaging.",
        "process": "Efficient manufacturing process with minimal waste.",
        "system": "Integration with existing food distribution systems and waste management infrastructure."
    }

    # Generate biomimicry solution based on user input
    biomimicry_solution = generate_biomimicry_solution(user_input)

    # Display the generated solution to the user
    return biomimicry_solution

# Add more routes and functions as needed...

if __name__ == '__main__':
    app.run(debug=True)
