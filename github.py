from fastapi import HTTPException
import requests
import time
import logging

logger = logging.getLogger(__name__)

def get_pr_commits(repo_full_name: str, pr_number: int, github_token: str, retries: int = 3, backoff_factor: float = 0.5):
    """Fetch the list of commits for a PR from GitHub API with retries and exception handling."""
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/commits"
    headers = {
        "Authorization": f"{github_token}",
        "Accept": "application/vnd.github.v3+json"
    }

    for attempt in range(retries):
        try:
            response = requests.get(url, headers=headers, timeout=10)
            if response.status_code == 200:
                return response.json()
            else:
                logger.warning(f"Attempt {attempt + 1}: GitHub API returned {response.status_code} - {response.text}")
        except requests.exceptions.RequestException as e:
            logger.warning(f"Attempt {attempt + 1}: Request failed with exception: {e}")

        sleep_time = backoff_factor * (2 ** attempt)
        time.sleep(sleep_time)

    # If all retries fail
    logger.error(f"Failed to fetch commits for PR #{pr_number} in {repo_full_name} after {retries} attempts.")
    raise HTTPException(status_code=502, detail="Failed to fetch PR commits from GitHub")
