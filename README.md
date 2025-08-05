# API Modules

A collection of reusable API modules for Coda, GitHub, and Google Calendar with secure authentication, error handling, and comprehensive documentation.

## Overview

This project contains three API modules:
- **Coda API** - Document and database management
- **GitHub API** - Repository and user management
- **Google Calendar API** - Calendar and event management

## Project Structure

```
API_Modules/
├── README.md
├── .env.example
├── requirements.txt
├── coda_api/
│   ├── __init__.py
│   ├── coda_client.py
│   └── examples.py
├── github_api/
│   ├── __init__.py
│   ├── github_client.py
│   └── examples.py
├── google_calendar_api/
│   ├── __init__.py
│   ├── calendar_client.py
│   └── examples.py
└── utils/
    ├── __init__.py
    ├── auth.py
    └── error_handling.py
```

## Setup

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Environment Configuration**
   ```bash
   cp .env.example .env
   ```
   
   Then edit `.env` with your API keys:
   ```
   # Coda API
   CODA_API_TOKEN=your_coda_token_here
   
   # GitHub API
   GITHUB_TOKEN=your_github_token_here
   
   # Google Calendar API
   GOOGLE_CALENDAR_CREDENTIALS_FILE=path_to_credentials.json
   ```

## Usage

Each API module can be imported and used independently:

```python
from coda_api import CodaClient
from github_api import GitHubClient
from google_calendar_api import GoogleCalendarClient

# Initialize clients
coda = CodaClient()
github = GitHubClient()
calendar = GoogleCalendarClient()

# Use the APIs
documents = coda.list_documents()
repos = github.get_user_repositories()
events = calendar.list_events()
```

## Features

- **Secure Authentication**: All API keys loaded from environment variables
- **Error Handling**: Comprehensive error handling with retry logic
- **Documentation**: Full docstrings and usage examples
- **Modular Design**: Each API is self-contained and reusable
- **Type Hints**: Full type annotations for better IDE support

## Examples

See the `examples.py` files in each module directory for detailed usage examples.

## Error Handling

All modules include:
- Rate limiting handling
- Network error retries
- Authentication error handling
- Input validation

## Contributing

When adding new API modules:
1. Create a new directory with the API name
2. Include `__init__.py`, `client.py`, and `examples.py`
3. Add authentication setup to `utils/auth.py`
4. Update this README with new module information
