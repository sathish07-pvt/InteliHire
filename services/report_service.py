from typing import Dict, Any, List
from models import db, InterviewSession, InterviewQuestion, PerformanceReport


class ReportService:
    """
    Evidence-based performance report generator.
    Aggregates question-by-question metrics to produce honest readiness evaluation.
    """

    @classmethod
    def generate_and_save_report(cls, session: InterviewSession) -> PerformanceReport:
        """
        Computes performance metrics from answered questions and persists the report.
        """
        questions: List[InterviewQuestion] = (
            InterviewQuestion.query
            .filter_by(session_id=session.id)
            .order_by(InterviewQuestion.order_index)
            .all()
        )

        if not questions:
            empty_report = PerformanceReport(
                session_id=session.id,
                user_id=session.user_id,
                overall_score=0.0,
                average_score=0.0,
                technical_knowledge_score=0.0,
                readiness_percentage=0.0,
                strong_topics=[],
                weak_topics=[],
                missing_concepts=[],
                recommendations=["Complete at least one question to receive evaluation feedback."],
                summary_notes="Interview terminated with no answers recorded."
            )
            db.session.add(empty_report)
            db.session.commit()
            return empty_report

        total_score = 0.0
        total_sim = 0.0
        total_keyword_cov = 0.0
        answered_count = 0

        strong_topics = set()
        weak_topics = set()
        all_missing = []

        for q in questions:
            score = q.final_score or 0.0
            if q.user_answer and q.user_answer.strip():
                answered_count += 1
                total_score += score
                total_sim += (q.similarity_score or 0.0)
                total_keyword_cov += (q.keyword_coverage or 0.0)

            # Categorize topic strengths
            topic_label = f"Q{q.order_index} ({q.difficulty})"
            if score >= 75.0:
                strong_topics.add(topic_label)
            elif score < 50.0:
                weak_topics.add(topic_label)

            if q.missing_concepts:
                all_missing.extend(q.missing_concepts[:2])

        if answered_count > 0:
            avg_score = round(total_score / answered_count, 1)
            avg_sim = round(total_sim / answered_count, 1)
            avg_cov = round(total_keyword_cov / answered_count, 1)
        else:
            avg_score = 0.0
            avg_sim = 0.0
            avg_cov = 0.0

        # Technical knowledge score: combination of semantic similarity & keyword precision
        tech_score = round((avg_sim * 0.5) + (avg_cov * 0.5), 1)

        # Readiness percentage is weighted by difficulty and average score
        diff_multiplier = {"Easy": 0.85, "Medium": 1.0, "Hard": 1.15}.get(session.difficulty, 1.0)
        readiness = round(min(100.0, avg_score * diff_multiplier), 1)

        # Unique missing concepts
        missing_list = list(dict.fromkeys(all_missing))[:6]

        # Personalized recommendations
        recommendations = []
        if readiness >= 80.0:
            recommendations.append(f"Ready for {session.company} {session.skill} technical interviews. Maintain depth by practicing system design edge cases.")
        elif readiness >= 55.0:
            recommendations.append(f"Moderate readiness for {session.company}. Focus on precision by actively citing technical terms rather than high-level generalities.")
        else:
            recommendations.append(f"Foundational review recommended for {session.skill}. Revisit core mechanisms, standard definitions, and data structures.")

        if missing_list:
            recommendations.append(f"Review and practice questions covering omitted concepts: {', '.join(missing_list[:3])}.")

        recommendations.append("Practice articulating structured responses using the STAR method for behavioral and Definition -> Mechanism -> Tradeoff for technical questions.")

        summary_notes = (
            f"Candidate completed {answered_count} of {session.question_count} questions for {session.company} ({session.skill} - {session.difficulty}). "
            f"Evaluated via scikit-learn TF-IDF Cosine Similarity & Lexical Keyword Coverage. "
            f"(Note: Communication clarity and vocal tone are marked as qualitative self-assessment)."
        )

        # Check if report already exists (e.g. re-eval)
        existing_report = PerformanceReport.query.filter_by(session_id=session.id).first()
        if existing_report:
            report = existing_report
            report.overall_score = avg_score
            report.average_score = avg_score
            report.technical_knowledge_score = tech_score
            report.readiness_percentage = readiness
            report.strong_topics = list(strong_topics)
            report.weak_topics = list(weak_topics)
            report.missing_concepts = missing_list
            report.recommendations = recommendations
            report.summary_notes = summary_notes
        else:
            report = PerformanceReport(
                session_id=session.id,
                user_id=session.user_id,
                overall_score=avg_score,
                average_score=avg_score,
                technical_knowledge_score=tech_score,
                readiness_percentage=readiness,
                strong_topics=list(strong_topics),
                weak_topics=list(weak_topics),
                missing_concepts=missing_list,
                recommendations=recommendations,
                summary_notes=summary_notes
            )
            db.session.add(report)

        db.session.commit()
        return report
