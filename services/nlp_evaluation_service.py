import re
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


class NLPEvaluationService:
    """
    Transparent, evidence-based NLP answer evaluation using TF-IDF Vectorizer,
    Cosine Similarity, and Lexical Keyword Coverage.
    """

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        # Lowercase, retain alphanumeric and basic programming symbols
        cleaned = re.sub(r"[^\w\s\+\#\./\-]", " ", text.lower())
        return " ".join(cleaned.split())

    @classmethod
    def evaluate_answer(
        cls,
        question: str,
        model_answer: str,
        user_answer: str,
        keywords: List[str]
    ) -> Dict[str, Any]:
        """
        Evaluates a candidate's answer against the model answer and target keywords.
        Returns a comprehensive dictionary with scores and actionable feedback.
        """
        raw_user = (user_answer or "").strip()
        cleaned_user = cls._clean_text(raw_user)
        cleaned_model = cls._clean_text(model_answer or "")
        word_count = len(cleaned_user.split())

        # 1. Edge Case: Empty or trivial answer (< 3 words)
        if not cleaned_user or word_count < 3:
            return {
                "similarity_score": 0.0,
                "keyword_coverage": 0.0,
                "final_score": 0.0,
                "strengths": [],
                "weaknesses": [
                    "Answer was left blank or was too brief to evaluate.",
                    "Candidate did not demonstrate understanding of the question requirements."
                ],
                "missing_concepts": keywords if keywords else ["Foundational subject concepts"],
                "feedback": (
                    "No substantive answer provided. In a live interview, provide at least a definition, "
                    "core mechanism, or practical example even if uncertain."
                ),
                "suggested_improvements": [
                    "Define the primary term or pattern requested.",
                    "Mention key technical keywords and architectural trade-offs.",
                    "Provide a brief code snippet or real-world example."
                ],
                "assessment_method": "TF-IDF Vector Space Model & Lexical Keyword Coverage"
            }

        # 2. TF-IDF Cosine Similarity & Lexical Semantic Alignment
        try:
            vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 1))
            corpus = [cleaned_model, cleaned_user]
            tfidf_matrix = vectorizer.fit_transform(corpus)
            cos_sim = float(cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:2])[0][0])
            
            # Token overlap alignment (Jaccard on non-stopword tokens)
            feature_names = set(vectorizer.get_feature_names_out())
            user_tokens = set(cleaned_user.split()) & feature_names
            model_tokens = set(cleaned_model.split()) & feature_names
            
            if model_tokens:
                jaccard = len(user_tokens & model_tokens) / len(user_tokens | model_tokens)
            else:
                jaccard = cos_sim

            blended_sim = (cos_sim * 0.65) + (jaccard * 0.35)
            similarity_pct = max(0.0, min(100.0, blended_sim * 100.0))
        except Exception:
            similarity_pct = 25.0

        # 3. Keyword Coverage Calculation
        detected_keywords = []
        missing_keywords = []

        if keywords:
            for kw in keywords:
                kw_clean = kw.lower().strip()
                # Check for full phrase or individual key tokens
                pattern = r"(?:\b|\s)" + re.escape(kw_clean) + r"(?:\b|\s)"
                if re.search(pattern, f" {cleaned_user} "):
                    detected_keywords.append(kw)
                else:
                    parts = [p for p in kw_clean.split() if len(p) > 2]
                    if parts and all(p in cleaned_user for p in parts):
                        detected_keywords.append(kw)
                    else:
                        missing_keywords.append(kw)

            keyword_coverage_pct = (len(detected_keywords) / len(keywords)) * 100.0
        else:
            keyword_coverage_pct = similarity_pct

        # 4. Completeness & Length Factor
        # Reward substantive answers while discouraging excessive rambling
        target_words = max(12, len(cleaned_model.split()) * 0.4)
        length_ratio = min(1.0, word_count / target_words)
        completeness_pct = length_ratio * 100.0

        # 5. Composite Final Score Formula (out of 100)
        # 35% Cosine Similarity + 45% Keyword Coverage + 20% Completeness
        raw_final = (similarity_pct * 0.35) + (keyword_coverage_pct * 0.45) + (completeness_pct * 0.20)
        
        # Keyword mastery bonus
        if keyword_coverage_pct >= 80.0:
            raw_final = min(100.0, raw_final + 10.0)

        final_score = round(max(5.0, min(100.0, raw_final)), 1)

        # 6. Constructive Feedback Generation
        strengths = []
        weaknesses = []

        if detected_keywords:
            strengths.append(f"Successfully identified key concepts: {', '.join(detected_keywords[:4])}.")
        if similarity_pct >= 60.0:
            strengths.append("Strong semantic alignment with technical interview criteria.")
        elif similarity_pct >= 40.0:
            strengths.append("Demonstrated foundational grasp of the core question.")

        if missing_keywords:
            weaknesses.append(f"Omitted crucial technical elements: {', '.join(missing_keywords[:4])}.")
        if word_count < 15:
            weaknesses.append("Response is somewhat brief; consider elaborating on internal mechanisms.")
        elif similarity_pct < 35.0:
            weaknesses.append("Explanation deviates from expected architectural explanation.")

        # Default fallback items if lists are empty
        if not strengths:
            strengths.append("Candidate attempted an answer with relevant terminology.")
        if not weaknesses:
            weaknesses.append("Minor polish on specific edge cases would further improve clarity.")

        feedback_summary = (
            f"Candidate achieved an overall score of {final_score}/100. "
            f"Semantic similarity: {round(similarity_pct, 1)}%, Keyword coverage: {round(keyword_coverage_pct, 1)}%. "
            f"Covered {len(detected_keywords)} of {len(keywords)} expected terms."
        )

        suggested_improvements = []
        if missing_keywords:
            suggested_improvements.append(f"Incorporate technical terms such as {', '.join(missing_keywords[:3])}.")
        if word_count < 25:
            suggested_improvements.append("Elaborate on how this concept impacts runtime performance or memory.")
        suggested_improvements.append("Structure answers systematically (definition -> mechanism -> practical example).")

        return {
            "similarity_score": round(similarity_pct, 1),
            "keyword_coverage": round(keyword_coverage_pct, 1),
            "final_score": final_score,
            "strengths": strengths,
            "weaknesses": weaknesses,
            "missing_concepts": missing_keywords,
            "feedback": feedback_summary,
            "suggested_improvements": suggested_improvements,
            "assessment_method": "TF-IDF Vector Space Model & Lexical Keyword Coverage"
        }
