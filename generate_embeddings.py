import weaviate
from weaviate.embedded import EmbeddedOptions
import cohere
import os
import pandas as pd
import numpy as np

# Setup API keys
cohere_api_key = os.getenv('cohere_api_key')
weaviate_api_key = os.getenv('weaviate_api_key')
weaviate_url = os.getenv('weaviate_url')

# Connect to Cohere
co = cohere.Client(cohere_api_key)

# Connect to Weaviate
client = weaviate.connect_to_wcs(
    cluster_url=weaviate_url,
    auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key))


def create_class():
    # Define a data collection (class) in Weaviate
    class_config = {
        "name": "BiologicalStrategiesInnovations",
        "vectorizer_config": weaviate.classes.config.Configure.Vectorizer.text2vec_cohere(),
        "generative_config": weaviate.classes.config.Configure.Generative.cohere()
    }
    class_object = client.collections.create(**class_config)
    return class_object


def process_file(file_path):
    # Extract filename without extension
    filename = os.path.splitext(os.path.basename(file_path))[0]

    # Load data
    raw_df = pd.read_csv(file_path)

    # Assuming 'name' column contains text data
    texts = raw_df['name'].tolist()

    # Embed text data using Cohere
    response = co.embed(
        texts=texts, 
        model='multilingual-22-12').embeddings

    # Convert embedding response to numpy array
    embeds = np.array(response)
    
    # Store all embeddings in a single list
    all_embeddings = []

    for i, (text, embedding) in enumerate(zip(texts, embeds)):
        all_embeddings.append(embedding)

    # Convert the list of embeddings into a single numpy array
    all_embeddings_array = np.array(all_embeddings)

    # Save the numpy array containing all embeddings to a single file
    np.save(f"{filename}_embeddings.npy", all_embeddings_array)

    #objects = []
    #for text, embedding in zip(texts, embeds):
    #    properties = {'text': text, 'embedding': embedding.tolist()}
    #    objects.append(properties)

    #client.collections.get('BiologicalStrategiesInnovations').data.insert_many(objects)

# Process embeddings for each CSV file
#process_file("biological-strategies.csv")
process_file("biological-innovations.csv")
