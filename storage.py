import copy
import datetime
import json
import os
import uuid
from typing import Any, Dict, List, Optional

DEFAULT_STORAGE_PATH = os.path.join(os.path.dirname(__file__), "data", "storage.json")

DEFAULT_SCHEMA = {
    "subjects": [],
    "topics": [],
    "flashcards": [],
    "study_material": [],
    "quizzes": [],
    "quiz_results": [],
    "weak_topics": []
}


def new_id() -> str:
    return str(uuid.uuid4())


def timestamp() -> str:
    return datetime.datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


class Storage:
    def __init__(self, path: str = DEFAULT_STORAGE_PATH) -> None:
        self.path = path
        self._ensure_data_directory()
        self.data = self._load()

    def _ensure_data_directory(self) -> None:
        directory = os.path.dirname(self.path)
        os.makedirs(directory, exist_ok=True)

    def _load(self) -> Dict[str, Any]:
        if not os.path.exists(self.path):
            return self._initialize_storage()

        with open(self.path, "r", encoding="utf-8") as handle:
            try:
                loaded_data = json.load(handle)
                # Merge with default schema to add any missing keys
                for key, default_value in DEFAULT_SCHEMA.items():
                    if key not in loaded_data:
                        loaded_data[key] = copy.deepcopy(default_value)
                return loaded_data
            except json.JSONDecodeError:
                return self._initialize_storage()

    def _initialize_storage(self) -> Dict[str, Any]:
        data = copy.deepcopy(DEFAULT_SCHEMA)
        self._save(data)
        return data

    def _save(self, data: Optional[Dict[str, Any]] = None) -> None:
        if data is None:
            data = self.data

        with open(self.path, "w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2)

    def persist(self) -> None:
        self._save()

    def _find_by_id(self, collection: str, object_id: str) -> Optional[Dict[str, Any]]:
        return next((item for item in self.data[collection] if item["id"] == object_id), None)

    def _exists(self, collection: str, object_id: str) -> bool:
        return self._find_by_id(collection, object_id) is not None

    def list_subjects(self) -> List[Dict[str, Any]]:
        return list(self.data["subjects"])

    def get_subject(self, subject_id: str) -> Optional[Dict[str, Any]]:
        return self._find_by_id("subjects", subject_id)

    def add_subject(self, name: str, description: str = "") -> Dict[str, Any]:
        subject = {
            "id": new_id(),
            "name": name,
            "description": description,
            "created_at": timestamp()
        }
        self.data["subjects"].append(subject)
        self.persist()
        return subject

    def update_subject(self, subject_id: str, name: str, description: str) -> Optional[Dict[str, Any]]:
        subject = self._find_by_id("subjects", subject_id)
        if subject is None:
            return None
        subject["name"] = name
        subject["description"] = description
        self.persist()
        return subject

    def delete_subject(self, subject_id: str) -> bool:
        if not self._exists("subjects", subject_id):
            return False

        topics_to_remove = [topic["id"] for topic in self.data["topics"] if topic["subject_id"] == subject_id]
        self.data["flashcards"] = [f for f in self.data["flashcards"] if f["topic_id"] not in topics_to_remove]
        self.data["study_material"] = [m for m in self.data["study_material"] if m["topic_id"] not in topics_to_remove]
        self.data["quiz_results"] = [q for q in self.data["quiz_results"] if q["topic_id"] not in topics_to_remove]
        self.data["topics"] = [t for t in self.data["topics"] if t["subject_id"] != subject_id]
        self.data["subjects"] = [s for s in self.data["subjects"] if s["id"] != subject_id]
        self.persist()
        return True

    def list_topics(self, subject_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if subject_id is None:
            return list(self.data["topics"])
        return [t for t in self.data["topics"] if t["subject_id"] == subject_id]

    def get_topic(self, topic_id: str) -> Optional[Dict[str, Any]]:
        return self._find_by_id("topics", topic_id)

    def add_topic(self, subject_id: str, name: str, description: str = "") -> Optional[Dict[str, Any]]:
        if not self._exists("subjects", subject_id):
            return None
        topic = {
            "id": new_id(),
            "subject_id": subject_id,
            "name": name,
            "description": description,
            "weak_score": 0,
            "created_at": timestamp()
        }
        self.data["topics"].append(topic)
        self.persist()
        return topic

    def update_topic(self, topic_id: str, name: str, description: str) -> Optional[Dict[str, Any]]:
        topic = self._find_by_id("topics", topic_id)
        if topic is None:
            return None
        topic["name"] = name
        topic["description"] = description
        self.persist()
        return topic

    def delete_topic(self, topic_id: str) -> bool:
        if not self._exists("topics", topic_id):
            return False

        self.data["flashcards"] = [f for f in self.data["flashcards"] if f["topic_id"] != topic_id]
        self.data["study_material"] = [m for m in self.data["study_material"] if m["topic_id"] != topic_id]
        self.data["quiz_results"] = [q for q in self.data["quiz_results"] if q["topic_id"] != topic_id]
        self.data["topics"] = [t for t in self.data["topics"] if t["id"] != topic_id]
        self.persist()
        return True

    def list_flashcards(self, topic_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if topic_id is None:
            return list(self.data["flashcards"])
        return [f for f in self.data["flashcards"] if f["topic_id"] == topic_id]

    def get_flashcard(self, flashcard_id: str) -> Optional[Dict[str, Any]]:
        return self._find_by_id("flashcards", flashcard_id)

    def add_flashcard(self, topic_id: str, question: str, answer: str) -> Optional[Dict[str, Any]]:
        if not self._exists("topics", topic_id):
            return None
        flashcard = {
            "id": new_id(),
            "topic_id": topic_id,
            "question": question,
            "answer": answer,
            "created_at": timestamp()
        }
        self.data["flashcards"].append(flashcard)
        self.persist()
        return flashcard

    def update_flashcard(self, flashcard_id: str, question: str, answer: str) -> Optional[Dict[str, Any]]:
        flashcard = self._find_by_id("flashcards", flashcard_id)
        if flashcard is None:
            return None
        flashcard["question"] = question
        flashcard["answer"] = answer
        self.persist()
        return flashcard

    def delete_flashcard(self, flashcard_id: str) -> bool:
        if not self._exists("flashcards", flashcard_id):
            return False
        self.data["flashcards"] = [f for f in self.data["flashcards"] if f["id"] != flashcard_id]
        self.persist()
        return True

    def list_study_material(self, topic_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if topic_id is None:
            return list(self.data["study_material"])
        return [m for m in self.data["study_material"] if m["topic_id"] == topic_id]

    def get_study_material(self, material_id: str) -> Optional[Dict[str, Any]]:
        return self._find_by_id("study_material", material_id)

    def add_study_material(self, topic_id: str, filename: str, content: str) -> Optional[Dict[str, Any]]:
        if not self._exists("topics", topic_id):
            return None
        material = {
            "id": new_id(),
            "topic_id": topic_id,
            "filename": filename,
            "content": content,
            "created_at": timestamp()
        }
        self.data["study_material"].append(material)
        self.persist()
        return material

    def delete_study_material(self, material_id: str) -> bool:
        if not self._exists("study_material", material_id):
            return False
        self.data["study_material"] = [m for m in self.data["study_material"] if m["id"] != material_id]
        self.persist()
        return True

    def add_quiz(self, subject_id: str, questions: List[Dict]) -> Dict[str, Any]:
        quiz = {
            "id": new_id(),
            "subject_id": subject_id,
            "questions": questions,
            "created_at": timestamp()
        }
        self.data["quizzes"].append(quiz)
        self.persist()
        return quiz

    def get_quiz(self, quiz_id: str) -> Optional[Dict[str, Any]]:
        return self._find_by_id("quizzes", quiz_id)

    def list_quiz_results(self, topic_id: Optional[str] = None) -> List[Dict[str, Any]]:
        if topic_id is None:
            return list(self.data["quiz_results"])
        return [q for q in self.data["quiz_results"] if q["topic_id"] == topic_id]

    def get_quiz_result(self, quiz_result_id: str) -> Optional[Dict[str, Any]]:
        return self._find_by_id("quiz_results", quiz_result_id)

    def add_quiz_result(self, topic_id: Optional[str], score: float, details: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        if topic_id and not self._exists("topics", topic_id):
            return None
        quiz_result = {
            "id": new_id(),
            "topic_id": topic_id,
            "score": score,
            "details": details,
            "created_at": timestamp()
        }
        self.data["quiz_results"].append(quiz_result)
        self.persist()
        return quiz_result

    def set_weak_score(self, topic_id: str, weak_score: int) -> Optional[Dict[str, Any]]:
        topic = self._find_by_id("topics", topic_id)
        if topic is None:
            return None
        topic["weak_score"] = weak_score
        self.persist()
        return topic
