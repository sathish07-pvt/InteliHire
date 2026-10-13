from services.nlp_evaluation_service import NLPEvaluationService


def test_empty_answer_handling():
    result = NLPEvaluationService.evaluate_answer(
        question="What is inheritance in Java?",
        model_answer="Inheritance is a mechanism where one class acquires the properties of another.",
        user_answer="",
        keywords=["inheritance", "extends", "superclass"]
    )
    assert result["final_score"] == 0.0
    assert result["similarity_score"] == 0.0
    assert result["keyword_coverage"] == 0.0
    assert len(result["missing_concepts"]) == 3
    assert "Answer was left blank" in result["weaknesses"][0]


def test_high_quality_answer_evaluation():
    question = "Explain why Java does not support multiple inheritance with classes."
    model_answer = "Java prevents multiple inheritance of classes to avoid ambiguity, specifically the diamond problem where two parent classes define the same method signature. Interfaces are used instead."
    user_answer = "Java avoids multiple inheritance with classes to prevent the diamond problem and compiler ambiguity when two classes have the same method signature. Instead Java uses interfaces."
    keywords = ["multiple inheritance", "diamond problem", "ambiguity", "interface", "method signature"]

    result = NLPEvaluationService.evaluate_answer(
        question=question,
        model_answer=model_answer,
        user_answer=user_answer,
        keywords=keywords
    )

    assert result["final_score"] >= 70.0
    assert result["similarity_score"] >= 50.0
    assert result["keyword_coverage"] >= 80.0
    assert len(result["strengths"]) > 0


def test_off_topic_answer_evaluation():
    question = "Explain ACID properties in DBMS."
    model_answer = "ACID stands for Atomicity, Consistency, Isolation, and Durability."
    user_answer = "The Eiffel tower is located in Paris France and attracts many tourists."
    keywords = ["ACID", "Atomicity", "Consistency", "Isolation", "Durability"]

    result = NLPEvaluationService.evaluate_answer(
        question=question,
        model_answer=model_answer,
        user_answer=user_answer,
        keywords=keywords
    )

    assert result["final_score"] <= 30.0
    assert result["keyword_coverage"] == 0.0
    assert len(result["missing_concepts"]) == 5
