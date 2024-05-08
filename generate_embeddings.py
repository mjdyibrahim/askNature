import weaviate
from weaviate.embedded import EmbeddedOptions
import cohere
import os
from dotenv import load_dotenv
import pandas as pd
import numpy as np
from tqdm import tqdm

load_dotenv()

# Define the path to the marker file
marker_file_path = "weaviate_class_created.txt"

# Setup API keys
cohere_api_key = os.getenv("CO_API_KEY")
weaviate_api_key = os.getenv("WEAVIATE_API_KEY")
weaviate_url = os.getenv("WEAVIATE_URL")

# Connect to Cohere
co = cohere.Client(cohere_api_key)

# Connect to Weaviate
client = weaviate.connect_to_wcs(
    cluster_url=weaviate.url(weaviate_url),
    auth_credentials=weaviate.auth.AuthApiKey(weaviate_api_key),
    additional_config=weaviate.config.AdditionalConfig(timeout=(60, 120))  # Values in seconds
)


def create_weaviate_class():
        # Check if the marker file exists
        if not os.path.exists(marker_file_path):
            # Define a data collection (class) in Weaviate
            class_config = {
                        "name": "BiologicalStrategiesInnovations",
                        "vectorizer_config": weaviate.classes.config.Configure.Vectorizer.text2vec_cohere(),
                        "generative_config": weaviate.classes.config.Configure.Generative.cohere(),
                    }
        class_object = client.collections.create(**class_config)

        # Create the marker file
        with open(marker_file_path, "w") as f:
                    f.write("Weaviate class created")

                return class_object
            else:
                print("Weaviate class already created.")
                return None
def process_file(file_path):
    # Extract filename without extension
filename = os.path.splitext(os.path.basename(file_path))[0]

    # Load data
raw_df = pd.read_csv(file_path)

    texts = raw_df["name"].tolist()

    # Embed text data using Cohere
embeds = co.embed(texts=texts, model="multilingual-22-12")

    # Save embeddings to a single numpy array file
all_embeddings_array = np.array([embed.vector for embed in embeds])
    np.save(f"{filename}_embeddings.npy", all_embeddings_array)

    # Process embeddings for each row of the CSV file
for text, embedding in tqdm(zip(texts, embeds)):
        # Create a Weaviate object with the text and embedding
object_data = {
            "text": text,
            "embedding": embedding.vector.tolist()
        }

        # Add the object to the Weaviate collection
client.collections.get("BiologicalStrategiesInnovations").data.insert_one(object_data)


def main():