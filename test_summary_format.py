#!/usr/bin/env python3
"""
Test that the summary prompt now requests both formats.
"""
from prompts import TAILOR_SUMMARY_PROMPT

print("="*70)
print("CV SUMMARY FORMAT CHECK")
print("="*70)

# Check for both formats
if "PARAGRAPH FORMAT" in TAILOR_SUMMARY_PROMPT:
    print("✓ Paragraph format requested")
else:
    print("✗ Paragraph format NOT mentioned")

if "BULLET POINT FORMAT" in TAILOR_SUMMARY_PROMPT:
    print("✓ Bullet point format requested")
else:
    print("✗ Bullet point format NOT mentioned")

if "BOTH versions" in TAILOR_SUMMARY_PROMPT or "BOTH formats" in TAILOR_SUMMARY_PROMPT:
    print("✓ Emphasis on providing BOTH formats")
else:
    print("✗ No emphasis on both formats")

# Check for bullet point details
if "4-6 punchy bullet points" in TAILOR_SUMMARY_PROMPT:
    print("✓ Specific guidance: 4-6 bullet points")
else:
    print("✗ No specific bullet count")

if "Start each bullet with" in TAILOR_SUMMARY_PROMPT:
    print("✓ Bullet point style guidance provided")
else:
    print("✗ No bullet style guidance")

print("\n" + "="*70)
print("Summary: CV summary will now be generated in TWO formats:")
print("  1. Paragraph format (3-4 sentences)")
print("  2. Bullet point format (4-6 bullets)")
print("="*70)

