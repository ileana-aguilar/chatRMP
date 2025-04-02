from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from pinecone import Pinecone  
import openai
import os
import re
from dotenv import load_dotenv
import spacy


nlp = spacy.load("en_core_web_sm")


load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")


if not PINECONE_API_KEY or not OPENAI_API_KEY:
    raise ValueError("Missing API keys! Check your .env file.")


pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index("rate-my-professors")
openai.api_key = OPENAI_API_KEY

app = FastAPI()


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class QueryRequest(BaseModel):
    query: str
    department: str | None = None

def summarize_reviews(name, reviews):
    if not reviews:
        return "No reviews available for this professor."

    summarized_review_text = " ".join(reviews[:3])
    response = openai.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "Summarize professor reviews into a short explanation of their strengths and weaknesses."},
            {"role": "user", "content": f"Summarize the following reviews for {name}: {summarized_review_text}"}
        ]
    )
    return response.choices[0].message.content

def extract_department(query_text, explicit_department):
    department_aliases = {
        "math": "Mathematics",
        "cs": "Computer Science",
        "comp sci": "Computer Science",
        "bio": "Biology",
        "chem": "Chemistry",
        "phy": "Physics",
    }

    known_departments = ["Mathematics", "English", "Computer Science", "History", "Physics"]

  
    if explicit_department:
        dept = explicit_department.lower().strip()
        return department_aliases.get(dept, dept.title())

   
    for alias, full_name in department_aliases.items():
        if alias in query_text:
            return full_name

    for dept in known_departments:
        if dept.lower() in query_text:
            return dept

    
    match = re.search(r"(?:in|of|from)\s+([\w\s]+)", query_text)
    if match:
        dept_raw = match.group(1).strip().lower()
        return department_aliases.get(dept_raw, dept_raw.title())

    return None



def handle_professor_name_query(query_text):
    match = re.search(r"professor ([\w\s'\-]+)", query_text, re.IGNORECASE)
    professor_name = match.group(1).strip().title() if match else None

    if not professor_name:
        return {"response": "I'm here to help with professor-related queries. Try asking about a department or a specific professor!"}

    professor_name = re.sub(r"\bDe\b", "de", professor_name)
    print(f"📌 Searching for professor: {professor_name}")

    results = index.query(
        vector=[0] * 1536,
        filter={"name": {"$eq": professor_name}},
        top_k=10,
        include_metadata=True
    )

    professors = results.get("matches", [])
    if not professors:
        return {"response": f"I couldn't find a professor named {professor_name}. Try another query!"}

    if len(professors) > 1:
        options = [f"{p['metadata']['name']} from {p['metadata']['department']}" for p in professors]
        return {"response": f"Multiple professors found:\n" + "\n".join(options)}

    prof = professors[0]["metadata"]
    summary = summarize_reviews(prof["name"], prof.get("reviews", []))
    return {"response": f"Professor {prof['name']} from {prof['department']}\nRating: {prof['rating']}\n{summary}"}

def list_professors_by_department(department):
    if not department:
        return {"response": "Please specify a department to list professors."}

    results = index.query(
        vector=[0] * 1536,
        filter={"department": {"$eq": department}},
        top_k=100,
        include_metadata=True
    )

    professors = [match["metadata"].get("name", "Unknown") for match in results.get("matches", [])]
    if not professors:
        return {"response": f"No professors found in the {department} department."}

    formatted = "\n".join([f"{i+1}. {name}" for i, name in enumerate(professors)])
    return {"response": f"Here are the professors in the {department} department:\n{formatted}"}

def find_best_professor_in_department(query_text, department):
    if not department:
        return {"response": "Please specify a department to find the best professor."}

    query_embedding = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[query_text]
    ).data[0].embedding

    results = index.query(
        vector=query_embedding,
        filter={"department": {"$eq": department}},
        top_k=1,
        include_metadata=True
    )

    matches = results.get("matches", [])
    if not matches:
        return {"response": f"No professors found in the {department} department."}

    prof = matches[0]["metadata"]
    summary = summarize_reviews(prof["name"], prof.get("reviews", []))
    return {"response": f"Best professor in {department}:\n{prof['name']}\nRating: {prof['rating']}\n{summary}"}


def find_worst_professor_in_department(query_text, department):
    if not department:
        return {"response": "Please specify a department to find the worst professor."}

    query_embedding = openai.embeddings.create(
        model="text-embedding-ada-002",
        input=[query_text]
    ).data[0].embedding

    results = index.query(
        vector=query_embedding,
        filter={"department": {"$eq": department}},
        top_k=10,
        include_metadata=True
    )

    matches = results.get("matches", [])
    if not matches:
        return {"response": f"No professors found in the {department} department."}

    
    worst_prof = sorted(matches, key=lambda x: x["metadata"].get("rating", 0))[0]["metadata"]
    summary = summarize_reviews(worst_prof["name"], worst_prof.get("reviews", []))
    return {"response": f"Worst professor in {department}:\n{worst_prof['name']}\nRating: {worst_prof['rating']}\n{summary}"}


@app.post("/search_professors")
def search_professors(request: QueryRequest):
    query_text = request.query.lower().strip()
    department = extract_department(query_text, request.department)
    print("Received request:", request.dict())  
    print("📌 Extracted department:", department)

    if "best" in query_text:
        return find_best_professor_in_department(query_text, department)
    
    if "worst" in query_text:
        return find_worst_professor_in_department(query_text, department)

    if "list" in query_text or "show" in query_text:
        return list_professors_by_department(department)

    return handle_professor_name_query(query_text)
