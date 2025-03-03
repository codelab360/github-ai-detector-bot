import os
import google.generativeai as genai
from github import Github
import re

# Retrieve API keys and issue details from GitHub Actions environment
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GIT_TOKEN = os.getenv("GIT_TOKEN")
REPO_NAME = os.getenv("GITHUB_REPOSITORY")
ISSUE_NUMBER = os.getenv("ISSUE_NUMBER")
ISSUE_BODY = os.getenv("ISSUE_BODY", "")

# Debugging Environment Variables
print(f"🔍 Debugging Variables:")
print(f"  - GEMINI_API_KEY: {'✅ Set' if GEMINI_API_KEY else '❌ Missing'}")
print(f"  - GIT_TOKEN: {'✅ Set' if GIT_TOKEN else '❌ Missing'}")
print(f"  - REPO_NAME: {REPO_NAME}")
print(f"  - ISSUE_NUMBER: {ISSUE_NUMBER}")
print(f"  - ISSUE_BODY: {ISSUE_BODY[:50]}...")  # Show only the first 50 characters

# Authenticate Google Gemini API
if not GEMINI_API_KEY:
    print("❌ ERROR: Missing GEMINI_API_KEY!")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel("gemini-1.5-pro-latest")  # ✅ Fixed Model Name

# Skip empty issues
if not ISSUE_BODY.strip():
    print("⚠️ Issue body is empty. Skipping detection.")
    exit(0)

# Analyze AI probability
response = model.generate_content(
    f"Analyze the following text and estimate the probability (0-100%) that it is AI-generated. "
    f"Return only the percentage (e.g., 65) without extra text.\n\n{ISSUE_BODY}"
)

# Extract AI probability
try:
    match = re.search(r"(\d+)", response.text)
    ai_probability = int(match.group(1)) / 100 if match else 0
except ValueError:
    ai_probability = 0

print(f"AI Detection Probability: {ai_probability * 100:.2f}%")

# If AI probability is ≥ 60%, close the issue
if ai_probability >= 0.6:
    if not GIT_TOKEN:
        print("❌ ERROR: GitHub token is missing or incorrect!")
        exit(1)

    github_client = Github(GIT_TOKEN.strip())  # ✅ Ensure no accidental whitespace issues
    repo = github_client.get_repo(REPO_NAME)
    issue = repo.get_issue(int(ISSUE_NUMBER))

    issue.create_comment("🚨 This issue appears to be AI-generated and does not meet our guidelines. Closing automatically.")
    issue.edit(state="closed")

    print("✅ Issue closed successfully!")
