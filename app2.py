from flask import Flask, render_template, request, jsonify
import os
import cohere
import weaviate
import pandas as pd

app = Flask(__name__)

# Setup API keys
cohere_api_key = os.getenv('cohere_api_key')
weaviate_api_key = os.getenv('weaviate_api_key')
weaviate_url = os.getenv('weaviate_url')

# Connect to Cohere
co = cohere.Client(cohere_api_key)

# Connect to a Weaviate Cluster instance
weaviate_client = weaviate.connect_to_wcs(
    cluster_url=weaviate_url,
    auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key))

# Load data
raw_df = pd.read_csv("biological-strategies.csv", index_col=0)
hq_df = raw_df

# Extract texts for embedding
texts = hq_df["0"].tolist()

# Embedding documents in Weaviate
class_name = "BiologicalStrategy"
for i, text in enumerate(texts):
    obj = {
        "text": text
    }
    weaviate_client.create_object(class_name, obj)

# Querying in Weaviate with Cohere semantic search
def retrieve(query):
    # Embed the query using Cohere
    xq = co.embed(
        texts=[query],
        model='multilingual-22-12',
        truncate='NONE'
    ).embeddings

    # Search for similar objects in Weaviate
    result = weaviate_client.query.builder().with_near_vector('embedding', xq[0]).build().execute()

    # Extract relevant information from the matches
    contexts = []
    for item in result['data']['Get'][class_name]:
        contexts.append(item['text'])

    return contexts

# Index route
@app.route('/')
def index():
    return render_template('index.html')

# Route for processing user input
@app.route('/process', methods=['POST'])
def process():
    query = request.form['query']
    if not query:
        return jsonify({'error': 'Empty query'})

    # Retrieve similar documents using Cohere semantic search
    similar_contexts = retrieve(query)

    return jsonify({'similar_contexts': similar_contexts})

if __name__ == '__main__':
    app.run(debug=True)
