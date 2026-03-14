import os
import json
import logging
from typing import Dict, Any, Optional
from github import Github
from github.GithubException import GithubException
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load environment variables (useful for local testing)
load_dotenv()

class GitHubExtractor:
    def __init__(self, token: Optional[str] = None):
        """
        Initialize the GitHub API client.
        :param token: Optional GitHub Personal Access Token. If not provided, it tries to read GITHUB_TOKEN from env.
                      Without a token, rate limits are very strict (60 requests/hr).
        """
        self.token = token or os.getenv("GITHUB_TOKEN")
        if self.token:
            self.gh = Github(self.token, retry=0, timeout=15)
        else:
            logging.warning("No GitHub token provided. Rate limits will be severely restricted.")
            self.gh = Github(retry=0, timeout=15)

    def get_user_data(self, username: str) -> Dict[str, Any]:
        """
        Fetches public repositories, languages, and general stats for a given username.
        :param username: The GitHub username to search for.
        :return: A dictionary containing the extracted data.
        """
        try:
            user = self.gh.get_user(username)
            
            # Basic stats
            data: Dict[str, Any] = {
                "username": user.login,
                "name": user.name,
                "bio": user.bio,
                "public_repos_count": user.public_repos,
                "followers": user.followers,
                "following": user.following,
                "created_at": user.created_at.isoformat() if user.created_at else None,
                "top_languages": {},
                "repos": []
            }

            repos = user.get_repos()
            language_counts = {}

            # Iterate through public repositories
            for repo in repos:
                # We only want to analyze their own repos, not forks (usually) 
                is_fork = repo.fork
                
                repo_info = {
                    "name": repo.name,
                    "description": repo.description,
                    "url": repo.html_url,
                    "is_fork": is_fork,
                    "stars": repo.stargazers_count,
                    "language": repo.language,
                    "created_at": repo.created_at.isoformat() if repo.created_at else None,
                    "updated_at": repo.updated_at.isoformat() if repo.updated_at else None
                }
                data["repos"].append(repo_info)

                # Aggregate language data
                if repo.language:
                    language_counts[repo.language] = language_counts.get(repo.language, 0) + 1

            # Sort languages by frequency
            sorted_languages = dict(sorted(language_counts.items(), key=lambda item: item[1], reverse=True))
            data["top_languages"] = sorted_languages

            return data

        except GithubException as e:
            logging.error(f"GitHub API Error for user '{username}': {e}")
            return {"error": f"GitHub API Error: {e.status} - {e.data.get('message', 'Unknown Error')}"}
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            return {"error": str(e)}

if __name__ == "__main__":
    print("Testing GitHub Extractor...")
    extractor = GitHubExtractor()
    test_user = "torvalds"  # Example user
    print(f"Fetching data for {test_user}...")
    result = extractor.get_user_data(test_user)
    print(json.dumps(result, indent=2))
