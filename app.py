import os

from flask import Flask, jsonify, request, render_template, current_app
from storage import Storage
from quiz_engine import QuizEngine
from rag_retrieval import RAGRetrieval

app = Flask(__name__, static_folder="static", template_folder="templates")

def get_storage():
    """Get storage instance, using configured path if available."""
    storage_path = current_app.config.get('STORAGE_PATH') or os.environ.get('STORAGE_PATH')
    if storage_path:
        return Storage(storage_path)
    # Use default storage for production
    if not hasattr(app, '_storage'):
        app._storage = Storage()
    return app._storage

def get_quiz_engine():
    """Get quiz engine instance."""
    if not hasattr(app, '_quiz_engine'):
        app._quiz_engine = QuizEngine(get_storage())
    return app._quiz_engine

def get_rag_retrieval():
    """Get RAG retrieval instance."""
    if not hasattr(app, '_rag_retrieval'):
        app._rag_retrieval = RAGRetrieval(get_storage())
    return app._rag_retrieval

@app.route("/")
def index():
    return render_template("index.html")

@app.route("/api/subjects", methods=["GET"])
def get_subjects():
    return jsonify(get_storage().list_subjects())

@app.route("/api/subjects", methods=["POST"])
def create_subject():
    payload = request.json or {}
    name = payload.get("name")
    description = payload.get("description", "")
    if not name:
        return jsonify({"error": "Subject name is required."}), 400
    subject = get_storage().add_subject(name=name, description=description)
    return jsonify(subject), 201

@app.route("/api/subjects/<subject_id>", methods=["GET"])
def get_subject(subject_id):
    subject = get_storage().get_subject(subject_id)
    if subject is None:
        return jsonify({"error": "Subject not found."}), 404
    return jsonify(subject)

@app.route("/api/subjects/<subject_id>", methods=["PUT"])
def update_subject(subject_id):
    payload = request.json or {}
    name = payload.get("name")
    description = payload.get("description", "")
    if not name:
        return jsonify({"error": "Subject name is required."}), 400
    subject = get_storage().update_subject(subject_id, name=name, description=description)
    if subject is None:
        return jsonify({"error": "Subject not found."}), 404
    return jsonify(subject)

@app.route("/api/subjects/<subject_id>", methods=["DELETE"])
def delete_subject(subject_id):
    success = get_storage().delete_subject(subject_id)
    if not success:
        return jsonify({"error": "Subject not found."}), 404
    return jsonify({"message": "Subject deleted."})

@app.route("/api/subjects/<subject_id>/topics", methods=["GET"])
def get_subject_topics(subject_id):
    return jsonify(get_storage().list_topics(subject_id=subject_id))

@app.route("/api/subjects/<subject_id>/topics", methods=["POST"])
def create_topic(subject_id):
    payload = request.json or {}
    name = payload.get("name")
    description = payload.get("description", "")
    if not name:
        return jsonify({"error": "Topic name is required."}), 400
    topic = get_storage().add_topic(subject_id=subject_id, name=name, description=description)
    if topic is None:
        return jsonify({"error": "Subject not found."}), 404
    return jsonify(topic), 201

@app.route("/api/topics", methods=["GET"])
def list_topics():
    subject_id = request.args.get("subject_id")
    return jsonify(get_storage().list_topics(subject_id=subject_id) if subject_id else get_storage().list_topics())

@app.route("/api/topics", methods=["POST"])
def create_topic_global():
    payload = request.json or {}
    subject_id = payload.get("subject_id")
    name = payload.get("name")
    description = payload.get("description", "")
    if not subject_id or not name:
        return jsonify({"error": "subject_id and topic name are required."}), 400
    topic = get_storage().add_topic(subject_id, name=name, description=description)
    if topic is None:
        return jsonify({"error": "Subject not found."}), 404
    return jsonify(topic), 201

@app.route("/api/topics/<topic_id>", methods=["GET"])
def get_topic(topic_id):
    topic = get_storage().get_topic(topic_id)
    if topic is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(topic)

@app.route("/api/topics/<topic_id>", methods=["PUT"])
def update_topic(topic_id):
    payload = request.json or {}
    name = payload.get("name")
    description = payload.get("description", "")
    if not name:
        return jsonify({"error": "Topic name is required."}), 400
    topic = get_storage().update_topic(topic_id, name=name, description=description)
    if topic is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(topic)

@app.route("/api/topics/<topic_id>", methods=["DELETE"])
def delete_topic(topic_id):
    success = get_storage().delete_topic(topic_id)
    if not success:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify({"message": "Topic deleted."})

@app.route("/api/topics/<topic_id>/flashcards", methods=["GET"])
def get_flashcards(topic_id):
    return jsonify(get_storage().list_flashcards(topic_id=topic_id))

@app.route("/api/flashcards", methods=["GET"])
def list_flashcards():
    topic_id = request.args.get("topic_id")
    return jsonify(get_storage().list_flashcards(topic_id=topic_id) if topic_id else get_storage().list_flashcards())

@app.route("/api/topics/<topic_id>/flashcards", methods=["POST"])
def create_flashcard(topic_id):
    payload = request.json or {}
    question = payload.get("question")
    answer = payload.get("answer")
    if not question or not answer:
        return jsonify({"error": "Flashcard question and answer are required."}), 400
    flashcard = get_storage().add_flashcard(topic_id=topic_id, question=question, answer=answer)
    if flashcard is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(flashcard), 201

@app.route("/api/flashcards", methods=["POST"])
def create_flashcard_global():
    payload = request.json or {}
    topic_id = payload.get("topic_id")
    question = payload.get("question")
    answer = payload.get("answer")
    if not topic_id or not question or not answer:
        return jsonify({"error": "topic_id, question, and answer are required."}), 400
    flashcard = get_storage().add_flashcard(topic_id=topic_id, question=question, answer=answer)
    if flashcard is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(flashcard), 201

