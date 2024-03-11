from flask import Flask, render_template, request, jsonify, session
import weaviate
from weaviate.embedded import EmbeddedOptions
import cohere
import os
import pandas as pd
import numpy as np

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Setup API keys
cohere_api_key = os.getenv('CO_API_KEY')
weaviate_api_key = os.getenv('WEAVIATE_API_KEY')
weaviate_url = os.getenv('WEAVIATE_URL')
openai_api_key = os.getenv('OPENAI_API_KEY')

# Connect to Cohere
co = cohere.Client(cohere_api_key)


# Connect to a Weaviate Cluster instance
client = weaviate.connect_to_wcs(
    cluster_url=weaviate_url,
    auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
)


@app.route("/")
def home():
    return render_template("index.html")


@app.route("/", methods=["POST"])
def get_bot_response():

    # Initialize conversation history list in session if not present
    if "conversation" not in session:
        session["conversation"] = []

    # Add user input to conversation history
    session["conversation"].append({"role": "user", "content": user_response})

    # Get conversation history
    conversation = session["conversation"]

    if len(conversation) == 0:
        user_response = request.json["message"]
        response = get_ai_response(user_response)

        ai_response = response.choices[0].message["content"].strip()

    else:
        previous_response = conversation[-1]
        user_response = request.json["message"]

        response = get_ai_response(user_response)

        ai_response = response.choices[0].message["content"].strip()

    previous_response = {"user": user_response, "assistant": ai_response}
    conversation.append(previous_response)
    session["conversation"].add_assistant_message(ai_response)

    return jsonify({"message": ai_response})

def update_context():

    # Extract relevant information from the matches
    contexts = []
    for item in result["data"]["Get"]["BiologicalStrategy"]:
        contexts.append(f"Text: {item['text']}")

    # Combine the information into formatted contexts
    formatted_contexts = "\n".join(contexts)

    return formatted_contexts


def get_ai_response(user_response):
    string_dialogue = update_context()
    for dict_message in session["conversation"].messages:
        if dict_message["role"] == "user":
            string_dialogue += "User: " + dict_message["content"] + "\\n\\n"
        else:
            string_dialogue += "Assistant: " + dict_message["content"] + "\\n\\n"
            ai_response = co.generate(query_embed=co.embed(texts=[query], input_type=search_query, model="multilingual-22-12"))
    return ai_response.generations[0].text.strip()



if __name__ == "__main__":
    app.run(debug=True)
