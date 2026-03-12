import requests
import json
import logging
from typing import List, Dict, Any
from urllib.parse import urlparse

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class LinkValidator:
    def __init__(self, timeout: int = 5):
        self.timeout = timeout
        
        # Domains frequently used for web app deployment
        self.deployment_domains = [
            "vercel.app",
            "herokuapp.com",
            "netlify.app",
            "github.io",
            "onrender.com",
            "railway.app",
            "fly.dev",
            "firebaseapp.com",
            "web.app",
            "surge.sh"
        ]

    def _is_deployed_app(self, url: str) -> bool:
        """
        Heuristic to check if a URL is likely a live deployed app.
        Checks against known hosting providers, or if it's a generic WWW domain
        that is NOT github or linkedin.
        """
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.lower()
        
        if not domain:
            return False

        # If it's a GitHub repo or LinkedIn profile, it's not a deployed app endpoint
        if domain in ["github.com", "www.github.com", "linkedin.com", "www.linkedin.com"]:
            return False
            
        # Check against common free hosting domains
        for deploy_domain in self.deployment_domains:
            if deploy_domain in domain:
                return True
                
        # If it has a standard custom domain (not github/linkedin), assume deployed
        return True

    def validate_url(self, url: str) -> Dict[str, Any]:
        """
        Validates a single URL.
        """
        # Ensure it has a scheme
        if not url.startswith("http"):
            url_to_test = "http://" + url
        else:
            url_to_test = url

        result = {
            "url": url,
            "is_deployed_app": self._is_deployed_app(url_to_test),
            "status_code": None,
            "is_reachable": False,
            "error": None
        }

        try:
            response = requests.get(url_to_test, timeout=self.timeout, allow_redirects=True)
            result["status_code"] = response.status_code
            
            # Treat 200-399 as reachable (including redirects that resolve successfully)
            if response.ok or response.status_code < 400:
                result["is_reachable"] = True
            elif response.status_code == 403:  # Some sites block programmatic access
                 result["is_reachable"] = True
                 result["error"] = "Forbidden (403), likely reachable but blocked access."
        except requests.exceptions.Timeout:
             result["error"] = "Connection Timeout"
        except requests.exceptions.ConnectionError:
             result["error"] = "Connection Error (DNS or Server Down)"
        except Exception as e:
             result["error"] = str(e)

        return result

    def validate_links(self, urls: List[str]) -> Dict[str, Any]:
        """
        Takes a list of URLs and validates each of them.
        Returns a dictionary mapping the original URL to its status.
        """
        results = {}
        # Remove duplicates
        unique_urls = list(set(urls))
        
        for url in unique_urls:
            logging.info(f"Validating {url}...")
            results[url] = self.validate_url(url)
            
        return results

if __name__ == "__main__":
    validator = LinkValidator()
    
    test_urls = [
        "https://github.com/torvalds/linux",
        "https://my-awesome-app.vercel.app",
        "http://this-does-not-exist-123444.com",
        "linkedin.com/in/test"
    ]
    
    print("Testing Link Validator...")
    results = validator.validate_links(test_urls)
    print(json.dumps(results, indent=2))
