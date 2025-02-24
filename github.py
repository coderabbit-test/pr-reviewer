from fastapi import HTTPException, logger
import requests


def get_pr_commits(repo_full_name, pr_number, github_token):
    """Fetch the list of commits for a PR from GitHub API."""
    url = f"https://api.github.com/repos/{repo_full_name}/pulls/{pr_number}/commits"
    print(url)
    headers = {"Authorization": f"{github_token}", "Accept": "application/vnd.github.v3+json"}

    response = requests.get(url, headers=headers)
    
    if response.status_code != 200:
        logger.error(f"Failed to fetch commits: {response.text}")
        raise HTTPException(status_code=500, detail="Error fetching PR commits")

    return response.json()
