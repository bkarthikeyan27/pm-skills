#!/usr/bin/env python3
"""
Collects all content that needs validation
"""

import os
import json
import subprocess

def run_command(cmd):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd,
            shell=True,
            capture_output=True,
            text=True
        )
        return result.stdout.strip()
    except Exception as e:
        print(f"Error running command: {e}")
        return ""

def collect_content():
    """Collect all content for validation"""
    
    content = {
        "code_changes": "",
        "commit_messages": "",
        "pr_title": "",
        "pr_body": "",
        "pr_comments": [],
        "review_comments": []
    }
    
    # Get code changes
    content["code_changes"] = run_command("git diff origin/main...HEAD")
    
    # Get commit messages
    content["commit_messages"] = run_command("git log --format=%B origin/main..HEAD")
    
    # Get PR info from environment
    content["pr_title"] = os.environ.get('PR_TITLE', '')
    content["pr_body"] = os.environ.get('PR_BODY', '')
    
    # Get comment if this is a comment event
    comment_body = os.environ.get('COMMENT_BODY', '')
    if comment_body:
        content["pr_comments"].append({
            "body": comment_body,
            "user": os.environ.get('COMMENT_USER', '')
        })
    
    return content

def main():
    """Main function"""
    content = collect_content()
    
    # Save to file
    with open('content_to_validate.json', 'w') as f:
        json.dump(content, f, indent=2)
    
    print("✅ Content collected successfully")
    print(f"   Code changes: {len(content['code_changes'])} chars")
    print(f"   Commits: {len(content['commit_messages'].split('\\n'))} messages")
    print(f"   PR title: {content['pr_title']}")

if __name__ == '__main__':
    main()
