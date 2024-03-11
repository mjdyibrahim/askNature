from flask import Flask, render_template, request, jsonify, session
import weaviate
from weaviate.embedded import EmbeddedOptions
import cohere
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np

load_dotenv()

app = Flask(__name__)
app.secret_key = os.urandom(24)  # Set a secret key for session management

# Load embeddings from .npy files
innovations_embeddings = np.load('biological-innovations_embeddings.npy')
strategies_embeddings = np.load('biological-strategies_embeddings.npy')

# Combine embeddings to create context string
context_embeddings = np.concatenate((innovations_embeddings, strategies_embeddings), axis=0)
context_string = ' '.join(map(str, context_embeddings.flatten()))

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

    # Get user response from JSON request
    user_response = request.json.get("message")  # Use get method to safely access JSON data

    if user_response:
        # Add user input to conversation history
        session["conversation"].append({"role": "user", "content": user_response})

        # Get conversation history
        conversation = session["conversation"]

        if len(conversation) == 0:
            response = get_ai_response(user_response)
            ai_response = None
        else:
            response = get_ai_response(user_response)
            ai_response = response.choices[0].message["content"].strip()

        previous_response = {"user": user_response, "assistant": ai_response}
        conversation.append(previous_response)
        session["conversation"].add_assistant_message(ai_response)

        return jsonify({"message": ai_response})
    else:
        return jsonify({"error": "No message provided"})



def get_ai_response(conversation):
    conversation_string = ""
    for message in conversation:
        if message["role"] == "user":
            conversation_string += "User: " + message["content"] + "\\n\\n"
        else:
            conversation_string += "Assistant: " + message["content"] + "\\n\\n"
    
    response = co.generate(query_embed=co.embed(texts=conversation_string, context=context_string, input_type="search_query", model="multilingual-22-12"))

    ai_response = response.generations[0].text.strip()

    return ai_response


if __name__ == "__main__":
    app.run(debug=True)
