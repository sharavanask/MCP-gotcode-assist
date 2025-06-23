import httpx
from mcp.server.fastmcp import FastMCP
from urllib.parse import urlparse


# Initialize MCP Server
mcp = FastMCP("assistcode")
# Hugging Face API Info
HF_API_TOKEN = "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"
HF_API_URL = "https://api-inference.huggingface.co/models/mistralai/Mixtral-8x7B-Instruct-v0.1"
HEADERS = {"Authorization": f"Bearer {HF_API_TOKEN}"}


@mcp.tool()
def fix_code_from_github(github_url: str, filepath: str, branch: str = "main") -> str:
    """
    Fetches Python code from GitHub and uses Mixtral to clean and fix it.

    Args:
        github_url: GitHub repo URL (e.g., https://github.com/user/repo)
        filepath: Path to file in repo (e.g., Fthree.py, src/main.py)
        branch: Git branch name (default = "main")

    Returns:
        Cleaned and improved code or error message.
    """
    try:
        parsed = urlparse(github_url)
        parts = parsed.path.strip("/").split("/")
        if len(parts) < 2:
            return "❌ Invalid GitHub URL. Use format https://github.com/user/repo"

        user, repo = parts[0], parts[1]
        raw_url = f"https://raw.githubusercontent.com/{user}/{repo}/{branch}/{filepath}"

        print(f"🔗 Fetching: {raw_url}")  # Debug logging
        file_response = httpx.get(raw_url)
        if file_response.status_code != 200:
            return f"❌ File fetch failed: {file_response.status_code} - {raw_url}"

        code = file_response.text
        prompt = f"""You are a senior Python developer. Clean and fix the following code. Return only the improved version:\n\n```python\n{code}\n```"""

        model_response = httpx.post(HF_API_URL, headers=HEADERS, json={"inputs": prompt})
        if model_response.status_code != 200:
            return f"❌ Hugging Face error: {model_response.status_code} - {model_response.text}"

        return model_response.json()[0]["generated_text"]

    except Exception as e:
        return f"❌ Exception: {str(e)}"

if __name__ == "__main__":
    mcp.run()
