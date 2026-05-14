import json
import os
import tempfile
import pytest
from storage import Storage, new_id, timestamp


@pytest.fixture
def temp_storage():
    """Create a temporary storage instance for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json', mode='w') as f:
        temp_path = f.name
        # Write empty JSON to ensure it's valid
        json.dump({}, f)

    storage = Storage(temp_path)
    yield storage

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


class TestStorage:
    def test_initialization(self, temp_storage):
        """Test storage initializes with default schema."""
        assert 'subjects' in temp_storage.data
        assert 'topics' in temp_storage.data
        assert 'flashcards' in temp_storage.data
        assert 'study_material' in temp_storage.data
        assert 'quizzes' in temp_storage.data
        assert 'quiz_results' in temp_storage.data
        assert 'weak_topics' in temp_storage.data

    def test_add_and_get_subject(self, temp_storage):
        """Test adding and retrieving a subject."""
        subject = temp_storage.add_subject("Test Subject", "Description")
        assert subject is not None
        assert subject['name'] == "Test Subject"
        assert subject['description'] == "Description"

        retrieved = temp_storage.get_subject(subject['id'])
        assert retrieved == subject

    def test_list_subjects(self, temp_storage):
        """Test listing subjects."""
        temp_storage.add_subject("Subject 1", "Desc 1")
        temp_storage.add_subject("Subject 2", "Desc 2")

        subjects = temp_storage.list_subjects()
        assert len(subjects) == 2
        assert subjects[0]['name'] == "Subject 1"
        assert subjects[1]['name'] == "Subject 2"

    def test_delete_subject_cascades(self, temp_storage):
        """Test deleting a subject cascades to topics and flashcards."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")
        flashcard = temp_storage.add_flashcard(topic['id'], "Q", "A")

        # Delete subject
        result = temp_storage.delete_subject(subject['id'])
        assert result is True

        # Check cascades
        assert temp_storage.get_subject(subject['id']) is None
        assert temp_storage.get_topic(topic['id']) is None
        assert temp_storage.get_flashcard(flashcard['id']) is None

    def test_add_and_get_topic(self, temp_storage):
        """Test adding and retrieving a topic."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Description")

        assert topic is not None
        assert topic['name'] == "Topic"
        assert topic['subject_id'] == subject['id']
        assert topic['weak_score'] == 0

        retrieved = temp_storage.get_topic(topic['id'])
        assert retrieved == topic

    def test_list_topics_by_subject(self, temp_storage):
        """Test listing topics for a specific subject."""
        subject1 = temp_storage.add_subject("Subject 1", "Desc")
        subject2 = temp_storage.add_subject("Subject 2", "Desc")

        temp_storage.add_topic(subject1['id'], "Topic 1", "Desc")
        temp_storage.add_topic(subject1['id'], "Topic 2", "Desc")
        temp_storage.add_topic(subject2['id'], "Topic 3", "Desc")

        topics = temp_storage.list_topics(subject_id=subject1['id'])
        assert len(topics) == 2
        assert all(t['subject_id'] == subject1['id'] for t in topics)

    def test_set_weak_score(self, temp_storage):
        """Test setting weak score on a topic."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        updated = temp_storage.set_weak_score(topic['id'], 5)
        assert updated is not None
        assert updated['weak_score'] == 5

        retrieved = temp_storage.get_topic(topic['id'])
        assert retrieved['weak_score'] == 5

    def test_add_and_get_flashcard(self, temp_storage):
        """Test adding and retrieving a flashcard."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")
        flashcard = temp_storage.add_flashcard(topic['id'], "Question", "Answer")

        assert flashcard is not None
        assert flashcard['question'] == "Question"
        assert flashcard['answer'] == "Answer"
        assert flashcard['topic_id'] == topic['id']

        retrieved = temp_storage.get_flashcard(flashcard['id'])
        assert retrieved == flashcard

    def test_add_and_get_study_material(self, temp_storage):
        """Test adding and retrieving study material."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")
        material = temp_storage.add_study_material(topic['id'], "file.txt", "Content here")

        assert material is not None
        assert material['filename'] == "file.txt"
        assert material['content'] == "Content here"
        assert material['topic_id'] == topic['id']

        retrieved = temp_storage.get_study_material(material['id'])
        assert retrieved == material

    def test_list_study_material_by_topic(self, temp_storage):
        """Test listing study material for a topic."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic1 = temp_storage.add_topic(subject['id'], "Topic 1", "Desc")
        topic2 = temp_storage.add_topic(subject['id'], "Topic 2", "Desc")

        temp_storage.add_study_material(topic1['id'], "file1.txt", "Content 1")
        temp_storage.add_study_material(topic1['id'], "file2.txt", "Content 2")
        temp_storage.add_study_material(topic2['id'], "file3.txt", "Content 3")

        materials = temp_storage.list_study_material(topic_id=topic1['id'])
        assert len(materials) == 2
        assert all(m['topic_id'] == topic1['id'] for m in materials)

    def test_add_quiz(self, temp_storage):
        """Test adding a quiz."""
        subject = temp_storage.add_subject("Subject", "Desc")
        questions = [{"id": "q1", "question": "Q?", "options": ["A", "B"], "correct_answer": "A", "topic_id": "t1"}]
        quiz = temp_storage.add_quiz(subject['id'], questions)

        assert quiz is not None
        assert quiz['subject_id'] == subject['id']
        assert quiz['questions'] == questions

        retrieved = temp_storage.get_quiz(quiz['id'])
        assert retrieved == quiz

    def test_add_quiz_result(self, temp_storage):
        """Test adding a quiz result."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        result = temp_storage.add_quiz_result(topic_id=topic['id'], score=85.0, details={"feedback": []})

        assert result is not None
        assert result['topic_id'] == topic['id']
        assert result['score'] == 85.0

        results = temp_storage.list_quiz_results(topic_id=topic['id'])
        assert len(results) == 1
        assert results[0] == result