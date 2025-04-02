from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({"message": "Welcome to the Rate My Professor Chatbot API!"})

@app.route("/query", methods=["GET"])
def query_professor():
    professor = request.args.get("professor")

    if not professor:
        return jsonify({"error": "Please provide a professor name"}), 400

    # Placeholder response (We'll replace this with Pinecone AI later)
    response = f"Professor {professor} has a rating of 4.5 and is known for a fair grading style."

    return jsonify({"response": response})

if __name__ == "__main__":
    app.run(debug=True, port=5000)
