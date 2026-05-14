import pytest
from storage import Storage
from rag_retrieval import RAGRetrieval
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
def rag_retrieval(temp_storage):
    """Create a RAGRetrieval instance with temp storage."""
    return RAGRetrieval(temp_storage)


class TestRAGRetrieval:
    def test_retrieve_definitions_no_material(self, temp_storage, rag_retrieval):
        """Test retrieving definitions with no study material."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        results = rag_retrieval.retrieve_definitions(topic['id'], "test query")
        assert results == []

    def test_retrieve_definitions_with_material(self, temp_storage, rag_retrieval):
        """Test retrieving definitions with study material."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        # Add study material with content
        content = "Python is a programming language. It is used for web development. Machine learning uses Python extensively."
        temp_storage.add_study_material(topic['id'], "python.txt", content)

        # Query for "Python"
        results = rag_retrieval.retrieve_definitions(topic['id'], "Python", limit=2)
        assert len(results) == 1  # One material
        assert results[0]['filename'] == "python.txt"
        assert len(results[0]['definitions']) == 2  # Limited to 2

        # Check that relevant sentences are returned
        definitions = results[0]['definitions']
        assert any("Python" in sent for sent in definitions)

    def test_retrieve_definitions_multiple_materials(self, temp_storage, rag_retrieval):
        """Test retrieving from multiple study materials."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        # Add multiple materials
        content1 = "Flask is a web framework. It uses Python."
        content2 = "Django is another web framework. It also uses Python."
        temp_storage.add_study_material(topic['id'], "flask.txt", content1)
        temp_storage.add_study_material(topic['id'], "django.txt", content2)

        results = rag_retrieval.retrieve_definitions(topic['id'], "framework", limit=5)
        assert len(results) == 2  # Two materials

        # Check relevance scoring - both should have matches
        for result in results:
            assert len(result['definitions']) > 0
            assert result['relevance_score'] > 0

    def test_retrieve_definitions_no_matches(self, temp_storage, rag_retrieval):
        """Test retrieving with query that has no matches."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        content = "Python is a programming language."
        temp_storage.add_study_material(topic['id'], "python.txt", content)

        results = rag_retrieval.retrieve_definitions(topic['id'], "nonexistent")
        assert results == []

    def test_get_topic_definitions(self, temp_storage, rag_retrieval):
        """Test getting all definitions for a topic."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        content = "First sentence. Second sentence! Third sentence?"
        temp_storage.add_study_material(topic['id'], "test.txt", content)

        definitions = rag_retrieval.get_topic_definitions(topic['id'])
        assert len(definitions) == 3
        assert "First sentence." in definitions
        assert "Second sentence!" in definitions
        assert "Third sentence?" in definitions

    def test_get_topic_definitions_multiple_materials(self, temp_storage, rag_retrieval):
        """Test getting definitions from multiple materials."""
        subject = temp_storage.add_subject("Subject", "Desc")
        topic = temp_storage.add_topic(subject['id'], "Topic", "Desc")

        content1 = "Material 1 sentence 1. Material 1 sentence 2."
        content2 = "Material 2 sentence 1. Material 2 sentence 2."
        temp_storage.add_study_material(topic['id'], "mat1.txt", content1)
        temp_storage.add_study_material(topic['id'], "mat2.txt", content2)

        definitions = rag_retrieval.get_topic_definitions(topic['id'])
        assert len(definitions) == 4
        assert all("sentence" in sent for sent in definitions)