import os
import json
import sys
import pandas as pd
from pinecone import Pinecone
from openai import OpenAI
from dotenv import load_dotenv
from pinecone import ServerlessSpec

os.environ.pop("PINECONE_API_KEY", None)
load_dotenv()


PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

pc = Pinecone(api_key=PINECONE_API_KEY)


INDEX_NAME = "rate-my-professors"


if INDEX_NAME not in pc.list_indexes().names():
    pc.create_index(
        name=INDEX_NAME,
        dimension=1536,  
        metric="cosine",
        spec=ServerlessSpec(
            cloud="aws",  
            region="us-east-1" 
        )
    )


index = pc.Index(INDEX_NAME)

openai_client = OpenAI(api_key=OPENAI_API_KEY)


professors_df = pd.read_csv("professors_queens_college.csv")
reviews_df = pd.read_csv("professors_reviews.csv")


merged_df = reviews_df.merge(professors_df, on="Professor ID", how="left")


def generate_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding  


batch_size = 10  
vectors = []

for _, row in merged_df.iterrows():
    professor_id = str(row["Professor ID"])  
    professor_name = row["Professor Name"]
    department = row["Department"]
    rating = row.get("Rating", "N/A")

 
    department = "" if pd.isna(department) else department
    rating = "" if pd.isna(rating) else rating


    reviews = merged_df[merged_df["Professor ID"] == row["Professor ID"]]["Review"].dropna().tolist()[:3]  # Limit to 3 reviews
    review_text = " ".join(reviews)


    embedding = generate_embedding(f"{professor_name} {department} {review_text}")


    assert isinstance(embedding, list), f"Embedding should be a list, but got {type(embedding)}"
    assert all(isinstance(x, float) for x in embedding), "Embedding values must be floats"


    metadata = {
        "name": professor_name,
        "department": department,
        "rating": rating,
        "reviews": reviews
    }

    vectors.append((professor_id, embedding, metadata))


    if len(vectors) >= batch_size:
        request_size = sys.getsizeof(json.dumps(vectors))
        print(f"🔍 Request size before upsert: {request_size} bytes")

        if request_size < 2097152:
            index.upsert(vectors)
        else:
            print("⚠️ Skipping batch: Exceeds 2MB limit!")
        
        vectors = []


if vectors:
    request_size = sys.getsizeof(json.dumps(vectors))
    print(f"🔍 Final request size before upsert: {request_size} bytes")
    
    if request_size < 2097152:
        index.upsert(vectors)
    else:
        print("⚠️ Skipping last batch: Exceeds 2MB limit!")

print(f"✅ Successfully stored {len(merged_df)} professors with reviews in Pinecone!")