@app.route("/api/flashcards/<flashcard_id>", methods=["GET"])
def get_flashcard(flashcard_id):
    flashcard = get_storage().get_flashcard(flashcard_id)
    if flashcard is None:
        return jsonify({"error": "Flashcard not found."}), 404
    return jsonify(flashcard)

@app.route("/api/flashcards/<flashcard_id>", methods=["PUT"])
def update_flashcard(flashcard_id):
    payload = request.json or {}
    question = payload.get("question")
    answer = payload.get("answer")
    if not question or not answer:
        return jsonify({"error": "Flashcard question and answer are required."}), 400
    flashcard = get_storage().update_flashcard(flashcard_id, question=question, answer=answer)
    if flashcard is None:
        return jsonify({"error": "Flashcard not found."}), 404
    return jsonify(flashcard)

@app.route("/api/flashcards/<flashcard_id>", methods=["DELETE"])
def delete_flashcard(flashcard_id):
    success = get_storage().delete_flashcard(flashcard_id)
    if not success:
        return jsonify({"error": "Flashcard not found."}), 404
    return jsonify({"message": "Flashcard deleted."})

@app.route("/api/study-material", methods=["GET"])
def list_study_material():
    topic_id = request.args.get("topic_id")
    return jsonify(get_storage().list_study_material(topic_id=topic_id) if topic_id else get_storage().list_study_material())

@app.route("/api/study-materials", methods=["GET"])
def list_study_materials():
    topic_id = request.args.get("topic_id")
    return jsonify(get_storage().list_study_material(topic_id=topic_id) if topic_id else get_storage().list_study_material())

@app.route("/api/study-material/<material_id>", methods=["GET"])
def get_study_material(material_id):
    material = get_storage().get_study_material(material_id)
    if material is None:
        return jsonify({"error": "Study material not found."}), 404
    return jsonify(material)

@app.route("/api/study-material/<material_id>", methods=["DELETE"])
def delete_study_material(material_id):
    success = get_storage().delete_study_material(material_id)
    if not success:
        return jsonify({"error": "Study material not found."}), 404
    return jsonify({"message": "Study material deleted."})

@app.route("/api/study-materials", methods=["POST"])
def upload_study_material_alias():
    payload = request.json or {}
    topic_id = payload.get("topic_id")
    filename = payload.get("filename")
    content = payload.get("content")
    if not topic_id or not filename or not content:
        return jsonify({"error": "topic_id, filename, and content are required."}), 400
    material = get_storage().add_study_material(topic_id=topic_id, filename=filename, content=content)
    if material is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(material), 201

@app.route("/api/study-material", methods=["POST"])
def upload_study_material():
    payload = request.json or {}
    topic_id = payload.get("topic_id")
    filename = payload.get("filename")
    content = payload.get("content")
    if not topic_id or not filename or not content:
        return jsonify({"error": "topic_id, filename, and content are required."}), 400
    material = get_storage().add_study_material(topic_id=topic_id, filename=filename, content=content)
    if material is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(material), 201

@app.route("/api/quiz-results", methods=["GET"])
def list_quiz_results():
    topic_id = request.args.get("topic_id")
    return jsonify(get_storage().list_quiz_results(topic_id=topic_id) if topic_id else get_storage().list_quiz_results())

@app.route("/api/quiz-results", methods=["POST"])
def create_quiz_result():
    payload = request.json or {}
    topic_id = payload.get("topic_id")
    score = payload.get("score")
    details = payload.get("details", {})
    if not topic_id or score is None:
        return jsonify({"error": "topic_id and score are required."}), 400
    quiz_result = get_storage().add_quiz_result(topic_id=topic_id, score=score, details=details)
    if quiz_result is None:
        return jsonify({"error": "Topic not found."}), 404
    return jsonify(quiz_result), 201

@app.route("/api/quizzes/generate", methods=["POST"])
def generate_quiz():
    payload = request.json or {}
    subject_id = payload.get("subject_id")
    if not subject_id:
        return jsonify({"error": "subject_id is required."}), 400
    quiz = get_quiz_engine().generate_quiz(subject_id)
    if quiz is None:
        return jsonify({"error": "Not enough study material to generate quiz."}), 400
    return jsonify(quiz)

@app.route("/api/quizzes/submit", methods=["POST"])
def submit_quiz():
    payload = request.json or {}
    quiz_id = payload.get("quiz_id")
    answers = payload.get("answers", {})
    if not quiz_id or not answers:
        return jsonify({"error": "quiz_id and answers are required."}), 400
    result = get_quiz_engine().grade_quiz(quiz_id, answers)
    if "error" in result:
        return jsonify(result), 400
    # Save the quiz result
    quiz = get_storage().get_quiz(quiz_id)
    subject_id = quiz["subject_id"] if quiz else None
    quiz_result = get_storage().add_quiz_result(topic_id=None, score=result["score"], details=result)
    return jsonify(result)

@app.route("/api/rag/retrieve", methods=["POST"])
def retrieve_definitions():
    payload = request.json or {}
    topic_id = payload.get("topic_id")
    query = payload.get("query")
    limit = payload.get("limit", 5)
    if not topic_id or not query:
        return jsonify({"error": "topic_id and query are required."}), 400
    results = get_rag_retrieval().retrieve_definitions(topic_id, query, limit)
    return jsonify(results)

@app.errorhandler(404)
def not_found(error):
    return jsonify({"error": "Resource not found."}), 404

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    debug_flag = os.environ.get('FLASK_DEBUG', '0') == '1' or os.environ.get('FLASK_ENV') == 'development'
    app.run(host='0.0.0.0', port=port, debug=debug_flag)
