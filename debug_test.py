#!/usr/bin/env python3
"""
Debug test to measure performance per step.
"""
import time
import os
os.environ['LANGCHAIN_TRACING_V2'] = 'false'

from main import resume_agent

# Very short test job description
job_desc = """
Python Developer at TestCo
Requirements: Python, Django, SQL
Responsibilities: Build web apps
"""

print("="*60)
print("PERFORMANCE DEBUG TEST")
print("="*60)

state = {
    'messages': [],
    'job_description': job_desc,
    'input_method': 'text',
    'company_name': 'TestCo',
    'keywords_analysis': None,
    'tailored_summary': None,
    'tailored_skills': None,
    'tailored_experience': None,
    'tailored_name_desc': None,
    'length_check_result': None,
    'cover_letter': None,
    'interest_answer': None,
    'output_files': None
}

print("\nStarting workflow with very short job description...")
print("This will measure time for each step.\n")

start_time = time.time()

try:
    result = resume_agent.invoke(state)
    
    total_time = time.time() - start_time
    
    print("\n" + "="*60)
    print(f"TOTAL TIME: {total_time:.2f} seconds")
    print("="*60)
    
    # Check outputs
    if result.get('keywords_analysis'):
        print(f"✓ Keywords: {len(result['keywords_analysis'])} chars")
    if result.get('tailored_summary'):
        print(f"✓ Summary: {len(result['tailored_summary'])} chars")
    if result.get('output_files'):
        print(f"✓ Files saved")
    
except KeyboardInterrupt:
    print("\n\nTest interrupted")
except Exception as e:
    print(f"\n\nError: {e}")
    import traceback
    traceback.print_exc()

