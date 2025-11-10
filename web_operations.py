from dotenv import load_dotenv
import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus, urlparse
import re
from langchain_openai import ChatOpenAI

load_dotenv()

# Initialize LLM for company extraction (lazy loaded)
_company_extractor_llm = None

def get_company_extractor_llm():
    """Get LLM instance for company name extraction."""
    global _company_extractor_llm
    if _company_extractor_llm is None:
        _company_extractor_llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    return _company_extractor_llm


def extract_company_with_llm(job_description: str, url: str = None) -> str:
    """
    Use LLM to intelligently extract company name from job description.
    
    Args:
        job_description: The job description text
        url: Optional URL for additional context
        
    Returns:
        Company name or None if extraction fails
    """
    try:
        llm = get_company_extractor_llm()
        
        # Take first 1000 characters for faster processing
        text_sample = job_description[:1000]
        
        prompt = f"""Extract the company name from this job posting. Return ONLY the company name, nothing else.
If you cannot find a company name, return "NONE".

Job posting:
{text_sample}"""
        
        if url:
            prompt += f"\n\nURL: {url}"
        
        response = llm.invoke(prompt)
        company_name = response.content.strip()
        
        # Validate response
        if (company_name and 
            company_name.upper() != "NONE" and 
            3 < len(company_name) < 100 and
            not company_name.startswith("I ") and
            not company_name.startswith("The ")):
            return company_name
        
    except Exception as e:
        print(f"LLM company extraction failed: {e}")
    
    return None


def fetch_job_description_from_url(url: str) -> str:
    """
    Fetch job description from a URL using BeautifulSoup.
    Falls back to BrightData API if simple scraping fails.
    
    Args:
        url: URL of the job posting
        
    Returns:
        Extracted job description text
    """
    try:
        # First try simple requests + BeautifulSoup
        print(f"Fetching job description from URL: {url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(['script', 'style', 'header', 'footer', 'nav']):
            script.decompose()
        
        # Try to find job description in common container classes/ids
        job_containers = [
            soup.find('div', {'class': lambda x: x and 'job-description' in x.lower()}),
            soup.find('div', {'id': lambda x: x and 'job-description' in x.lower()}),
            soup.find('div', {'class': lambda x: x and 'description' in x.lower()}),
            soup.find('section', {'class': lambda x: x and 'job' in x.lower()}),
            soup.find('article'),
            soup.find('main')
        ]
        
        # Use first non-None container
        container = next((c for c in job_containers if c), None)
        
        if container:
            text = container.get_text(separator='\n', strip=True)
        else:
            # Fallback: get all text from body
            text = soup.get_text(separator='\n', strip=True)
        
        # Clean up the text
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        cleaned_text = '\n'.join(lines)
        
        if len(cleaned_text) < 100:
            raise ValueError("Extracted text too short, likely failed to parse properly")
        
        print(f"Successfully extracted {len(cleaned_text)} characters")
        return cleaned_text
        
    except Exception as e:
        print(f"BeautifulSoup scraping failed: {e}")
        print("Attempting to use BrightData API...")
        return fetch_with_brightdata(url)

def fetch_with_brightdata(url: str) -> str:
    """
    Fallback method using BrightData API for more complex pages.
    
    Args:
        url: URL of the job posting
        
    Returns:
        Extracted job description text
    """
    api_key = os.getenv("BRIGHTDATA_API_KEY")
    
    if not api_key:
        raise ValueError("BrightData API key not found. Please set BRIGHTDATA_API_KEY in .env file")
    
    api_url = "https://api.brightdata.com/request"
    
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json",
    }
    
    payload = {
        "zone": "ai_agent2",
        "url": f"{url}?brd_json=1",
        "format": "raw"
    }
    
    try:
        response = requests.post(api_url, headers=headers, json=payload, timeout=30)
        response.raise_for_status()
        data = response.json()
        
        # Extract text from BrightData response
        # This will vary based on the response structure
        if isinstance(data, dict):
            text = data.get('text', '')
            if not text:
                # Try to concatenate all text values
                text = ' '.join(str(v) for v in data.values() if isinstance(v, str))
        else:
            text = str(data)
        
        if len(text) < 100:
            raise ValueError("BrightData extraction failed or returned insufficient data")
        
        print(f"BrightData extraction successful: {len(text)} characters")
        return text
        
    except Exception as e:
        raise ValueError(f"Failed to fetch job description using BrightData: {e}")

