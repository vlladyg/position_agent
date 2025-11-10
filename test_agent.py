#!/usr/bin/env python3
"""
Test script for the Resume Tailoring Agent.
This tests the workflow with a sample job description.
"""
from main import resume_agent

# Sample job description for testing
SAMPLE_JOB_DESCRIPTION = """
Senior Python Developer
TechCorp Solutions

About the Role:
We're looking for a Senior Python Developer to join our growing team. You'll be 
responsible for building scalable web applications using modern Python frameworks.

Requirements:
- 5+ years of Python development experience
- Strong experience with Django or Flask
- Proficiency in SQL databases (PostgreSQL, MySQL)
- Experience with RESTful API design
- Knowledge of Docker and containerization
- Familiarity with AWS or other cloud platforms
- Experience with Git and CI/CD pipelines
- Strong problem-solving and analytical skills

Nice to Have:
- Experience with React or Vue.js
- Knowledge of microservices architecture
- Experience with Kubernetes
- Contributions to open-source projects

Responsibilities:
- Design and implement scalable backend services
- Write clean, maintainable, and well-tested code
- Collaborate with frontend developers and product managers
- Participate in code reviews and architectural decisions
- Mentor junior developers
- Optimize application performance and database queries

We offer competitive salary, benefits, and the opportunity to work on 
challenging projects with cutting-edge technologies.
"""


def test_agent():
    """Test the agent with sample job description."""
    print("\n" + "="*80)
    print("TESTING RESUME TAILORING AGENT")
    print("="*80)
    print("\nThis test will run the complete workflow with a sample job description.")
    print("\n" + "="*80 + "\n")
    
    # Prepare initial state
    initial_state = {
        "messages": [],
        "job_description": SAMPLE_JOB_DESCRIPTION,
        "input_method": "text",
        "company_name": "TechCorp Solutions",
        "keywords_analysis": None,
        "tailored_summary": None,
        "tailored_skills": None,
        "tailored_experience": None,
        "tailored_name_desc": None,
        "length_check_result": None,
        "cover_letter": None,
        "interest_answer": None,
        "output_files": None
    }
    
    try:
        # Run the agent
        final_state = resume_agent.invoke(initial_state)
        
        # Verify outputs
        print("\n" + "="*80)
        print("TEST RESULTS")
        print("="*80)
        
        checks = {
            "Job Description": bool(final_state.get("job_description")),
            "Keywords Analysis": bool(final_state.get("keywords_analysis")),
            "Tailored Summary": bool(final_state.get("tailored_summary")),
            "Tailored Skills": bool(final_state.get("tailored_skills")),
            "Tailored Experience": bool(final_state.get("tailored_experience")),
            "Tailored Name/Desc": bool(final_state.get("tailored_name_desc")),
            "Length Check": bool(final_state.get("length_check_result")),
            "Cover Letter": bool(final_state.get("cover_letter")),
            "Interest Answer": bool(final_state.get("interest_answer")),
            "Output Files": bool(final_state.get("output_files"))
        }
        
        all_passed = all(checks.values())
        
        for check_name, passed in checks.items():
            status = "✓" if passed else "✗"
            print(f"{status} {check_name}: {'PASS' if passed else 'FAIL'}")
        
        if final_state.get("output_files"):
            files = final_state["output_files"]
            print(f"\nGenerated Files:")
            print(f"  - Text: {files.get('text_file')}")
            print(f"  - PDF:  {files.get('pdf_file', 'Not generated')}")
        
        print("\n" + "="*80)
        if all_passed:
            print("✓ ALL TESTS PASSED!")
        else:
            print("✗ SOME TESTS FAILED")
        print("="*80 + "\n")
        
        return all_passed
        
    except Exception as e:
        print("\n" + "="*80)
        print("✗ TEST FAILED WITH ERROR")
        print("="*80)
        print(f"\nError: {e}")
        import traceback
        traceback.print_exc()
        return False


if __name__ == "__main__":
    import sys
    
    print("\n⚠ NOTE: This test requires:")
    print("  1. Valid OPENAI_API_KEY in .env")
    print("  2. CV.pdf in literature/ folder")
    print("  3. How to write an excellent Cover Letter.pdf in literature/ folder")
    print("\nPress Ctrl+C to cancel, or Enter to continue...")
    
    try:
        input()
    except KeyboardInterrupt:
        print("\n\nTest cancelled.\n")
        sys.exit(0)
    
    success = test_agent()
    sys.exit(0 if success else 1)

