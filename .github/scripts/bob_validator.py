#!/usr/bin/env python3
"""
Bob Content Validator
Validates all content for offensive language, confidential info, and security issues
"""

import anthropic
import json
import sys
import os
import re

def load_content():
    """Load content from JSON file"""
    try:
        with open('content_to_validate.json', 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Error: content_to_validate.json not found")
        sys.exit(1)

def create_validation_prompt(content):
    """Create comprehensive validation prompt for Bob"""
    
    prompt = f"""
You are Bob, IBM's AI content validator. Analyze ALL the following content for:

1. OFFENSIVE LANGUAGE: profanity, slurs, discriminatory language
2. UNPROFESSIONAL CONTENT: sarcastic, dismissive, or inappropriate comments
3. IBM CONFIDENTIAL INFO: internal systems, employee info, proprietary data
4. SECURITY ISSUES: hardcoded credentials, exposed secrets
5. COMPLIANCE VIOLATIONS: GDPR, licensing, export control

Content to Validate:

## Code Changes:
{content.get('code_changes', '')[:3000]}
## Commit Messages:
{content.get('commit_messages', '')}

## PR Title:
{content.get('pr_title', '')}

## PR Description:
{content.get('pr_body', '')}

## Comments:
{json.dumps(content.get('pr_comments', []), indent=2)}

Respond ONLY with valid JSON:
{{
  "approved": true/false,
  "overall_severity": "none"|"low"|"medium"|"high"|"critical",
  "confidence": 0.0-1.0,
  "issues": [
    {{
      "category": "offensive_language"|"unprofessional"|"confidential"|"security"|"compliance",
      "severity": "low"|"medium"|"high"|"critical",
      "location": "code"|"commit"|"pr_title"|"pr_body"|"comment",
      "file_path": "optional",
      "line_number": "optional",
      "description": "clear description",
      "found_text": "problematic text",
      "suggestion": "how to fix",
      "auto_fixable": true/false
    }}
  ],
  "summary": "brief assessment",
  "recommendations": ["list of recommendations"]
}}

Context awareness: Technical terms like "kill process" are acceptable.
"""
    return prompt

def validate_with_bob(content):
    """Send content to Bob for validation"""
    
    api_key = os.environ.get('ANTHROPIC_API_KEY')
    if not api_key:
        print("❌ Error: ANTHROPIC_API_KEY not set")
        sys.exit(1)
    
    client = anthropic.Anthropic(api_key=api_key)
    prompt = create_validation_prompt(content)
    
    print("🤖 Bob is analyzing content...")
    
    try:
        response = client.messages.create(
            model="claude-3-opus-20240229",
            max_tokens=4096,
            temperature=0.3,
            messages=[{"role": "user", "content": prompt}]
        )
        
        result_text = response.content[0].text
        
        # Extract JSON from response
        json_match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if json_match:
            result_text = json_match.group(0)
        
        return json.loads(result_text)
        
    except Exception as e:
        print(f"❌ Error during validation: {e}")
        sys.exit(1)

def display_results(result):
    """Display validation results"""
    
    print("\n" + "="*70)
    print("🤖 BOB VALIDATION REPORT")
    print("="*70)
    
    if result['approved']:
        print("\n✅ APPROVED")
        print(f"\nSummary: {result['summary']}")
        
        if result.get('recommendations'):
            print("\n💡 Recommendations:")
            for rec in result['recommendations']:
                print(f"  • {rec}")
        
        return 0
    
    else:
        print("\n❌ REJECTED")
        print(f"\nOverall Severity: {result['overall_severity'].upper()}")
        print(f"Confidence: {result.get('confidence', 0):.0%}")
        print(f"\nSummary: {result['summary']}")
        
        print(f"\n🚨 Issues Found ({len(result['issues'])}):")
        print("-" * 70)
        
        for i, issue in enumerate(result['issues'], 1):
            print(f"\n{i}. [{issue['severity'].upper()}] {issue['category'].replace('_', ' ').title()}")
            print(f"   Location: {issue['location']}")
            if issue.get('file_path'):
                print(f"   File: {issue['file_path']}")
            if issue.get('line_number'):
                print(f"   Line: {issue['line_number']}")
            print(f"   Issue: {issue['description']}")
            if issue.get('found_text'):
                print(f"   Found: {issue['found_text']}")
            if issue.get('suggestion'):
                print(f"   Fix: {issue['suggestion']}")
        
        print("\n" + "="*70)
        print("Please fix these issues and try again.")
        print("="*70)
        
        return 1

def main():
    """Main validation function"""
    
    # Load content
    content = load_content()
    
    # Validate with Bob
    result = validate_with_bob(content)
    
    # Save report
    with open('bob_report.json', 'w') as f:
        json.dump(result, f, indent=2)
    
    # Display results
    exit_code = display_results(result)
    
    sys.exit(exit_code)

if __name__ == '__main__':
    main()
