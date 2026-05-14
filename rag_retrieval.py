import re
from typing import List, Dict, Optional
from storage import Storage

class RAGRetrieval:
    def __init__(self, storage: Storage):
        self.storage = storage

    def retrieve_definitions(self, topic_id: str, query: str, limit: int = 5) -> List[Dict]:
        """
        Retrieve relevant definitions from study material for the given topic.
        Uses simple keyword matching for now.
        """
        study_materials = self.storage.list_study_material(topic_id=topic_id)
        if not study_materials:
            return []

        query_keywords = set(re.findall(r'\b\w+\b', query.lower()))
        results = []

        for material in study_materials:
            content = material["content"].lower()
            content_words = set(re.findall(r'\b\w+\b', content))

            # Simple overlap score
            overlap = len(query_keywords.intersection(content_words))
            if overlap > 0:
                # Extract sentences containing keywords
                sentences = re.split(r'(?<=[.!?])\s+', material["content"])
                relevant_sentences = [
                    sentence for sentence in sentences
                    if any(keyword in sentence.lower() for keyword in query_keywords)
                ]

                results.append({
                    "material_id": material["id"],
                    "filename": material["filename"],
                    "definitions": relevant_sentences[:limit],  # Limit per material
                    "relevance_score": overlap
                })

        # Sort by relevance and return top results
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        return results[:limit]

    def get_topic_definitions(self, topic_id: str) -> List[str]:
        """
        Get all definitions/snippets from study material for a topic.
        """
        study_materials = self.storage.list_study_material(topic_id=topic_id)
        all_definitions = []
        for material in study_materials:
            sentences = re.split(r'(?<=[.!?])\s+', material["content"])
            all_definitions.extend(sentences)
        return all_definitions
