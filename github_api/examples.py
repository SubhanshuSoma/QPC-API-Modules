"""
GitHub API Examples

This module provides comprehensive examples of how to use the GitHub API client.
All examples include error handling and best practices.
"""

import os
from typing import Dict, List, Any
from github_client import GitHubClient
from utils.error_handling import APIError, AuthenticationError, RateLimitError


def basic_usage_example():
    """
    Basic usage example showing how to initialize and use the GitHub client.
    """
    print("=== GitHub API Basic Usage Example ===\n")
    
    try:
        # Initialize the client
        client = GitHubClient()
        print("✓ GitHub client initialized successfully")
        
        # Test connection
        if client.test_connection():
            print("✓ Connection to GitHub API successful")
        else:
            print("✗ Connection to GitHub API failed")
            return
        
        # Get authenticated user info
        print("\n--- Getting Authenticated User Info ---")
        try:
            user = client.get_user_info()
            print(f"Authenticated as: {user.get('login', 'Unknown')}")
            print(f"Name: {user.get('name', 'Unknown')}")
            print(f"Email: {user.get('email', 'Unknown')}")
            print(f"Public repos: {user.get('public_repos', 0)}")
        except APIError as e:
            print(f"Could not get user info: {e}")
        
    except AuthenticationError as e:
        print(f"✗ Authentication failed: {e}")
    except APIError as e:
        print(f"✗ API error: {e}")
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def user_management_example():
    """
    Example showing user management operations.
    """
    print("\n=== User Management Example ===\n")
    
    try:
        client = GitHubClient()
        
        # Get info for a specific user
        username = "octocat"
        print(f"--- Getting User Info for {username} ---")
        
        try:
            user = client.get_user_info(username)
            print(f"Username: {user.get('login', 'Unknown')}")
            print(f"Name: {user.get('name', 'Unknown')}")
            print(f"Bio: {user.get('bio', 'No bio')}")
            print(f"Location: {user.get('location', 'Unknown')}")
            print(f"Followers: {user.get('followers', 0)}")
            print(f"Following: {user.get('following', 0)}")
        except APIError as e:
            print(f"Could not get user info: {e}")
        
        # Get user repositories
        print(f"\n--- Getting Repositories for {username} ---")
        try:
            repos = client.get_user_repositories(username, per_page=5)
            print(f"Found {len(repos)} repositories:")
            for repo in repos:
                print(f"  - {repo.get('name', 'Unknown')}")
                print(f"    Description: {repo.get('description', 'No description')}")
                print(f"    Stars: {repo.get('stargazers_count', 0)}")
                print(f"    Language: {repo.get('language', 'Unknown')}")
                print()
        except APIError as e:
            print(f"Could not get repositories: {e}")
        
    except Exception as e:
        print(f"✗ Error in user management: {e}")


def repository_management_example():
    """
    Example showing repository management operations.
    """
    print("\n=== Repository Management Example ===\n")
    
    try:
        client = GitHubClient()
        
        # Get repository details
        owner = "octocat"
        repo_name = "Hello-World"
        print(f"--- Getting Repository Details ---")
        print(f"Repository: {owner}/{repo_name}")
        
        try:
            repo = client.get_repository(owner, repo_name)
            print(f"Name: {repo.get('name', 'Unknown')}")
            print(f"Description: {repo.get('description', 'No description')}")
            print(f"Stars: {repo.get('stargazers_count', 0)}")
            print(f"Forks: {repo.get('forks_count', 0)}")
            print(f"Language: {repo.get('language', 'Unknown')}")
            print(f"URL: {repo.get('html_url', 'Unknown')}")
        except APIError as e:
            print(f"Could not get repository details: {e}")
        
        # Create a new repository (commented out to avoid actual creation)
        print(f"\n--- Repository Creation Example ---")
        print("Note: Repository creation is commented out to avoid actual creation")
        """
        try:
            new_repo = client.create_repository(
                name="test-repo-example",
                description="A test repository created via API",
                private=True,
                auto_init=True
            )
            print(f"Created repository: {new_repo.get('html_url', 'Unknown')}")
        except APIError as e:
            print(f"Could not create repository: {e}")
        """
        
    except Exception as e:
        print(f"✗ Error in repository management: {e}")


