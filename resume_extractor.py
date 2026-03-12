import pdfplumber
import re
import json
import logging
from typing import Dict, List, Any

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class ResumeExtractor:
    def __init__(self):
        # A rudimentary list of known skills/languages for basic matching
        self.known_skills = [
            'python', 'java', 'c++', 'c#', 'javascript', 'typescript', 'go', 'ruby', 'rust',
            'swift', 'kotlin', 'php', 'html', 'css', 'react', 'angular', 'vue', 'node.js',
            'django', 'flask', 'spring', 'sql', 'mysql', 'postgresql', 'mongodb', 'docker',
            'kubernetes', 'aws', 'azure', 'gcp', 'git', 'linux', 'machine learning', 'pytorch',
            'tensorflow', 'pandas', 'numpy', 'express', 'fastapi'
        ]
        
        # Regex to find common URL patterns
        self.url_regex = re.compile(
            r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+'
            r'|(?:www\.)?(?:github\.com|linkedin\.com)/[a-zA-Z0-9_-]+'
        )

    def extract_text_from_pdf(self, pdf_path: str) -> str:
        """Extract all text from a PDF file."""
        text = ""
        try:
            with pdfplumber.open(pdf_path) as pdf:
                for page in pdf.pages:
                    page_text = page.extract_text()
                    if page_text:
                        text += page_text + "\n"
            return text
        except Exception as e:
            logging.error(f"Failed to extract text from {pdf_path}: {e}")
            return ""

    def clean_text(self, text: str) -> str:
        """Basic text cleaning."""
        # Replace non-breaking spaces, multiple newlines, etc.
        text = re.sub(r'\s+', ' ', text)
        return text.strip()

    def extract_skills(self, text: str) -> List[str]:
        """Simple keyword matching for skills."""
        text_lower = text.lower()
        found_skills = set()
        
        for skill in self.known_skills:
            escaped_skill = re.escape(skill)
            if re.search(rf'(?:\b|(?<=\W)){escaped_skill}(?:\b|(?=\W))', text_lower):
                found_skills.add(skill)
                
        return list(found_skills)

    def extract_urls(self, text: str) -> List[str]:
        """Extract URLs found in the text."""
        urls = self.url_regex.findall(text)
        # Deduplicate and clean
        clean_urls = set()
        for url in urls:
            if url.startswith('github.com') or url.startswith('www.github.com') or \
               url.startswith('linkedin.com') or url.startswith('www.linkedin.com'):
                if not url.startswith('http'):
                    url = 'https://' + url.replace('www.', '')
            clean_urls.add(url)
        return list(clean_urls)

    def process_resume(self, pdf_path: str) -> Dict[str, Any]:
        """
        Main pipeline to process a resume PDF.
        """
        raw_text = self.extract_text_from_pdf(pdf_path)
        if not raw_text:
            return {"error": "Could not extract text from the provided PDF."}

        cleaned_text = self.clean_text(raw_text)
        
        skills = self.extract_skills(raw_text)
        urls = self.extract_urls(raw_text)
        
        return {
            "source_file": pdf_path,
            "skills_found": skills,
            "extracted_urls": urls,
            "raw_text_length": len(raw_text),
            "cleaned_text": cleaned_text
        }

if __name__ == "__main__":
    import sys
    extractor = ResumeExtractor()
    
    if len(sys.argv) > 1:
        test_pdf = sys.argv[1]
        print(f"Processing {test_pdf}...")
        result = extractor.process_resume(test_pdf)
        print(json.dumps(result, indent=2))
    else:
        print("Usage: python resume_extractor.py <path_to_resume.pdf>")
