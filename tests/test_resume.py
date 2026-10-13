from services.resume_service import ResumeService


def test_resume_skill_dictionary_extraction():
    sample_text = """
    John Doe
    B.Tech Information Technology
    Skills: Proficient in Java, Spring Boot, MySQL, DBMS, and Python.
    Built a RESTful API using Flask and SQLite with JWT authentication.
    Good knowledge of Data Structures and Algorithms.
    """

    analysis = ResumeService.extract_skills_and_recommendations(sample_text)
    detected = analysis["skills"]
    recommendations = analysis["recommendations"]

    assert "Java" in detected
    assert "Spring Boot" in detected
    assert "Python" in detected
    assert "DBMS" in detected
    assert "SQL" in detected
    assert "Data Structures" in detected
    assert len(recommendations) > 0


def test_resume_scanned_or_empty_detection():
    # Empty string simulates scanned image PDF with 0 extractable text
    analysis = ResumeService.extract_skills_and_recommendations("")
    assert analysis["skills"] == []
    assert analysis["recommendations"] == []
