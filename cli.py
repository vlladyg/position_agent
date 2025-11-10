#!/usr/bin/env python3
"""
CLI interface for the Resume and Cover Letter Tailoring Agent.
"""
from main import resume_agent
from web_operations import fetch_job_description_from_url
import sys


def print_header():
    """Print welcome header."""
    print("\n" + "="*80)
    print("RESUME & COVER LETTER TAILORING AGENT")
    print("="*80)
    print("\nThis AI agent will help you tailor your resume and cover letter")
    print("to perfectly match a specific job description.")
    print("\nThe agent will:")
    print("  1. Analyze key terms from the job description")
    print("  2. Tailor your professional summary")
    print("  3. Optimize your skills section")
    print("  4. Rewrite experience bullets")
    print("  5. Update your professional title")
    print("  6. Verify everything fits on one page")
    print("  7. Generate a customized cover letter")
    print("  8. Create an 'interest answer' for interviews")
    print("  9. Save everything to text and PDF files")
    print("\n" + "="*80 + "\n")


def get_job_description_input():
    """Get job description from user via text or URL."""
    print("How would you like to provide the job description?")
    print("  1. Paste the text directly")
    print("  2. Provide a URL to the job posting")
    
    while True:
        choice = input("\nEnter your choice (1 or 2): ").strip()
        
        if choice == "1":
            print("\n" + "-"*80)
            print("Please paste the job description below.")
            print("When finished, press Enter on a blank line, then type 'END' and press Enter.")
            print("-"*80 + "\n")
            
            lines = []
            while True:
                line = input()
                if line.strip().upper() == "END":
                    break
                lines.append(line)
            
            job_description = "\n".join(lines).strip()
            
            if not job_description:
                print("\n⚠ No job description provided. Please try again.\n")
                continue
            
            if len(job_description) < 100:
                print(f"\n⚠ Job description seems very short ({len(job_description)} characters).")
                confirm = input("Are you sure this is complete? (y/n): ").strip().lower()
                if confirm != 'y':
                    continue
            
            return job_description, "text", None  # Return None for URL
        
        elif choice == "2":
            url = input("\nEnter the URL of the job posting: ").strip()
            
            if not url:
                print("\n⚠ No URL provided. Please try again.\n")
                continue
            
            if not url.startswith("http"):
                print("\n⚠ URL should start with http:// or https://\n")
                continue
            
            print("\nFetching job description from URL...")
            try:
                job_description = fetch_job_description_from_url(url)
                
                print(f"\n✓ Successfully fetched job description ({len(job_description)} characters)")
                print("\nPreview (first 500 characters):")
                print("-"*80)
                print(job_description[:500] + "...")
                print("-"*80)
                
                confirm = input("\nDoes this look correct? (y/n): ").strip().lower()
                if confirm == 'y':
                    return job_description, "url", url  # Return the URL
                else:
                    print("\nLet's try again...\n")
                    continue
                    
            except Exception as e:
                print(f"\n✗ Failed to fetch job description: {e}")
                print("\nWould you like to:")
                print("  1. Try a different URL")
                print("  2. Paste the job description text instead")
                
                retry = input("Choice (1 or 2): ").strip()
                if retry == "2":
                    choice = "1"
                    continue
                else:
                    continue
        
        else:
            print("\n⚠ Invalid choice. Please enter 1 or 2.\n")


def get_company_name():
    """Optionally get company name from user."""
    print("\n" + "-"*80)
    company = input("Enter company name (or press Enter to auto-detect): ").strip()
    print("-"*80)
    
    return company if company else None


def confirm_start():
    """Confirm before starting the processing."""
    print("\n" + "="*80)
    print("READY TO START")
    print("="*80)
    print("\nThe agent will now process your job description and tailor your")
    print("resume and cover letter. This may take 2-5 minutes.")
    print("\n" + "="*80)
    
    input("\nPress Enter to start...")


def run_agent():
    """Main function to run the CLI agent."""
    print_header()
    
    # Get job description
    job_description, input_method, job_url = get_job_description_input()
    
    # Optionally get company name
    company_name = get_company_name()
    
    # Confirm start
    confirm_start()
    
    # Prepare initial state
    initial_state = {
        "messages": [],
        "job_description": job_description,
        "input_method": input_method,
        "job_url": job_url,  # Add the URL to state
        "company_name": company_name,
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
    
    # Run the agent
    try:
        print("\n")
        final_state = resume_agent.invoke(initial_state)
        
        # Print summary
        print("\n" + "="*80)
        print("✓ PROCESS COMPLETE!")
        print("="*80)
        
        if final_state.get("output_files"):
            files = final_state["output_files"]
            print(f"\nYour tailored resume and cover letter have been saved:")
            print(f"\n  📄 Text file: {files['text_file']}")
            if files.get('pdf_file'):
                print(f"  📄 PDF file:  {files['pdf_file']}")
            else:
                print(f"  ⚠  PDF generation failed - using text file only")
            
            print(f"\n  Position:    {files.get('position', 'N/A')}")
            print(f"  Company:     {final_state.get('company_name', 'N/A')}")
        
        print("\n" + "="*80)
        print("\nThank you for using the Resume Tailoring Agent!")
        print("Good luck with your application! 🎉")
        print("="*80 + "\n")
        
    except KeyboardInterrupt:
        print("\n\n⚠ Process interrupted by user.")
        print("No files were saved.\n")
        sys.exit(1)
        
    except Exception as e:
        print(f"\n\n✗ An error occurred: {e}")
        print("\nPlease check your inputs and try again.")
        print("If the problem persists, check that:")
        print("  - Your .env file contains a valid OPENAI_API_KEY")
        print("  - The CV and cover letter guide PDFs are in the literature/ folder")
        print("  - You have internet connectivity")
        sys.exit(1)


if __name__ == "__main__":
    run_agent()