def extract_company_name_with_llm(job_description: str, url: str = None) -> str:
    """
    Use LLM to extract company name from job description.
    Fast and accurate using gpt-4o-mini.
    
    Args:
        job_description: The job description text
        url: Optional URL of the job posting
        
    Returns:
        Extracted company name or None if extraction fails
    """
    try:
        llm = get_llm()
        
        # Create a concise prompt
        prompt = f"""Extract the company/organization name from this job posting. 
Return ONLY the company name, nothing else. If you cannot determine the company name with confidence, return "UNKNOWN".

Job posting:
{job_description[:2000]}"""  # Use first 2000 chars to keep it fast

        if url:
            prompt += f"\n\nURL: {url}"
        
        response = llm.invoke(prompt)
        company_name = response.content.strip()
        
        # Validate the response
        if company_name and company_name != "UNKNOWN" and len(company_name) < 100:
            return sanitize_filename(company_name)
        
        return None
        
    except Exception as e:
        print(f"  LLM extraction failed: {e}")
        return None


def extract_company_name_from_url(url: str) -> str:
    """
    Extract company name from URL using domain patterns.
    
    Args:
        url: Job posting URL
        
    Returns:
        Company name from URL or None
    """
    try:
        parsed = urlparse(url)
        domain = parsed.netloc.lower()
        
        # Remove common prefixes
        domain = domain.replace('www.', '').replace('jobs.', '').replace('careers.', '')
        
        # Known job board patterns
        job_boards = {
            'linkedin.com': None,
            'indeed.com': None,
            'glassdoor.com': None,
            'monster.com': None,
            'ziprecruiter.com': None,
            'careerbuilder.com': None,
            'simplyhired.com': None,
            'lever.co': None,
            'greenhouse.io': None,
            'workday.com': None,
            'icims.com': None,
        }
        
        # Check if it's a job board
        for board in job_boards:
            if board in domain:
                return None  # Can't extract from job boards
        
        # Extract company name from domain
        # Remove TLD
        company_domain = domain.split('.')[0]
        
        # Clean up and capitalize
        company_name = company_domain.replace('-', ' ').replace('_', ' ').title()
        
        if len(company_name) > 3:  # Reasonable company name
            return company_name
            
    except:
        pass
    
    return None


