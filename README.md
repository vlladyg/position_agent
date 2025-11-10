# Resume and Cover Letter Tailoring Agent

An AI-powered personal assistant built with LangGraph and GPT-5 that helps you tailor your resume and cover letter to specific job descriptions.

## Features

- **Intelligent Analysis**: Extracts keywords, tools, verbs, and methodologies from job descriptions
- **Resume Tailoring**: 
  - Rewrites professional summary for 100% alignment
  - Optimizes skills section
  - Tailors experience bullets
  - Updates professional title and specialization
  - Ensures one-page format compliance
- **Cover Letter Generation**: Creates compelling, personalized cover letters using best practices
- **Interview Prep**: Generates thoughtful "why interested" answers
- **RAG-Powered**: Uses local ChromaDB with your CV and cover letter writing guide
- **Web Support**: Can fetch job descriptions from URLs
- **Multiple Formats**: Outputs both text and PDF files

## Setup

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Environment Configuration

Ensure your `.env` file contains:

```
OPENAI_API_KEY=your_openai_api_key_here
BRIGHTDATA_API_KEY=your_brightdata_key_here  # Optional, for URL fetching fallback
```

### 3. Required Files

Place these files in the `literature/` folder:
- `CV.pdf` - Your current resume/CV
- `How to write an excellent Cover Letter.pdf` - Cover letter writing guide

## Usage

### Run the CLI Agent

```bash
python cli.py
```

### Workflow

1. **Input Job Description**: Choose to paste text or provide a URL
2. **Company Name**: Optionally enter company name (auto-detected if not provided)
3. **Processing**: Agent analyzes and tailors your materials (2-5 minutes)
4. **Output**: Files saved in `outputs/` folder

### Output Files

The agent creates:
- `[Company]_[Position]_[Timestamp]_tailored.txt` - Complete text file with all sections
- `[Company]_[Position]_[Timestamp]_CV.pdf` - Tailored resume in PDF format (if generation succeeds)

Each text file contains:
- Keywords Analysis
- Professional Title & Specialization
- Professional Summary
- Skills
- Experience Bullets
- Cover Letter
- Interest Answer

## Architecture

### Components

1. **rag_setup.py**: ChromaDB vector store initialization with CV and cover letter guide
2. **web_operations.py**: URL fetching with BeautifulSoup and BrightData fallback
3. **prompts.py**: Specialized prompts for each tailoring step
4. **pdf_operations.py**: PDF generation and text file output
5. **main.py**: LangGraph state machine with 10 processing nodes
6. **cli.py**: User-friendly command-line interface

### LangGraph Workflow

```
START 
  → Get Job Description
  → Analyze Keywords
  → Tailor Summary
  → Tailor Skills
  → Tailor Experience
  → Tailor Name/Description
  → Check Resume Length (One-Page)
  → Generate Cover Letter
  → Generate Interest Answer
  → Save Outputs
  → END
```

## Technologies

- **LangGraph**: Workflow orchestration
- **GPT-5**: Language model for tailoring and generation
- **ChromaDB**: Vector database for RAG
- **LangChain**: Document processing and retrieval
- **BeautifulSoup**: Web scraping
- **ReportLab**: PDF generation

## Notes

- First run initializes the ChromaDB vector store (may take 30-60 seconds)
- Subsequent runs use the cached vector store
- The one-page checker ensures your resume stays concise and focused
- All tool calls to retrieve CV and cover letter guide info are automatic

## Troubleshooting

### Common Issues

1. **"PDF file not found"**: Ensure CV.pdf is in the `literature/` folder
2. **"API key error"**: Check your OPENAI_API_KEY in .env
3. **"Failed to fetch URL"**: Try pasting the text directly, or check BrightData API key
4. **"PDF generation failed"**: Text file still contains all content

## Example Usage

```bash
$ python cli.py

================================================================================
RESUME & COVER LETTER TAILORING AGENT
================================================================================

This AI agent will help you tailor your resume and cover letter
to perfectly match a specific job description.

How would you like to provide the job description?
  1. Paste the text directly
  2. Provide a URL to the job posting

Enter your choice (1 or 2): 1

[... paste job description ...]

Enter company name (or press Enter to auto-detect): 

[... processing ...]

✓ PROCESS COMPLETE!

Your tailored resume and cover letter have been saved:
  📄 Text file: outputs/TechCorp_Senior_Developer_20251110_143052_tailored.txt
  📄 PDF file:  outputs/TechCorp_Senior_Developer_20251110_143052_CV.pdf

Thank you for using the Resume Tailoring Agent!
Good luck with your application! 🎉
```

## License

For personal use.

