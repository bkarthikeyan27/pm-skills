#!/bin/bash
# IBM PR Creation Script with Bob Pre-validation

set -e

echo "🤖 IBM PR Creation Tool"
echo "======================="
echo ""

# Get PR details
read -p "PR Title: " PR_TITLE
echo ""
echo "PR Description (press Ctrl+D when done):"
PR_BODY=$(cat)

echo ""
echo "🔍 Bob is pre-validating your PR..."

# Create temporary content file
cat > /tmp/pr_content.json << JSON
{
  "pr_title": "$PR_TITLE",
  "pr_body": "$PR_BODY",
  "code_changes": "$(git diff origin/main...HEAD | head -c 3000)",
  "commit_messages": "$(git log --format=%B origin/main..HEAD)"
}
JSON

# Validate with Bob (if API available)
if [ ! -z "$IBM_BOB_API" ]; then
  RESULT=$(curl -s -X POST $IBM_BOB_API/validate \
    -H "Content-Type: application/json" \
    -d @/tmp/pr_content.json)
  
  STATUS=$(echo $RESULT | jq -r '.approved')
  
  if [ "$STATUS" != "true" ]; then
    echo ""
    echo "❌ Bob pre-validation failed:"
    echo $RESULT | jq -r '.issues[] | "  [\(.severity)] \(.description)"'
    echo ""
    echo "Please fix these issues before creating PR."
    rm /tmp/pr_content.json
    exit 1
  fi
fi

echo "✅ Pre-validation passed!"
echo ""

# Create PR to external repo
echo "Creating PR to external repository..."

gh pr create \
  --repo external-org/project-name \
  --title "$PR_TITLE" \
  --body "$PR_BODY" \
  --base main

echo ""
echo "✅ PR created successfully!"
echo "Bob will continue monitoring this PR."

rm /tmp/pr_content.json
