"""
GitHub API Client

A comprehensive client for interacting with the GitHub API.
Provides repository and user management with secure authentication
and error handling.
"""

import requests
from typing import Dict, List, Optional, Any
from utils.auth import AuthManager
from utils.error_handling import (
    ErrorHandler, retry_on_failure, validate_input,
    APIError, AuthenticationError, RateLimitError
)


class GitHubClient:
    """
    Client for interacting with the GitHub API.
    
    Provides methods for managing repositories, users, and GitHub resources.
    Includes secure authentication, error handling, and retry logic.
    """
    
    def __init__(self, api_token: Optional[str] = None, base_url: str = "https://api.github.com"):
        """
        Initialize the GitHub API client.
        
        Args:
            api_token (Optional[str]): GitHub API token. If not provided, 
                                     will be loaded from environment variables.
            base_url (str): Base URL for the GitHub API
        """
        self.base_url = base_url
        self.api_token = api_token or AuthManager.get_github_token()
        
        # Validate token format
        if not AuthManager.validate_token_format(self.api_token, 'github'):
            raise ValueError("Invalid GitHub API token format")
        
        # Set up headers
        self.headers = {
            'Authorization': f'token {self.api_token}',
            'Accept': 'application/vnd.github.v3+json',
            'User-Agent': 'GitHub-API-Client/1.0'
        }
    
    @retry_on_failure(max_attempts=3)
    def get_user_info(self, username: Optional[str] = None) -> Dict[str, Any]:
        """
        Get information about a GitHub user.
        
        Args:
            username (Optional[str]): GitHub username. If not provided, 
                                    returns info for the authenticated user.
            
        Returns:
            Dict[str, Any]: User information
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If username is invalid
            
        Example:
            >>> client = GitHubClient()
            >>> user = client.get_user_info("octocat")
            >>> print(f"User: {user['login']} - {user['name']}")
        """
        if username and not isinstance(username, str):
            raise ValueError("Username must be a string")
        
        endpoint = f"/users/{username}" if username else "/user"
        url = f"{self.base_url}{endpoint}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            ErrorHandler.handle_rate_limit(response, "GitHub")
            return ErrorHandler.handle_response(response, "GitHub")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get user info: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_user_repositories(self, username: Optional[str] = None, 
                            per_page: int = 30, page: int = 1) -> List[Dict[str, Any]]:
        """
        Get repositories for a GitHub user.
        
        Args:
            username (Optional[str]): GitHub username. If not provided, 
                                    returns repos for the authenticated user.
            per_page (int): Number of repositories per page (max 100)
            page (int): Page number for pagination
            
        Returns:
            List[Dict[str, Any]]: List of repository objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If parameters are invalid
            
        Example:
            >>> client = GitHubClient()
            >>> repos = client.get_user_repositories("octocat", per_page=10)
            >>> for repo in repos:
            ...     print(f"Repo: {repo['name']} - {repo['description']}")
        """
        if username and not isinstance(username, str):
            raise ValueError("Username must be a string")
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            raise ValueError("per_page must be an integer between 1 and 100")
        if not isinstance(page, int) or page < 1:
            raise ValueError("page must be a positive integer")
        
        endpoint = f"/users/{username}/repos" if username else "/user/repos"
        url = f"{self.base_url}{endpoint}"
        params = {'per_page': per_page, 'page': page}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            ErrorHandler.handle_rate_limit(response, "GitHub")
            return ErrorHandler.handle_response(response, "GitHub")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get user repositories: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_repository(self, owner: str, repo: str) -> Dict[str, Any]:
        """
        Get detailed information about a specific repository.
        
        Args:
            owner (str): Repository owner username
            repo (str): Repository name
            
        Returns:
            Dict[str, Any]: Repository information
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If owner or repo is invalid
            
        Example:
            >>> client = GitHubClient()
            >>> repo = client.get_repository("octocat", "Hello-World")
            >>> print(f"Repository: {repo['name']} - Stars: {repo['stargazers_count']}")
        """
        if not owner or not isinstance(owner, str):
            raise ValueError("Owner must be a non-empty string")
        if not repo or not isinstance(repo, str):
            raise ValueError("Repository name must be a non-empty string")
        
        url = f"{self.base_url}/repos/{owner}/{repo}"
        
        try:
            response = requests.get(url, headers=self.headers, timeout=30)
            ErrorHandler.handle_rate_limit(response, "GitHub")
            return ErrorHandler.handle_response(response, "GitHub")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get repository {owner}/{repo}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def create_repository(self, name: str, description: Optional[str] = None,
                         private: bool = False, auto_init: bool = True) -> Dict[str, Any]:
        """
        Create a new repository for the authenticated user.
        
        Args:
            name (str): Repository name
            description (Optional[str]): Repository description
            private (bool): Whether the repository should be private
            auto_init (bool): Whether to initialize with README
            
        Returns:
            Dict[str, Any]: The created repository object
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If required parameters are missing
            
        Example:
            >>> client = GitHubClient()
            >>> new_repo = client.create_repository(
            ...     name="my-new-project",
            ...     description="A new project",
            ...     private=True
            ... )
            >>> print(f"Created repository: {new_repo['html_url']}")
        """
        if not name or not isinstance(name, str):
            raise ValueError("Repository name must be a non-empty string")
        
        url = f"{self.base_url}/user/repos"
        payload = {
            'name': name,
            'private': private,
            'auto_init': auto_init
        }
        
        if description:
            payload['description'] = description
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            ErrorHandler.handle_rate_limit(response, "GitHub")
            return ErrorHandler.handle_response(response, "GitHub")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create repository {name}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def get_repository_issues(self, owner: str, repo: str, 
                            state: str = "open", per_page: int = 30) -> List[Dict[str, Any]]:
        """
        Get issues for a specific repository.
        
        Args:
            owner (str): Repository owner username
            repo (str): Repository name
            state (str): Issue state ('open', 'closed', 'all')
            per_page (int): Number of issues per page (max 100)
            
        Returns:
            List[Dict[str, Any]]: List of issue objects
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If parameters are invalid
            
        Example:
            >>> client = GitHubClient()
            >>> issues = client.get_repository_issues("octocat", "Hello-World", state="open")
            >>> for issue in issues:
            ...     print(f"Issue #{issue['number']}: {issue['title']}")
        """
        if not owner or not isinstance(owner, str):
            raise ValueError("Owner must be a non-empty string")
        if not repo or not isinstance(repo, str):
            raise ValueError("Repository name must be a non-empty string")
        if state not in ['open', 'closed', 'all']:
            raise ValueError("State must be 'open', 'closed', or 'all'")
        if not isinstance(per_page, int) or per_page < 1 or per_page > 100:
            raise ValueError("per_page must be an integer between 1 and 100")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        params = {'state': state, 'per_page': per_page}
        
        try:
            response = requests.get(url, headers=self.headers, params=params, timeout=30)
            ErrorHandler.handle_rate_limit(response, "GitHub")
            return ErrorHandler.handle_response(response, "GitHub")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to get issues for {owner}/{repo}: {str(e)}")
    
    @retry_on_failure(max_attempts=3)
    def create_issue(self, owner: str, repo: str, title: str, 
                    body: Optional[str] = None, labels: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Create a new issue in a repository.
        
        Args:
            owner (str): Repository owner username
            repo (str): Repository name
            title (str): Issue title
            body (Optional[str]): Issue description
            labels (Optional[List[str]]): List of label names
            
        Returns:
            Dict[str, Any]: The created issue object
            
        Raises:
            AuthenticationError: If authentication fails
            APIError: If the API request fails
            ValidationError: If required parameters are missing
            
        Example:
            >>> client = GitHubClient()
            >>> issue = client.create_issue(
            ...     owner="octocat",
            ...     repo="Hello-World",
            ...     title="Bug report",
            ...     body="This is a bug description",
            ...     labels=["bug", "help wanted"]
            ... )
            >>> print(f"Created issue #{issue['number']}")
        """
        if not owner or not isinstance(owner, str):
            raise ValueError("Owner must be a non-empty string")
        if not repo or not isinstance(repo, str):
            raise ValueError("Repository name must be a non-empty string")
        if not title or not isinstance(title, str):
            raise ValueError("Title must be a non-empty string")
        
        url = f"{self.base_url}/repos/{owner}/{repo}/issues"
        payload = {'title': title}
        
        if body:
            payload['body'] = body
        if labels:
            payload['labels'] = labels
        
        try:
            response = requests.post(url, headers=self.headers, json=payload, timeout=30)
            ErrorHandler.handle_rate_limit(response, "GitHub")
            return ErrorHandler.handle_response(response, "GitHub")
        except requests.exceptions.RequestException as e:
            raise APIError(f"Failed to create issue in {owner}/{repo}: {str(e)}")
    
    def test_connection(self) -> bool:
        """
        Test the connection to the GitHub API.
        
        Returns:
            bool: True if connection is successful, False otherwise
            
        Example:
            >>> client = GitHubClient()
            >>> if client.test_connection():
            ...     print("Connection successful!")
            ... else:
            ...     print("Connection failed!")
        """
        try:
            # Try to get authenticated user info as a connection test
            self.get_user_info()
            return True
        except Exception:
            return False 