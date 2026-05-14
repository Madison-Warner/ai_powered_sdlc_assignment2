import pytest
import tempfile
import os
from app import app
from storage import Storage


@pytest.fixture
def client():
    """Create a test client for the Flask app."""
    # Create temporary storage
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_path = f.name

    # Override the storage path in app
    app.config['TESTING'] = True
    app.config['STORAGE_PATH'] = temp_path

    # Initialize storage
    storage = Storage(temp_path)

    # Reset cached instances
    if hasattr(app, '_quiz_engine'):
        delattr(app, '_quiz_engine')
    if hasattr(app, '_rag_retrieval'):
        delattr(app, '_rag_retrieval')
    if hasattr(app, '_storage'):
        delattr(app, '_storage')

    with app.test_client() as client:
        yield client

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestAppIntegration:
    def test_get_subjects_empty(self, client):
        """Test getting subjects when none exist."""
        response = client.get('/api/subjects')
        assert response.status_code == 200
        data = response.get_json()
        assert data == []

    def test_create_and_get_subject(self, client):
        """Test creating and retrieving a subject."""
        # Create subject
        response = client.post('/api/subjects', json={
            'name': 'Test Subject',
            'description': 'Test Description'
        })
        assert response.status_code == 201
        subject = response.get_json()
        assert subject['name'] == 'Test Subject'
        assert subject['description'] == 'Test Description'
        assert 'id' in subject

        # Get subjects
        response = client.get('/api/subjects')
        assert response.status_code == 200
        subjects = response.get_json()
        assert len(subjects) == 1
        assert subjects[0] == subject

    def test_create_topic(self, client):
        """Test creating a topic under a subject."""
        # Create subject first
        response = client.post('/api/subjects', json={
            'name': 'Subject',
            'description': 'Desc'
        })
        subject = response.get_json()

        # Create topic
        response = client.post('/api/topics', json={
            'subject_id': subject['id'],
            'name': 'Test Topic',
            'description': 'Topic Description'
        })
        assert response.status_code == 201
        topic = response.get_json()
        assert topic['name'] == 'Test Topic'
        assert topic['subject_id'] == subject['id']
        assert topic['weak_score'] == 0

    def test_create_flashcard(self, client):
        """Test creating a flashcard."""
        # Create subject and topic
        subject_resp = client.post('/api/subjects', json={'name': 'Subject', 'description': 'Desc'})
        subject = subject_resp.get_json()

        topic_resp = client.post('/api/topics', json={
            'subject_id': subject['id'],
            'name': 'Topic',
            'description': 'Desc'
        })
        topic = topic_resp.get_json()

        # Create flashcard
        response = client.post('/api/flashcards', json={
            'topic_id': topic['id'],
            'question': 'What is 2+2?',
            'answer': '4'
        })
        assert response.status_code == 201
        flashcard = response.get_json()
        assert flashcard['question'] == 'What is 2+2?'
        assert flashcard['answer'] == '4'

    def test_upload_study_material(self, client):
        """Test uploading study material."""
        # Create subject and topic
        subject_resp = client.post('/api/subjects', json={'name': 'Subject', 'description': 'Desc'})
        subject = subject_resp.get_json()

        topic_resp = client.post('/api/topics', json={
            'subject_id': subject['id'],
            'name': 'Topic',
            'description': 'Desc'
        })
        topic = topic_resp.get_json()

        # Upload material
        response = client.post('/api/study-materials', json={
            'topic_id': topic['id'],
            'filename': 'test.txt',
            'content': 'This is test content. It has multiple sentences.'
        })
        assert response.status_code == 201
        material = response.get_json()
        assert material['filename'] == 'test.txt'
        assert material['content'] == 'This is test content. It has multiple sentences.'

    def test_generate_quiz_insufficient_material(self, client):
        """Test generating quiz with insufficient material."""
        # Create subject and topic but no material
        subject_resp = client.post('/api/subjects', json={'name': 'Subject', 'description': 'Desc'})
        subject = subject_resp.get_json()

        client.post('/api/topics', json={
            'subject_id': subject['id'],
            'name': 'Topic',
            'description': 'Desc'
        })

        # Try to generate quiz
        response = client.post('/api/quizzes/generate', json={
            'subject_id': subject['id']
        })
        assert response.status_code == 400
        data = response.get_json()
        assert 'error' in data

    def test_full_quiz_workflow(self, client):
        """Test the complete quiz workflow: create subject/topic/material, generate quiz, submit answers."""
        # Create subject
        subject_resp = client.post('/api/subjects', json={'name': 'Math', 'description': 'Mathematics'})
        subject = subject_resp.get_json()

        # Create topic
        topic_resp = client.post('/api/topics', json={
            'subject_id': subject['id'],
            'name': 'Algebra',
            'description': 'Basic algebra'
        })
        topic = topic_resp.get_json()

        # Upload study material with enough content
        content = '. '.join([f'Statement {i} about algebra' for i in range(20)]) + '.'
        client.post('/api/study-materials', json={
            'topic_id': topic['id'],
            'filename': 'algebra.txt',
            'content': content
        })

        # Generate quiz
        quiz_resp = client.post('/api/quizzes/generate', json={
            'subject_id': subject['id']
        })
        assert quiz_resp.status_code == 200
        quiz = quiz_resp.get_json()
        assert len(quiz['questions']) == 15
        assert quiz['subject_id'] == subject['id']

        # Prepare answers (assume all correct for simplicity)
        answers = {}
        for q in quiz['questions']:
            answers[q['id']] = q['correct_answer']

        # Submit quiz
        submit_resp = client.post('/api/quizzes/submit', json={
            'quiz_id': quiz['id'],
            'answers': answers
        })
        assert submit_resp.status_code == 200
        result = submit_resp.get_json()
        assert result['score'] == 100.0
        assert result['correct_count'] == 15
        assert result['total_questions'] == 15

    def test_rag_retrieve(self, client):
        """Test RAG retrieval endpoint."""
        # Create subject, topic, material
        subject_resp = client.post('/api/subjects', json={'name': 'Science', 'description': 'Science'})
        subject = subject_resp.get_json()

        topic_resp = client.post('/api/topics', json={
            'subject_id': subject['id'],
            'name': 'Physics',
            'description': 'Physics basics'
        })
        topic = topic_resp.get_json()

        client.post('/api/study-materials', json={
            'topic_id': topic['id'],
            'filename': 'physics.txt',
            'content': 'Newton\'s laws govern motion. Gravity is a fundamental force.'
        })

        # Retrieve definitions
        response = client.post('/api/rag/retrieve', json={
            'topic_id': topic['id'],
            'query': 'laws',
            'limit': 2
        })
        assert response.status_code == 200
        results = response.get_json()
        assert len(results) == 1
        assert results[0]['filename'] == 'physics.txt'
        assert len(results[0]['definitions']) > 0

    def test_invalid_requests(self, client):
        """Test various invalid requests."""
        # Missing required fields
        response = client.post('/api/subjects', json={})
        assert response.status_code == 400

        response = client.post('/api/topics', json={'name': 'Topic'})
        assert response.status_code == 400

        response = client.post('/api/quizzes/generate', json={})
        assert response.status_code == 400

        response = client.post('/api/quizzes/submit', json={})
        assert response.status_code == 400

        response = client.post('/api/rag/retrieve', json={'query': 'test'})
        assert response.status_code == 400