def issue_management_example():
    """
    Example showing issue management operations.
    """
    print("\n=== Issue Management Example ===\n")
    
    try:
        client = GitHubClient()
        
        # Get repository issues
        owner = "octocat"
        repo_name = "Hello-World"
        print(f"--- Getting Issues for {owner}/{repo_name} ---")
        
        try:
            issues = client.get_repository_issues(owner, repo_name, state="open", per_page=5)
            print(f"Found {len(issues)} open issues:")
            for issue in issues:
                print(f"  Issue #{issue.get('number', 'Unknown')}: {issue.get('title', 'No title')}")
                print(f"    State: {issue.get('state', 'Unknown')}")
                print(f"    Created by: {issue.get('user', {}).get('login', 'Unknown')}")
                print(f"    Created: {issue.get('created_at', 'Unknown')}")
                print()
        except APIError as e:
            print(f"Could not get issues: {e}")
        
        # Create a new issue (commented out to avoid actual creation)
        print(f"--- Issue Creation Example ---")
        print("Note: Issue creation is commented out to avoid actual creation")
        """
        try:
            new_issue = client.create_issue(
                owner=owner,
                repo=repo_name,
                title="Test issue from API",
                body="This is a test issue created via the GitHub API",
                labels=["bug", "help wanted"]
            )
            print(f"Created issue #{new_issue.get('number', 'Unknown')}")
        except APIError as e:
            print(f"Could not create issue: {e}")
        """
        
    except Exception as e:
        print(f"✗ Error in issue management: {e}")


def pagination_example():
    """
    Example showing how to handle pagination for large datasets.
    """
    print("\n=== Pagination Example ===\n")
    
    try:
        client = GitHubClient()
        username = "octocat"
        
        print(f"--- Paginated Repository List for {username} ---")
        
        page = 1
        per_page = 3
        total_repos = 0
        
        while True:
            try:
                repos = client.get_user_repositories(username, per_page=per_page, page=page)
                
                if not repos:
                    break
                
                print(f"Page {page}:")
                for repo in repos:
                    print(f"  - {repo.get('name', 'Unknown')}")
                    total_repos += 1
                
                page += 1
                
                # Limit to first 3 pages for demo
                if page > 3:
                    break
                    
            except APIError as e:
                print(f"Error on page {page}: {e}")
                break
        
        print(f"\nTotal repositories found: {total_repos}")
        
    except Exception as e:
        print(f"✗ Error in pagination example: {e}")


def error_handling_example():
    """
    Example showing proper error handling for different scenarios.
    """
    print("\n=== Error Handling Example ===\n")
    
    try:
        client = GitHubClient()
        
        # Test with invalid username
        print("--- Testing with Invalid Username ---")
        try:
            client.get_user_info("invalid_username_that_does_not_exist_12345")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
        # Test with invalid repository
        print("\n--- Testing with Invalid Repository ---")
        try:
            client.get_repository("octocat", "non-existent-repo-12345")
        except APIError as e:
            print(f"✓ Properly caught API error: {e}")
        
        # Test with invalid parameters
        print("\n--- Testing with Invalid Parameters ---")
        try:
            client.get_user_repositories("octocat", per_page=0)
        except ValueError as e:
            print(f"✓ Properly caught validation error: {e}")
        
        # Test with invalid issue state
        print("\n--- Testing with Invalid Issue State ---")
        try:
            client.get_repository_issues("octocat", "Hello-World", state="invalid_state")
        except ValueError as e:
            print(f"✓ Properly caught validation error: {e}")
        
    except Exception as e:
        print(f"✗ Unexpected error: {e}")


def rate_limiting_example():
    """
    Example showing how the client handles rate limiting.
    """
    print("\n=== Rate Limiting Example ===\n")
    
    try:
        client = GitHubClient()
        
        print("--- Testing Rate Limit Handling ---")
        print("Making multiple requests to test rate limiting...")
        
        # Make multiple requests to potentially trigger rate limiting
        for i in range(5):
            try:
                user = client.get_user_info("octocat")
                print(f"  Request {i+1}: Success - User: {user.get('login', 'Unknown')}")
            except RateLimitError as e:
                print(f"  Request {i+1}: Rate limited - {e}")
                break
            except APIError as e:
                print(f"  Request {i+1}: API error - {e}")
                break
        
    except Exception as e:
        print(f"✗ Error in rate limiting test: {e}")


def main():
    """
    Run all examples.
    """
    print("GitHub API Examples")
    print("=" * 50)
    
    # Run all examples
    basic_usage_example()
    user_management_example()
    repository_management_example()
    issue_management_example()
    pagination_example()
    error_handling_example()
    rate_limiting_example()
    
    print("\n" + "=" * 50)
    print("All examples completed!")


if __name__ == "__main__":
    main() 