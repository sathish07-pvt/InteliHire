from typing import Dict, Any, List, Optional
from models import db, Question
from services.question_generation_service import QuestionGenerationService


class QuestionSelectionService:
    """
    Hybrid Question Selection & Adaptive Engine.
    Executes tiered selection priority and adapts difficulty based on candidate performance.
    """

    DIFFICULTY_LEVELS = ["Easy", "Medium", "Hard"]

    @classmethod
    def get_adapted_difficulty(cls, current_difficulty: str, previous_score: Optional[float]) -> str:
        """
        Adapts difficulty for the next question based on candidate score:
        - Score >= 80: progress to higher difficulty
        - Score 50-79: retain current difficulty
        - Score < 50: reduce to simpler foundational difficulty
        """
        if previous_score is None:
            return current_difficulty or "Medium"

        try:
            curr_idx = cls.DIFFICULTY_LEVELS.index(current_difficulty)
        except ValueError:
            curr_idx = 1  # Default to Medium

        if previous_score >= 80.0:
            next_idx = min(len(cls.DIFFICULTY_LEVELS) - 1, curr_idx + 1)
        elif previous_score < 50.0:
            next_idx = max(0, curr_idx - 1)
        else:
            next_idx = curr_idx

        return cls.DIFFICULTY_LEVELS[next_idx]

    @classmethod
    def select_next_question(
        cls,
        skill: str,
        company: str,
        interview_type: str,
        target_difficulty: str,
        used_question_ids: List[int],
        used_question_texts: List[str],
        previous_question_id: Optional[int] = None,
        previous_score: Optional[float] = None
    ) -> Dict[str, Any]:
        """
        Executes hybrid question selection following strict hierarchy:
        1. Linked follow-up question in question bank (if parent question had follow_up link)
        2. Unused company-specific question from bank matching skill & difficulty
        3. Unused general question from bank matching skill & difficulty
        4. Locally generated template question
        """
        adapted_diff = cls.get_adapted_difficulty(target_difficulty, previous_score)

        # 1. Tier 1: Linked Follow-Up Question
        if previous_question_id:
            parent_q = db.session.get(Question, previous_question_id)
            if parent_q and parent_q.follow_up_questions:
                for child_q in parent_q.follow_up_questions:
                    if child_q.is_active and child_q.id not in used_question_ids:
                        return {
                            "question_id": child_q.id,
                            "question_text": child_q.question_text,
                            "model_answer": child_q.model_answer,
                            "keywords": child_q.keywords or [],
                            "difficulty": child_q.difficulty,
                            "source": "company_bank" if child_q.company == company else "general_bank",
                            "category": child_q.category or f"{skill} Follow-up"
                        }

        # 2. Tier 2: Company-Specific Question from Bank
        if company and company.lower() != "general":
            # First try matching adapted difficulty
            company_q = (
                Question.query
                .filter(
                    Question.company.ilike(company),
                    Question.skill.ilike(skill),
                    Question.interview_type.ilike(interview_type),
                    Question.difficulty == adapted_diff,
                    Question.is_active == True,
                    ~Question.id.in_(used_question_ids) if used_question_ids else True
                )
                .first()
            )
            # If no exact difficulty match, try any difficulty in company bank
            if not company_q:
                company_q = (
                    Question.query
                    .filter(
                        Question.company.ilike(company),
                        Question.skill.ilike(skill),
                        Question.interview_type.ilike(interview_type),
                        Question.is_active == True,
                        ~Question.id.in_(used_question_ids) if used_question_ids else True
                    )
                    .first()
                )

            if company_q:
                return {
                    "question_id": company_q.id,
                    "question_text": company_q.question_text,
                    "model_answer": company_q.model_answer,
                    "keywords": company_q.keywords or [],
                    "difficulty": company_q.difficulty,
                    "source": "company_bank",
                    "category": company_q.category or f"{company} Technical Question"
                }

        # 3. Tier 3: General Question Bank
        # Match adapted difficulty first
        general_q = (
            Question.query
            .filter(
                Question.skill.ilike(skill),
                Question.interview_type.ilike(interview_type),
                Question.difficulty == adapted_diff,
                Question.is_active == True,
                ~Question.id.in_(used_question_ids) if used_question_ids else True
            )
            .first()
        )
        if not general_q:
            # Try any difficulty in general bank
            general_q = (
                Question.query
                .filter(
                    Question.skill.ilike(skill),
                    Question.interview_type.ilike(interview_type),
                    Question.is_active == True,
                    ~Question.id.in_(used_question_ids) if used_question_ids else True
                )
                .first()
            )

        if general_q:
            return {
                "question_id": general_q.id,
                "question_text": general_q.question_text,
                "model_answer": general_q.model_answer,
                "keywords": general_q.keywords or [],
                "difficulty": general_q.difficulty,
                "source": "general_bank",
                "category": general_q.category or f"{skill} Practice"
            }

        # 4. Tier 4: Local Question Generation Engine
        gen = QuestionGenerationService.generate_question(
            skill=skill,
            difficulty=adapted_diff,
            interview_type=interview_type,
            company=company,
            used_questions=used_question_texts
        )
        return {
            "question_id": None,
            "question_text": gen["question_text"],
            "model_answer": gen["model_answer"],
            "keywords": gen["keywords"],
            "difficulty": gen["difficulty"],
            "source": "generator",
            "category": gen.get("category", f"{skill} Concept Check")
        }
