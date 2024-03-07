from flask import Flask, render_template, request
import weaviate
from weaviate.embedded import EmbeddedOptions
import cohere
import os
import random
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


response = co.embed(texts=texts, model='multilingual-22-12').embeddings
embeds = np.array(response)

raw_df = pd.read_csv("biological-strategies.csv", index_col=0)
print(raw_df.shape)
hq_df = raw_df
hq_df.head()

# Embed the documents and store in index
search_index = AnnoyIndex(embeds.shape[1], 'angular')
# Add all the vectors to the search index
for i in range(len(embeds)):
    search_index.add_item(i, embeds[i])

search_index.build(100) # 10 trees
search_index.save('quran_index.ann')

@app.route('/')
def index():
    return render_template('index.html')




# Add more routes and functions as needed...

if __name__ == '__main__':
    app.run(debug=True)
