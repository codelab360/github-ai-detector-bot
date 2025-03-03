import os
import google.generativeai as genai
from github import Github

# Retrieve API keys and issue details from GitHub Actions environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER")
ISSUE_BODY = os.getenv("ISSUE_BODY", "")

# Authenticate Google Gemini API
genai.configure(api_key=GEMINI_API_KEY)

# Skip empty issues
if not ISSUE_BODY.strip():
    exit(0)

# Analyze AI probability with Gemini
model = genai.GenerativeModel("gemini-pro")
response = model.generate_content(
    f"Analyze the following text and estimate the probability (0-100%) that it is AI-generated. "
    f"Return only the percentage (e.g., 65) without extra text.\n\n{ISSUE_BODY}"
)

# Extract AI probability
try:
    ai_probability = float(response.text.strip()) / 100
except ValueError:
    ai_probability = 0  # Default to 0 if parsing fails

# If AI probability is ≥ 60%, close the issue
if ai_probability >= 0.6:
    github_client = Github(GITHUB_TOKEN)
    repo = github_client.get_repo(REPO_NAME)
    issue = repo.get_issue(int(ISSUE_NUMBER))

    issue.create_comment("🚨 This issue appears to be AI-generated and does not meet our guidelines. Closing automatically.")
    issue.edit(state="closed")

print(f"AI Detection Probability: {ai_probability * 100:.2f}%")
