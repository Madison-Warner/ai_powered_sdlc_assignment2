import random
import re
from typing import Dict, List, Optional
from storage import Storage

class QuizEngine:
    def __init__(self, storage: Storage):
        self.storage = storage

    def generate_quiz(self, subject_id: str) -> Optional[Dict]:
        """
        Generate a 15-question quiz for the given subject.
        Questions are based on study material from topics in the subject.
        """
        topics = self.storage.list_topics(subject_id=subject_id)
        if not topics:
            return None

        all_sentences = []
        for topic in topics:
            study_materials = self.storage.list_study_material(topic_id=topic["id"])
            for material in study_materials:
                sentences = re.split(r'(?<=[.!?])\s+', material["content"])
                for sentence in sentences:
                    sentence = sentence.strip()
                    if sentence:
                        all_sentences.append({
                            "sentence": sentence,
                            "topic_id": topic["id"],
                            "material_id": material["id"]
                        })

        if len(all_sentences) < 15:
            return None  # Not enough content

        # Select 15 sentences with topic weighting based on weak score
        for item in all_sentences:
            topic = self.storage.get_topic(item["topic_id"])
            item["weight"] = 1 + (topic["weak_score"] if topic else 0)

        selected_sentences = self._weighted_sample_without_replacement(all_sentences, 15)

        questions = []
        for item in selected_sentences:
            question_type = random.choice(["multiple_choice", "true_false"])
            if question_type == "multiple_choice":
                question = self._generate_multiple_choice_from_material(item)
            else:
                question = self._generate_true_false_from_material(item)
            questions.append(question)

        # Save the quiz
        quiz = self.storage.add_quiz(subject_id, questions)
        return quiz

    def _weighted_sample_without_replacement(self, items: List[Dict], count: int) -> List[Dict]:
        selected = []
        available = list(items)
        while len(selected) < count and available:
            weights = [item.get("weight", 1) for item in available]
            chosen = random.choices(available, weights=weights, k=1)[0]
            selected.append(chosen)
            available.remove(chosen)
        return selected

    def _generate_multiple_choice_from_material(self, item: Dict) -> Dict:
        """
        Generate a multiple-choice question from a study material sentence.
        """
        question_text = "Which of the following statements is correct?"
        correct_answer = item["sentence"]

        # Generate 3 distractors (simple for now)
        distractors = [
            "Incorrect statement 1.",
            "Incorrect statement 2.",
            "Incorrect statement 3."
        ]

        options = [correct_answer] + distractors
        random.shuffle(options)

        return {
            "id": item["material_id"] + "_" + str(random.randint(1000, 9999)),  # unique id
            "type": "multiple_choice",
            "question": question_text,
            "options": options,
            "correct_answer": correct_answer,
            "topic_id": item["topic_id"]
        }

    def _generate_true_false_from_material(self, item: Dict) -> Dict:
        """
        Generate a true/false question from a study material sentence.
        """
        statement = f"True or False: {item['sentence']}"
        correct_answer = "True"

        return {
            "id": item["material_id"] + "_" + str(random.randint(1000, 9999)),  # unique id
            "type": "true_false",
            "question": statement,
            "options": ["True", "False"],
            "correct_answer": correct_answer,
            "topic_id": item["topic_id"]
        }

    def grade_quiz(self, quiz_id: str, answers: Dict[str, str]) -> Dict:
        """
        Grade the quiz answers and update weak topics.
        """
        quiz = self.storage.get_quiz(quiz_id)
        if not quiz:
            return {"error": "Quiz not found"}

        topic_score_delta = {}
        correct_count = 0
        total_questions = len(quiz["questions"])
        feedback = []

        for question in quiz["questions"]:
            question_id = question["id"]
            user_answer = answers.get(question_id, "")
            correct_answer = question["correct_answer"]
            topic_id = question["topic_id"]

            is_correct = user_answer.strip().lower() == correct_answer.strip().lower()
            if is_correct:
                correct_count += 1
                topic_score_delta[topic_id] = topic_score_delta.get(topic_id, 0) - 1
            else:
                topic_score_delta[topic_id] = topic_score_delta.get(topic_id, 0) + 1

            feedback.append({
                "question_id": question_id,
                "user_answer": user_answer,
                "correct_answer": correct_answer,
                "is_correct": is_correct
            })

        # Update weak scores with decay for correct answers and increase for incorrect ones
        for topic_id, delta in topic_score_delta.items():
            topic = self.storage.get_topic(topic_id)
            if topic is None:
                continue
            current_score = topic["weak_score"]
            new_score = max(0, current_score + delta)
            self.storage.set_weak_score(topic_id, new_score)

        score_percentage = (correct_count / total_questions) * 100 if total_questions > 0 else 0

        return {
            "score": score_percentage,
            "correct_count": correct_count,
            "total_questions": total_questions,
            "feedback": feedback
        }
