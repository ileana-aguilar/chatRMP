import os
import pinecone
from openai import OpenAI
from dotenv import load_dotenv


load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

pc = pinecone.Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("rate-my-professors")  


openai_client = OpenAI(api_key=OPENAI_API_KEY)

def generate_embedding(text):
    response = openai_client.embeddings.create(
        model="text-embedding-ada-002",
        input=text
    )
    return response.data[0].embedding

def search_professors(query, department_filter="Computer Science", top_k=10):
    query_embedding = generate_embedding(query)
    
    
    results = index.query(vector=query_embedding, top_k=top_k, include_metadata=True)

    
    filtered_results = [
        match for match in results['matches']
        if match['metadata'].get('department', '').lower() == department_filter.lower()
    ]

    
    if not filtered_results:
        print(f"🚨 No professors found for department: {department_filter}")
        return

    for match in filtered_results:
        metadata = match['metadata']
        print(f"🎓 Professor: {metadata['name']} ({metadata['department']})")
        print(f"⭐ Rating: {metadata.get('rating', 'N/A')}")
        print(f"📖 Reviews: {', '.join(metadata['reviews'][:2])}...\n")
    
    return filtered_results


if __name__ == "__main__":
    search_query = input("Ask about professors: ")
    department = input("Enter department to filter by (e.g., Computer Science): ")
    search_professors(search_query, department)