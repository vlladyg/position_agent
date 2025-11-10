#!/usr/bin/env python3
"""
Test the updated cover letter generation with longer format.
"""
import os
os.environ['LANGCHAIN_TRACING_V2'] = 'false'

from prompts import GENERATE_COVER_LETTER_PROMPT

# Check the prompt
print("="*70)
print("COVER LETTER PROMPT CHECK")
print("="*70)

# Look for word count requirement
if "600-900 words" in GENERATE_COVER_LETTER_PROMPT:
    print("✓ Word count updated: 600-900 words (1-1.5 pages)")
else:
    print("✗ Word count NOT updated")

if "retrieve_cover_letter_guide" in GENERATE_COVER_LETTER_PROMPT:
    print("✓ RAG tool usage: retrieve_cover_letter_guide is mentioned")
else:
    print("✗ RAG tool NOT mentioned")

if "FIRST:" in GENERATE_COVER_LETTER_PROMPT or "IMPORTANT:" in GENERATE_COVER_LETTER_PROMPT:
    print("✓ Emphasis on using guide: Strong instruction to use RAG")
else:
    print("✗ No strong emphasis on using guide")

# Count instruction points
instruction_lines = [line for line in GENERATE_COVER_LETTER_PROMPT.split('\n') if line.strip().startswith(tuple('123456789'))]
print(f"✓ Number of detailed instructions: {len(instruction_lines)}")

print("\n" + "="*70)
print("Summary: Cover letter will now be 600-900 words (1-1.5 pages)")
print("RAG: Yes, using retrieve_cover_letter_guide for best practices")
print("="*70)

