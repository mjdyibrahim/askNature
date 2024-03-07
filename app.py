from flask import Flask, render_template, request
import weaviate
from weaviate.embedded import EmbeddedOptions
import cohere
import os
import pandas as pd
import numpy as np

app = Flask(__name__)

# Setup API keys
cohere_api_key = os.getenv('cohere_api_key')
weaviate_api_key = os.getenv('weaviate_api_key')
weaviate_url = os.getenv('weaviate_url')
openai_api_key = os.getenv('openai_api_key')
  
# Connect to Cohere
co = cohere.Client(cohere_api_key)


# Connect to a Weaviate Cluster instance
client = weaviate.connect_to_wcs(
    cluster_url=weaviate_url,
    auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key))


response = co.embed(
    texts=texts, 
    model='multilingual-22-12').embeddings
embeds = np.array(response)


# Indexing in Weaviate
# Create classes and objects in Weaviate corresponding to your data and embeddings
# Assuming 'embeds' is your embeddings array

class_name = "BiologicalStrategy"

for i, text in enumerate(texts):
    obj = {
        "text": text,
        "embedding": embeds[i].tolist()
    }
    client.create_object(class_name, obj)

# Continue with your complete and index route functions

    # Build the prompt with the retrieved contexts included
    prompt_start = (
        f"Answer the Query based on the contexts, if it's not in the contexts say 'I don't know the answer'. \n\n"
        f"Context:\n"
    )
    prompt_end = (
        f"\n\nQuery: {query}\nAnswer in the language of Query, if Query is in English Answer in English. Please provide reference Quran verses."
    )

    # Append contexts until hitting the limit
    for i in range(1, len(contexts)):
        if len("".join(contexts[:i])) >= limit:
            prompt = (
                prompt_start +
                "".join(contexts[:i-1]) +
                prompt_end
            )
            break
        elif i == len(contexts)-1:
            prompt = (
                prompt_start +
                "".join(contexts) +
                prompt_end
            )
    return prompt





@app.route('/')
def index():
    return render_template('index.html')


def complete(prompt):
  response = co.generate(
                          model='c4ai-aya',
                          prompt=prompt,
                          max_tokens=3000,
                          temperature=0.4,
                          k=0,
                          stop_sequences=['\n\n'],
                          return_likelihoods='NONE'
                        )
  return response.generations[0].text.strip()

# Add more routes and functions as needed...
# Querying in Weaviate
def retrieve(query):
    # Embed the query using Cohere
    xq = co.embed(
        texts=[query],
        model='multilingual-22-12',
        truncate='NONE'
    ).embeddings

    # Search for similar objects in Weaviate
    result = client.query.builder().with_near_text('text', query).with_near_vector('embedding', xq[0]).build().execute()

    # Extract relevant information from the matches
    contexts = []
    for item in result['data']['Get']['BiologicalStrategy']:
        contexts.append(f"Text: {item['text']}")

    # Combine the information into formatted contexts
    formatted_contexts = "\n".join(contexts)

    return formatted_contexts

if __name__ == '__main__':
    app.run(debug=True)
