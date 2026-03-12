# AI Skill Analyzer - Backend Data Collection Pipeline

This repository contains the backend data collection and cleaning modules for the **AI Skill Analyzer** project. These scripts fetch, extract, and clean data from various sources (GitHub, Resumes, Web Links, and Demo Videos) to output a unified JSON structure for downstream AI evaluation and UI rendering.

## Setup & Installation

**Prerequisites:**
- Python 3.10+
- [FFmpeg](https://ffmpeg.org/download.html) (strictly required for `yt-dlp` and `whisper` to transcribe audio)

**1. Create virtual environment and install dependencies:**
```bash
python -m venv venv
# On Windows
.\venv\Scripts\activate
# On Mac/Linux
source venv/bin/activate

pip install -r requirements.txt
```

**2. Configure Environment Variables:**
Rename `.env.template` to `.env` and add your GitHub Personal Access Token.
```bash
GITHUB_TOKEN=your_token_here
```
*(Without a token, GitHub strictly limits API requests to 60/hr. With a token, you get 5000/hr).*

## Usage

### 1. Unified Pipeline (`main.py`)

The easiest way to use the backend is the `main.py` orchestrator script. It runs all modules concurrently based on the arguments you provide.

```bash
python main.py --github "torvalds" --resume "path/to/resume.pdf" --videos "https://youtu.be/..." --urls "https://myapp.vercel.app" --out "student_data.json"
```

**Arguments:**
- `--github`: GitHub username to extract stats and repos.
- `--resume`: Path to the student's resume PDF.
- `--videos`: One or more video URLs (spaced) to transcribe.
- `--urls`: One or more web URLs (spaced) to validate deployment status.
- `--out`: Output JSON file name (default is `backend_output.json`).

### 2. Individual Modules

You can also import and construct the modules independently in your own scripts or FastAPI endpoints:

#### GitHub Extractor
Fetches profile info, repositories, and aggregates language usage.
```python
from github_extractor import GitHubExtractor
extractor = GitHubExtractor()
data = extractor.get_user_data("username")
```

#### Resume Extractor
Extracts raw text, identifies programming skills based on keywords, and extracts URLs for validation.
```python
from resume_extractor import ResumeExtractor
extractor = ResumeExtractor()
data = extractor.process_resume("resume.pdf")
```

#### Link Validator
Checks the HTTP status of URLs and uses heuristics to guess if the link is a hosted web application.
```python
from link_validator import LinkValidator
validator = LinkValidator()
status_map = validator.validate_links(["https://app.vercel.app", "https://github.com/repo"])
```

#### Video Transcriber
Downloads audio from YouTube or demo links via `yt-dlp` and runs OpenAI's `whisper` model locally to transcribe the demo.
```python
from video_transcriber import VideoTranscriber
transcriber = VideoTranscriber(model_size="base") # Use 'tiny' for speed or 'small'/'medium' for accuracy
transcript = transcriber.transcribe_video("https://youtu.be/demo")
```
