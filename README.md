# Supervaize Hello World

This is the hello world project for Supervaize - a FastAPI application demonstrating how to build and deploy agents with Supervaize.

## Getting Started

### Prerequisites

- Python 3.12 or higher
- [uv](https://github.com/astral-sh/uv) package manager

### Local Development

1. **Set up the virtual environment with uv:**

   ```bash
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

2. **Install dependencies:**

   ```bash
   uv pip install -e .
   ```

3. **Start the Supervaizer server:**

   ```bash
   supervaizer start
   ```

   Your application will be available at `http://localhost:8000` (or the port configured in your `supervaizer_control.py`).

### Configuration

Edit `supervaizer_control.py` to configure your agent(s). See the [Supervaize documentation](https://doc.supervaize.com) for detailed configuration options and examples.

## Documentation

For more information, troubleshooting, and advanced usage, visit the [Supervaize documentation](https://doc.supervaize.com).

## Deployment

### Deploy with Vercel

This project is configured to deploy easily on Vercel:

[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https%3A%2F%2Fgithub.com%2Fvercel%2Fexamples%2Ftree%2Fmain%2Fpython%2Ffastapi&demo-title=FastAPI&demo-description=Use%20FastAPI%20on%20Vercel%20with%20Serverless%20Functions%20using%20the%20Python%20Runtime.&demo-url=https%3A%2F%2Fvercel-plus-fastapi.vercel.app%2F&demo-image=https://assets.vercel.com/image/upload/v1669994600/random/python.png)

1. **Install Vercel CLI (optional, for local testing):**

   ```bash
   npm i -g vercel
   ```

2. **Deploy:**

   ```bash
   vercel
   ```

   Or use the one-click deploy button above to deploy directly from GitHub.

For more information about deploying FastAPI applications on Vercel, see the [Vercel Python Runtime documentation](https://vercel.com/docs/concepts/functions/serverless-functions/runtimes/python).
