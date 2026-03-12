import json
import logging
import argparse
from typing import Dict, Any, List, Optional

# Import all our modules
from github_extractor import GitHubExtractor
from resume_extractor import ResumeExtractor
from link_validator import LinkValidator
from video_transcriber import VideoTranscriber

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SkillAnalyzerPipeline:
    def __init__(self):
        logging.info("Initializing Backend Pipeline modules...")
        self.github_ext = GitHubExtractor()
        self.resume_ext = ResumeExtractor()
        self.link_val = LinkValidator()
        self.video_ts = VideoTranscriber(model_size="base") # Use 'base' for faster processing 
        logging.info("Modules Initialized.")

    def run_pipeline(self, 
                    github_username: Optional[str] = None, 
                    resume_pdf_path: Optional[str] = None, 
                    video_urls: Optional[List[str]] = None,
                    extra_urls: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Runs the full backend extraction and cleaning pipeline.
        """
        final_output: Dict[str, Any] = {
            "github_data": None,
            "resume_data": None,
            "link_validation": None,
            "video_transcripts": []
        }

        urls_to_validate = []

        # 1. Process GitHub
        if github_username:
            logging.info(f"==> Processing GitHub for {github_username}...")
            final_output["github_data"] = self.github_ext.get_user_data(github_username)
            # Add repos to URL validation list
            if "repos" in final_output["github_data"] and isinstance(final_output["github_data"]["repos"], list):
                # Don't validate GitHub repo URLs, as they are mostly up, but maybe add homepage links
                pass

        # 2. Process Resume
        if resume_pdf_path:
            logging.info(f"==> Processing Resume {resume_pdf_path}...")
            resume_data = self.resume_ext.process_resume(resume_pdf_path)
            final_output["resume_data"] = resume_data
            if "extracted_urls" in resume_data:
                urls_to_validate.extend(resume_data["extracted_urls"])

        # 3. Process Extra URLs
        if extra_urls:
            urls_to_validate.extend(extra_urls)

        # 4. Validate URLs
        if urls_to_validate:
            logging.info(f"==> Validating {len(urls_to_validate)} URLs...")
            final_output["link_validation"] = self.link_val.validate_links(urls_to_validate)

        # 5. Process Videos
        if video_urls:
            for v_url in video_urls:
                logging.info(f"==> Transcribing Video {v_url}...")
                ts_data = self.video_ts.transcribe_video(v_url)
                final_output["video_transcripts"].append(ts_data)

        logging.info("==> Pipeline processing complete.")
        return final_output

def main():
    parser = argparse.ArgumentParser(description="AI Skill Analyzer - Backend Pipeline")
    parser.add_argument("--github", type=str, help="GitHub username to extract data from")
    parser.add_argument("--resume", type=str, help="Path to the resume PDF")
    parser.add_argument("--videos", type=str, nargs="+", help="List of video URLs to transcribe")
    parser.add_argument("--urls", type=str, nargs="+", help="List of extra URLs to validate")
    parser.add_argument("--out", type=str, default="backend_output.json", help="Output JSON file path")
    
    args = parser.parse_args()

    # If no arguments provided, print help
    if not (args.github or args.resume or args.videos or args.urls):
        parser.print_help()
        return

    pipeline = SkillAnalyzerPipeline()
    
    results = pipeline.run_pipeline(
        github_username=args.github,
        resume_pdf_path=args.resume,
        video_urls=args.videos,
        extra_urls=args.urls
    )

    # Save to file
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2)
        
    logging.info(f"Results saved to {args.out}")

if __name__ == "__main__":
    main()
