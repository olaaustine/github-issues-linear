# github-issues-linear

## Overview

github-issues-linear is an automation tool designed to synchronize issues from a GitHub repository to a Linear workspace. The application is intended for teams that use GitHub for code management and Linear for project tracking, providing seamless integration between the two platforms. It is scheduled to run every day at 8am using APScheduler, ensuring that new or updated GitHub issues are reflected in Linear without manual intervention.

## Purpose

This project addresses the common need for engineering and product teams to keep their issue tracking systems in sync. By automating the transfer of issues from GitHub to Linear, it eliminates the need for manual copying, reduces the risk of missing important updates, and ensures that all stakeholders have a unified view of ongoing work.

## Features
- **Automated Issue Sync:** Fetches issues from a specified GitHub repository and creates corresponding issues in a Linear team.
- **Scheduled Execution:** Uses APScheduler to run the sync process every day at 8am, ensuring up-to-date information in Linear.
- **Error Handling:** Provides clear error messages for authentication issues, API errors, and data mismatches.
- **Redis Integration:** Uses Redis to cache and track the status of issues between GitHub and Linear, enabling efficient status checks and updates.
- **Dockerized Deployment:** Easily deployable as a Docker container for consistent and reproducible environments.
- **Modern Python:** Built for Python 3.13+ and leverages Pydantic for data validation.

## How It Works
1. **Configuration:**
   - Set up your GitHub and Linear API credentials in the configuration file or environment variables.
   - Specify the GitHub repository and Linear team to sync.
   - Ensure Redis is running and accessible to the application (see below).
2. **Execution:**
   - The application uses PyGithub to fetch issues from the GitHub repository.
   - For each issue, it creates a corresponding issue in Linear using the Linear API.
   - Issue status and metadata are cached in Redis for efficient lookups and updates.
   - The process is scheduled to run daily at 8am using APScheduler.
3. **Deployment:**
   - The application can be run locally or deployed using Docker for production use.

## Setup Instructions

### Prerequisites
- Python 3.13+
- GitHub Personal Access Token with repo access
- Linear API Key
- **Redis server running and accessible** (default: `localhost:6379`)

### Installation
1. **Clone the repository:**
   ```sh
   git clone https://github.com/olaaustine/github-issues-linear.git
   cd github-issues-linear
   ```
2. **Install dependencies:**
   ```sh
   pip install -r requirements.txt
   ```
   Or, if using `uv`:
   ```sh
   uv pip install --system --requirements requirements.txt
   ```
3. **Configure environment variables:**
   - Set `GITHUB_TOKEN`, `LINEAR_API_KEY`, `GITHUB_REPOSITORY`, and `LINEAR_TEAM_ID` as environment variables or in a `.env` file.
   - Example `.env`:
     ```env
     GITHUB_TOKEN=ghp_xxx
     LINEAR_API_KEY=lin_api_xxx
     GITHUB_REPOSITORY=your-org/your-repo
     LINEAR_TEAM_ID=your-linear-team-id
     REDIS_URL=redis://localhost:6379/0
     ```
   - If using Docker Compose, ensure your `docker-compose.yml` includes a Redis service.

### Running the Application
- **Locally:**
  ```sh
  python main.py
  ```
- **With Docker:**
  1. Build and start all services (including Redis) using Docker Compose:
     ```sh
     docker-compose up --build
     ```
  2. Run the main application container (if not using Compose for everything):
     ```sh
     docker run --env-file .env github-issues-linear
     ```
  3. Run tests inside the container:
     ```sh
     docker run github-issues-linear pytest
     ```

## Configuration
- All configuration options (API keys, repository, team ID, Redis URL) can be set via environment variables or a config file in `src/config.py`.
- The sync schedule is set to 8am daily by default using APScheduler. This can be changed in the scheduler setup in `main.py`.
- Dependencies are managed in `pyproject.toml` and `requirements.txt`.

## Redis Usage
- Redis is used to cache issue status and metadata for efficient syncing between GitHub and Linear.
- Each issue is stored in Redis with a key like `github_issue:{issue_title}` and a JSON value containing fields such as `linear_id`, `linear_url`, and `linear_status`.
- Ensure Redis is running before starting the application. You can use the provided `redis.conf` or a Dockerized Redis instance.

## Testing
- **Unit tests** are located in `src/tests/`.
- **Important:** To avoid real API and Redis calls during testing:
  - Patch `requests.post` in your tests to mock external HTTP requests.
  - Mock the config object by assigning a `MagicMock` to the service instance's config attribute.
  - Patch or mock `redis_client` in tests that would otherwise connect to a real Redis server.
- Example for patching in tests:
  ```python
  @patch("src.linear.linear.requests.post")
  def test_something(mock_post):
      mock_post.return_value = MagicMock(status_code=200, json=lambda: {...})
      ...
  ```
- If you see Redis connection errors in tests, ensure you are patching or mocking `redis_client`.

## Scheduler Customization
- The sync job is scheduled using APScheduler. To change the time or frequency, edit the scheduler setup in `main.py`.
- Example (in `main.py`):
  ```python
  scheduler.add_job(sync_issues, 'cron', hour=8, minute=0)
  ```

## Troubleshooting
- **401 Unauthorized:** Check that your GitHub and Linear API tokens are correct and have the required permissions.
- **404 Not Found:** Ensure the repository and team IDs are correct and accessible.
- **400 Bad Request:** Check the data being sent to the Linear API matches the expected schema.
- **PaginatedList errors:** When using PyGithub, make sure to iterate over the PaginatedList to access individual issues.
- **Python Version:** This project requires Python 3.13+ as specified in `pyproject.toml`.
- **Redis ConnectionError in tests:** Patch or mock `redis_client` in your tests to avoid real Redis connections.

## Contributing
Pull requests and issues are welcome! Please open an issue to discuss your proposed changes before submitting a PR.

## License
MIT License. See [LICENSE](LICENSE) for details.

## Support
For technical support, please open an issue in this repository or contact the maintainer.
