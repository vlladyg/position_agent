"""
PDF operations for modifying CV and saving outputs.
"""
import os
from datetime import datetime
from pypdf import PdfReader, PdfWriter
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.units import inch
from io import BytesIO

def save_text_output(output_dir: str, company_name: str, position: str,
                     keywords_analysis: str, tailored_summary: str,
                     tailored_skills: str, tailored_experience: str,
                     tailored_name_desc: str, cover_letter: str,
                     interest_answer: str) -> str:
    """
    Save all outputs to a structured text file.
    
    Args:
        output_dir: Directory to save the file
        company_name: Company name for filename
        position: Position title for filename
        All other args: Content sections to save
        
    Returns:
        Path to saved text file
    """
    # Create output directory if it doesn't exist
    os.makedirs(output_dir, exist_ok=True)
    
    # Sanitize filename
    safe_company = sanitize_filename(company_name)
    safe_position = sanitize_filename(position) if position else "Position"
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    filename = f"{safe_company}_{safe_position}_{timestamp}_tailored.txt"
    filepath = os.path.join(output_dir, filename)
    
    # Build content
    content = f"""
{'='*80}
TAILORED RESUME AND COVER LETTER
{'='*80}
Company: {company_name}
Position: {position}
Generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
{'='*80}

{'='*80}
KEYWORDS ANALYSIS
{'='*80}
{keywords_analysis}

{'='*80}
PROFESSIONAL TITLE & SPECIALIZATION
{'='*80}
{tailored_name_desc}

{'='*80}
PROFESSIONAL SUMMARY
{'='*80}
{tailored_summary}

{'='*80}
SKILLS
{'='*80}
{tailored_skills}

{'='*80}
EXPERIENCE BULLETS
{'='*80}
{tailored_experience}

{'='*80}
COVER LETTER
{'='*80}
{cover_letter}

{'='*80}
WHY ARE YOU INTERESTED IN THIS POSITION?
{'='*80}
{interest_answer}

{'='*80}
END OF DOCUMENT
{'='*80}
"""
    
    # Write to file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(content)
    
    print(f"\n✓ Text output saved: {filepath}")
    return filepath

def create_tailored_cv_pdf(output_dir: str, company_name: str, position: str,
                           tailored_name_desc: str, tailored_summary: str,
                           tailored_skills: str, tailored_experience: str) -> str:
    """
    Create a new PDF with tailored CV content.
    This creates a simple formatted PDF rather than modifying the original.
    
    Args:
        output_dir: Directory to save the file
        company_name: Company name for filename
        position: Position title for filename
        tailored_name_desc: Professional title
        tailored_summary: Professional summary
        tailored_skills: Skills section
        tailored_experience: Experience bullets
        
    Returns:
        Path to saved PDF or None if failed
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        # Sanitize filename
        safe_company = sanitize_filename(company_name)
        safe_position = sanitize_filename(position) if position else "Position"
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        filename = f"{safe_company}_{safe_position}_{timestamp}_CV.pdf"
        filepath = os.path.join(output_dir, filename)
        
        # Create PDF
        doc = SimpleDocTemplate(
            filepath,
            pagesize=letter,
            rightMargin=0.5*inch,
            leftMargin=0.5*inch,
            topMargin=0.5*inch,
            bottomMargin=0.5*inch
        )
        
        # Container for the 'Flowable' objects
        story = []
        
        # Define styles
        styles = getSampleStyleSheet()
        
        title_style = ParagraphStyle(
            'CustomTitle',
            parent=styles['Heading1'],
            fontSize=14,
            textColor='#000000',
            spaceAfter=6,
            alignment=1  # Center
        )
        
        heading_style = ParagraphStyle(
            'CustomHeading',
            parent=styles['Heading2'],
            fontSize=11,
            textColor='#000000',
            spaceAfter=6,
            spaceBefore=8
        )
        
        body_style = ParagraphStyle(
            'CustomBody',
            parent=styles['Normal'],
            fontSize=10,
            textColor='#000000',
            spaceAfter=6
        )
        
        # Add content
        # Title
        story.append(Paragraph(tailored_name_desc.replace('\n', '<br/>'), title_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Summary
        story.append(Paragraph("<b>PROFESSIONAL SUMMARY</b>", heading_style))
        story.append(Paragraph(tailored_summary.replace('\n', '<br/>'), body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Skills
        story.append(Paragraph("<b>SKILLS</b>", heading_style))
        story.append(Paragraph(tailored_skills.replace('\n', '<br/>'), body_style))
        story.append(Spacer(1, 0.1*inch))
        
        # Experience
        story.append(Paragraph("<b>EXPERIENCE</b>", heading_style))
        story.append(Paragraph(tailored_experience.replace('\n', '<br/>'), body_style))
        
        # Build PDF
        doc.build(story)
        
        print(f"\n✓ PDF CV saved: {filepath}")
        return filepath
        
    except Exception as e:
        print(f"\n✗ Failed to create PDF: {e}")
        print("  Text file will still contain all the tailored content.")
        return None

def sanitize_filename(name: str) -> str:
    """
    Sanitize a string to be used as a filename.
    
    Args:
        name: String to sanitize
        
    Returns:
        Sanitized filename-safe string
    """
    # Remove or replace invalid filename characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, '_')
    
    # Limit length
    name = name[:50]
    
    # Remove leading/trailing spaces and dots
    name = name.strip('. ')
    
    return name if name else "Unknown"

def extract_position_title(job_description: str) -> str:
    """
    Extract position title from job description.
    
    Args:
        job_description: The job description text
        
    Returns:
        Position title or "Position"
    """
    lines = job_description.split('\n')
    
    # Common job title patterns
    for line in lines[:10]:
        line_stripped = line.strip()
        if not line_stripped:
            continue
            
        # Often the first substantial line is the job title
        if len(line_stripped) > 5 and len(line_stripped) < 100:
            # Filter out common non-title lines
            lower = line_stripped.lower()
            if not any(word in lower for word in ['http', 'www', 'posted', 'date', 'company', 'location']):
                return line_stripped
    
    return "Position"

def save_all_outputs(output_dir: str, company_name: str, job_description: str,
                    keywords_analysis: str, tailored_summary: str,
                    tailored_skills: str, tailored_experience: str,
                    tailored_name_desc: str, cover_letter: str,
                    interest_answer: str) -> dict:
    """
    Save all outputs (both text and PDF if possible).
    
    Returns:
        Dictionary with paths to saved files
    """
    position = extract_position_title(job_description)
    
    # Always save text file
    text_path = save_text_output(
        output_dir, company_name, position,
        keywords_analysis, tailored_summary, tailored_skills,
        tailored_experience, tailored_name_desc,
        cover_letter, interest_answer
    )
    
    # Try to create PDF
    pdf_path = create_tailored_cv_pdf(
        output_dir, company_name, position,
        tailored_name_desc, tailored_summary,
        tailored_skills, tailored_experience
    )
    
    result = {
        "text_file": text_path,
        "pdf_file": pdf_path,
        "position": position
    }
    
    return result

