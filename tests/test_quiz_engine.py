import pytest
from storage import Storage
from quiz_engine import QuizEngine
import tempfile
import os


@pytest.fixture
def temp_storage():
    """Create a temporary storage instance for testing."""
    with tempfile.NamedTemporaryFile(delete=False, suffix='.json') as f:
        temp_path = f.name

    storage = Storage(temp_path)
    yield storage

    # Cleanup
    if os.path.exists(temp_path):
        os.unlink(temp_path)


@pytest.fixture
def quiz_engine(temp_storage):
    """Create a QuizEngine instance with temp storage."""
    return QuizEngine(temp_storage)


class TestQuizEngine:
    def test_generate_quiz_no_subjects(self, quiz_engine):
        """Test generating quiz with no subjects."""
        result = quiz_engine.generate_quiz("nonexistent")
        assert result is None

    def test_generate_quiz_no_topics(self, temp_storage, quiz_engine):
        """Test generating quiz with subject but no topics."""
        subject = temp_storage.add_subject("Subject", "Desc")
        result = quiz_engine.generate_quiz(subject['id'])
        assert result is None

    def test_generate_quiz_insufficient_material(self, temp_storage, quiz_engine):
        """Test generating quiz with topics but insufficient study material."""
        subject = temp_storage.add_subject("Subject", "Desc")
        temp_storage.add_topic(subject['id'], "Topic", "Desc")
        # No study material added

        result = quiz_engine.generate_quiz(subject['id'])
        assert result is None

    def test_generate_quiz_success(self, temp_storage, quiz_engine):
        """Test successful quiz generation."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")
        # Add enough study material
        for i in range(20):  # More than 15 sentences
            temp_storage.add_study_material(topic['id'], f"file{i}.txt", f"This is sentence {i}. Another sentence here.")

        result = quiz_engine.generate_quiz(subject['id'])
        assert result is not None
        assert result['subject_id'] == subject['id']
        assert len(result['questions']) == 15

        # Check questions have required fields
        for q in result['questions']:
            assert 'id' in q
            assert 'type' in q
            assert 'question' in q
            assert 'options' in q
            assert 'correct_answer' in q
            assert 'topic_id' in q

    def test_weighted_sample(self, quiz_engine):
        """Test the weighted sampling method."""
        items = [
            {"id": 1, "weight": 1},
            {"id": 2, "weight": 10},
            {"id": 3, "weight": 1}
        ]

        # Sample multiple times to check weighting
        samples = []
        for _ in range(100):
            sample = quiz_engine._weighted_sample_without_replacement(items.copy(), 2)
            samples.extend(sample)

        # Item 2 should appear more often due to higher weight
        count_2 = sum(1 for s in samples if s['id'] == 2)
        count_1 = sum(1 for s in samples if s['id'] == 1)
        count_3 = sum(1 for s in samples if s['id'] == 3)

        assert count_2 > count_1
        assert count_2 > count_3

    def test_grade_quiz_not_found(self, quiz_engine):
        """Test grading a non-existent quiz."""
        result = quiz_engine.grade_quiz("nonexistent", {})
        assert result == {"error": "Quiz not found"}

    def test_grade_quiz_success(self, temp_storage, quiz_engine):
        """Test successful quiz grading."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic1 = temp_storage.add_topic(subject['id'], "Topic 1", "Desc")
        topic2 = temp_storage.add_topic(subject['id'], "Topic 2", "Desc")

        questions = [
            {"id": "q1", "question": "Q1?", "options": ["A", "B"], "correct_answer": "A", "topic_id": topic1['id']},
            {"id": "q2", "question": "Q2?", "options": ["C", "D"], "correct_answer": "C", "topic_id": topic2['id']},
        ]
        quiz = temp_storage.add_quiz(subject['id'], questions)

        # Submit answers: one correct, one incorrect
        answers = {"q1": "A", "q2": "D"}

        result = quiz_engine.grade_quiz(quiz['id'], answers)
        assert "error" not in result
        assert result['score'] == 50.0  # 1 out of 2 correct
        assert result['correct_count'] == 1
        assert result['total_questions'] == 2
        assert len(result['feedback']) == 2

        # Check weak scores updated
        updated_topic1 = temp_storage.get_topic(topic1['id'])
        updated_topic2 = temp_storage.get_topic(topic2['id'])
        assert updated_topic1['weak_score'] == 0  # Correct answer, score decreased
        assert updated_topic2['weak_score'] == 1  # Incorrect answer, score increased

    def test_generate_multiple_choice_from_material(self, temp_storage, quiz_engine):
        """Test generating multiple choice question from material."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        item = {
            "sentence": "This is a test sentence.",
            "topic_id": topic['id'],
            "material_id": "mat1"
        }

        question = quiz_engine._generate_multiple_choice_from_material(item)
        assert question['question'] == "Which of the following statements is correct?"
        assert question['correct_answer'] == "This is a test sentence."
        assert len(question['options']) == 4  # correct + 3 distractors
        assert question['correct_answer'] in question['options']
        assert question['topic_id'] == topic['id']

    def test_generate_true_false_from_material(self, temp_storage, quiz_engine):
        """Test generating true/false question from material."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        item = {
            "sentence": "This is a test sentence.",
            "topic_id": topic['id'],
            "material_id": "mat1"
        }

        question = quiz_engine._generate_true_false_from_material(item)
        assert question['question'] == "True or False: This is a test sentence."
        assert question['correct_answer'] == "True"
        assert question['options'] == ["True", "False"]
        assert question['topic_id'] == topic['id']