def extract_company_name_from_text(job_description: str, url: str = None) -> str:
    """
    Extract company name from job description text or URL.
    Uses LLM as primary method, with regex patterns as fallback.
    
    Args:
        job_description: The job description text
        url: Optional URL of the job posting
        
    Returns:
        Extracted company name or "Unknown_Company"
    """
    # Method 1: Try LLM extraction (most accurate)
    print("  Extracting company name with LLM...")
    llm_company = extract_company_with_llm(job_description, url)
    if llm_company:
        print(f"  ✓ LLM extracted: {llm_company}")
        return sanitize_filename(llm_company)
    
    print("  LLM extraction unsuccessful, trying pattern matching...")
    
    # Method 2: Try URL extraction if provided
    if url:
        url_company = extract_company_name_from_url(url)
        if url_company:
            return sanitize_filename(url_company)
    
    lines = job_description.split('\n')
    
    # Pattern 1: Look for "Company:" or "Company Name:" patterns
    for i, line in enumerate(lines[:30]):
        line_stripped = line.strip()
        line_lower = line.lower()
        
        # Direct company indicator
        if any(pattern in line_lower for pattern in ['company:', 'company name:', 'organization:']):
            company = re.split(r'[:]\s*', line_stripped, 1)
            if len(company) > 1:
                company_name = company[1].strip()
                if 3 < len(company_name) < 50:
                    return sanitize_filename(company_name)
        
        # Pattern: "at [Company]" or "@ [Company]" or "@Company"
        if re.match(r'^(at|@)\s*[A-Z]', line_stripped, re.IGNORECASE):
            company = re.split(r'^(at|@)\s*', line_stripped, maxsplit=1, flags=re.IGNORECASE)
            if len(company) > 2:
                company_name = company[2].strip()
                if 3 < len(company_name) < 50 and not any(word in company_name.lower() for word in ['the', 'this', 'our']):
                    return sanitize_filename(company_name)
        
        # Pattern: Line that looks like a company name (capitalized, reasonable length)
        if i < 10 and line_stripped:  # First 10 lines only
            # Skip if it looks like a job title
            if any(title in line_lower for title in ['engineer', 'developer', 'manager', 'analyst', 'specialist', 'designer', 'director', 'scientist', 'architect', 'lead', 'senior', 'junior', 'intern']):
                continue
            
            # Check if it's a properly formatted company name
            if (line_stripped[0].isupper() and 
                3 < len(line_stripped) < 50 and
                not line_stripped.endswith(':') and
                not line_lower.startswith(('http', 'www', 'posted', 'date', 'location', 'salary', 'benefits', 'apply'))):
                
                # Check if next line might be a location (supports company name)
                if i + 1 < len(lines):
                    next_line = lines[i + 1].strip()
                    if any(location_word in next_line.lower() for location_word in ['location:', 'city', 'remote', 'hybrid', ', CA', ', NY', ', TX']):
                        return sanitize_filename(line_stripped)
    
    # Pattern 2: Look for company mentions in sentences
    # Common patterns: "Join [Company]", "Work at [Company]", "[Company] is looking"
    text_sample = ' '.join(lines[:50])  # First 50 lines
    
    patterns = [
        r'join\s+([A-Z][A-Za-z\s&]{2,40}?)(?:\s+as|\s+to|\s+and)',
        r'work\s+(?:at|for)\s+([A-Z][A-Za-z\s&]{2,40}?)(?:\s+as|\s+to|\s+and|\s+is)',
        r'([A-Z][A-Za-z\s&]{2,40}?)\s+is\s+(?:looking|hiring|seeking)',
        r'welcome\s+to\s+([A-Z][A-Za-z\s&]{2,40}?)[\.\!]',
        r'about\s+([A-Z][A-Za-z\s&]{2,40}?)(?:\s+About|\s+Our|\s+The)',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, text_sample, re.IGNORECASE)
        if match:
            company = match.group(1).strip()
            if 3 < len(company) < 50:
                return sanitize_filename(company)
    
    # Pattern 3: Look for company in title tags or meta information
    # This would require HTML parsing, but we're working with text
    
    # Pattern 4: Smart extraction - find capitalized entity that appears multiple times
    words = re.findall(r'\b[A-Z][A-Za-z]{2,}\b', ' '.join(lines[:50]))
    if words:
        # Find most common capitalized word that's not a common word
        common_words = {'The', 'This', 'Our', 'We', 'Are', 'You', 'Your', 'Will', 'About', 'Join', 'Work', 'Team', 'Role', 'Job', 'Position', 'Requirements', 'Responsibilities'}
        candidate_words = [w for w in words if w not in common_words]
        
        if candidate_words:
            # Use most frequent
            from collections import Counter
            word_counts = Counter(candidate_words)
            most_common = word_counts.most_common(3)
            
            for word, count in most_common:
                if count >= 2 and 3 < len(word) < 30:  # Appears at least twice
                    return sanitize_filename(word)
    
    return "Unknown_Company"

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

