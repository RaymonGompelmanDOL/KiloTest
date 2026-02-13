#!/usr/bin/env python3
"""
Podcast Summarization Agent

Receives a JSON payload with podcast episode details and creates a markdown summary.
Optionally transcribes audio if available.
"""

import json
import os
import re
import sys
import pathlib
import subprocess
from datetime import datetime
from typing import Optional, Dict, Any


def sanitize_filename(text: str, max_length: int = 50) -> str:
    """
    Convert text to a safe filename slug.
    
    Args:
        text: The text to sanitize
        max_length: Maximum length of the resulting slug
        
    Returns:
        A safe filename slug
    """
    # Convert to lowercase
    slug = text.lower()
    
    # Replace spaces and special chars with hyphens
    slug = re.sub(r'[^\w\s-]', '', slug)
    slug = re.sub(r'[-\s]+', '-', slug)
    
    # Remove leading/trailing hyphens
    slug = slug.strip('-')
    
    # Truncate to max length
    if len(slug) > max_length:
        slug = slug[:max_length].rstrip('-')
    
    return slug


def format_date_for_filename(date_str: str) -> str:
    """
    Convert a date string to YYYY-MM-DD format for filenames.
    
    Args:
        date_str: Date string in various formats
        
    Returns:
        Date in YYYY-MM-DD format, or current date if parsing fails
    """
    if not date_str:
        return datetime.utcnow().strftime('%Y-%m-%d')
    
    # Try common date formats
    formats = [
        '%Y-%m-%d',
        '%Y-%m-%dT%H:%M:%S%z',
        '%Y-%m-%dT%H:%M:%SZ',
        '%a, %d %b %Y %H:%M:%S %z',
        '%a, %d %b %Y %H:%M:%S %Z',
    ]
    
    for fmt in formats:
        try:
            dt = datetime.strptime(date_str, fmt)
            return dt.strftime('%Y-%m-%d')
        except ValueError:
            continue
    
    # If all parsing fails, use current date
    return datetime.utcnow().strftime('%Y-%m-%d')


def download_audio(audio_url: str, output_path: pathlib.Path) -> bool:
    """
    Download audio file from URL.
    
    Args:
        audio_url: URL of the audio file
        output_path: Path to save the audio file
        
    Returns:
        True if successful, False otherwise
    """
    try:
        import requests
        response = requests.get(audio_url, stream=True, timeout=60)
        response.raise_for_status()
        
        with open(output_path, 'wb') as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        
        return True
    except Exception as e:
        print(f"Error downloading audio: {e}", file=sys.stderr)
        return False


def transcribe_audio(audio_path: pathlib.Path) -> Optional[str]:
    """
    Transcribe audio file using available tools.
    
    This is a placeholder that checks for common transcription tools.
    In practice, you might use:
    - OpenAI Whisper API
    - Local Whisper model
    - Other transcription services
    
    Args:
        audio_path: Path to the audio file
        
    Returns:
        Transcript text if successful, None otherwise
    """
    # Check if whisper CLI is available
    try:
        result = subprocess.run(
            ['which', 'whisper'],
            capture_output=True,
            text=True,
            timeout=5
        )
        
        if result.returncode == 0:
            # Whisper is available, use it
            print("Transcribing with Whisper...", file=sys.stderr)
            result = subprocess.run(
                ['whisper', str(audio_path), '--model', 'base', '--output_format', 'txt'],
                capture_output=True,
                text=True,
                timeout=600  # 10 minutes max
            )
            
            if result.returncode == 0:
                # Read the generated transcript
                txt_path = audio_path.with_suffix('.txt')
                if txt_path.exists():
                    return txt_path.read_text()
        
    except Exception as e:
        print(f"Transcription error: {e}", file=sys.stderr)
    
    return None


def generate_summary(title: str, published: str, episode_url: str, 
                     transcript: Optional[str] = None) -> Dict[str, Any]:
    """
    Generate a summary structure from podcast metadata and optional transcript.
    
    Args:
        title: Episode title
        published: Publication date
        episode_url: URL to the episode
        transcript: Optional transcript text
        
    Returns:
        Dictionary with summary sections
    """
    summary = {
        'title': title,
        'published': published,
        'episode_url': episode_url,
        'has_transcript': transcript is not None,
    }
    
    if transcript:
        # In a real implementation, you would use AI/LLM to analyze the transcript
        # For now, we'll create a template that can be filled in
        summary['short_summary'] = [
            "Episode discusses key topics (to be analyzed from transcript)",
            "Main themes and discussions covered",
            "Notable insights shared by speakers",
            "Practical applications and examples",
            "Conclusions and final thoughts"
        ]
        
        summary['detailed_summary'] = [
            "Introduction and context setting",
            "First major topic: [to be extracted from transcript]",
            "Second major topic: [to be extracted from transcript]",
            "Third major topic: [to be extracted from transcript]",
            "Discussion of implications and applications",
            "Q&A or audience interaction (if applicable)",
            "Key examples and case studies mentioned",
            "Expert opinions and perspectives shared",
            "Technical details and specifications (if applicable)",
            "Future outlook and predictions",
            "Closing remarks and next steps"
        ]
        
        summary['key_takeaways'] = [
            "Key insight #1 from the episode",
            "Key insight #2 from the episode",
            "Key insight #3 from the episode",
            "Key insight #4 from the episode",
            "Key insight #5 from the episode"
        ]
        
        summary['action_items'] = [
            "Suggested action based on episode content",
            "Resources to explore further",
            "Practices to implement"
        ]
    else:
        # Limited summary without transcript
        summary['short_summary'] = [
            f"Episode titled: {title}",
            "Transcript not available; summary is limited.",
            "Please listen to the full episode for complete details.",
            f"Published: {published}",
            f"Available at: {episode_url}"
        ]
        
        summary['detailed_summary'] = [
            "Detailed summary requires transcript analysis.",
            "Transcript was not available at the time of processing.",
            "Please refer to the episode URL for full content."
        ]
        
        summary['key_takeaways'] = [
            "Full transcript needed for detailed takeaways.",
            "Please listen to the episode directly.",
            f"Episode URL: {episode_url}"
        ]
        
        summary['action_items'] = []
    
    return summary


def create_markdown_summary(summary: Dict[str, Any]) -> str:
    """
    Create markdown content from summary dictionary.
    
    Args:
        summary: Dictionary containing summary sections
        
    Returns:
        Markdown formatted string
    """
    md_lines = [
        f"# {summary['title']}",
        "",
        f"**Published:** {summary['published']}",
        "",
        f"**Source:** [{summary['episode_url']}]({summary['episode_url']})",
        "",
    ]
    
    if not summary['has_transcript']:
        md_lines.extend([
            "> **Note:** Transcript not available; summary is limited.",
            "",
        ])
    
    # Short Summary
    md_lines.extend([
        "## Short Summary",
        "",
    ])
    for bullet in summary['short_summary']:
        md_lines.append(f"- {bullet}")
    md_lines.append("")
    
    # Detailed Summary
    md_lines.extend([
        "## Detailed Summary",
        "",
    ])
    for bullet in summary['detailed_summary']:
        md_lines.append(f"- {bullet}")
    md_lines.append("")
    
    # Key Takeaways
    md_lines.extend([
        "## Key Takeaways",
        "",
    ])
    for bullet in summary['key_takeaways']:
        md_lines.append(f"- {bullet}")
    md_lines.append("")
    
    # Action Items
    if summary['action_items']:
        md_lines.extend([
            "## Action Items",
            "",
        ])
        for bullet in summary['action_items']:
            md_lines.append(f"- {bullet}")
        md_lines.append("")
    
    return "\n".join(md_lines)


def create_git_branch(branch_name: str) -> bool:
    """
    Create and checkout a new git branch.
    
    Args:
        branch_name: Name of the branch to create
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Configure git if needed
        subprocess.run(['git', 'config', 'user.name', 'Podcast Summary Bot'], check=False)
        subprocess.run(['git', 'config', 'user.email', 'bot@podcast-summary.local'], check=False)
        
        # Create and checkout branch
        result = subprocess.run(
            ['git', 'checkout', '-b', branch_name],
            capture_output=True,
            text=True
        )
        
        return result.returncode == 0
    except Exception as e:
        print(f"Error creating branch: {e}", file=sys.stderr)
        return False


def commit_and_push(branch_name: str, file_path: pathlib.Path, commit_message: str) -> bool:
    """
    Commit changes and push to remote.
    
    Args:
        branch_name: Name of the branch
        file_path: Path to the file to commit
        commit_message: Commit message
        
    Returns:
        True if successful, False otherwise
    """
    try:
        # Add file
        subprocess.run(['git', 'add', str(file_path)], check=True)
        
        # Commit
        subprocess.run(['git', 'commit', '-m', commit_message], check=True)
        
        # Push
        subprocess.run(['git', 'push', '-u', 'origin', branch_name], check=True)
        
        return True
    except Exception as e:
        print(f"Error committing/pushing: {e}", file=sys.stderr)
        return False


def create_pull_request(branch_name: str, title: str, body: str) -> bool:
    """
    Create a GitHub Pull Request using gh CLI.
    
    Args:
        branch_name: Name of the branch
        title: PR title
        body: PR description
        
    Returns:
        True if successful, False otherwise
    """
    try:
        result = subprocess.run(
            ['gh', 'pr', 'create', '--base', 'main', '--head', branch_name, 
             '--title', title, '--body', body],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"Pull request created: {result.stdout.strip()}", file=sys.stderr)
            return True
        else:
            print(f"Error creating PR: {result.stderr}", file=sys.stderr)
            return False
            
    except Exception as e:
        print(f"Error creating pull request: {e}", file=sys.stderr)
        return False


def main():
    """Main entry point for the podcast summarization agent."""
    
    # Read JSON payload from stdin or environment variable
    payload_json = os.environ.get('PODCAST_PAYLOAD')
    
    if not payload_json:
        # Try reading from stdin
        payload_json = sys.stdin.read()
    
    if not payload_json:
        print("Error: No payload provided", file=sys.stderr)
        sys.exit(1)
    
    try:
        payload = json.loads(payload_json)
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON payload: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Extract required fields
    title = payload.get('title', 'Untitled Episode')
    published = payload.get('published', '')
    episode_url = payload.get('episodeUrl', '')
    audio_url = payload.get('audioUrl')
    
    print(f"Processing podcast: {title}", file=sys.stderr)
    
    # Generate safe filename components
    safe_date = format_date_for_filename(published)
    safe_title = sanitize_filename(title)
    
    # Create summary filename
    filename = f"{safe_date}-{safe_title}.md"
    summaries_dir = pathlib.Path('summaries')
    summaries_dir.mkdir(exist_ok=True)
    
    summary_path = summaries_dir / filename
    
    # Check if summary already exists
    if summary_path.exists():
        print(f"Summary already exists: {summary_path}", file=sys.stderr)
        print("Updating existing summary...", file=sys.stderr)
    
    # Attempt transcription if audio URL is provided
    transcript = None
    if audio_url:
        print(f"Audio URL provided: {audio_url}", file=sys.stderr)
        
        # Download audio
        temp_audio = pathlib.Path(f'/tmp/podcast_audio_{safe_date}_{safe_title}.mp3')
        if download_audio(audio_url, temp_audio):
            print("Audio downloaded successfully", file=sys.stderr)
            
            # Attempt transcription
            transcript = transcribe_audio(temp_audio)
            
            # Clean up temp file
            try:
                temp_audio.unlink()
            except:
                pass
        else:
            print("Failed to download audio", file=sys.stderr)
    
    # Generate summary
    summary = generate_summary(title, published, episode_url, transcript)
    
    # Create markdown content
    markdown_content = create_markdown_summary(summary)
    
    # Write summary file
    summary_path.write_text(markdown_content)
    print(f"Summary written to: {summary_path}", file=sys.stderr)
    
    # Create git branch
    branch_name = f"ai/podcast-{safe_date}-{safe_title}"
    if create_git_branch(branch_name):
        print(f"Created branch: {branch_name}", file=sys.stderr)
        
        # Commit and push
        commit_message = f"Add podcast summary: {title}"
        if commit_and_push(branch_name, summary_path, commit_message):
            print("Changes committed and pushed", file=sys.stderr)
            
            # Create PR
            pr_title = f"Podcast Summary: {title}"
            pr_body = f"""## Podcast Summary

**Episode:** {title}
**Published:** {published}
**Source:** {episode_url}

### Short Summary

"""
            for bullet in summary['short_summary']:
                pr_body += f"- {bullet}\n"
            
            pr_body += f"\n**Full summary:** [View file](summaries/{filename})"
            
            if create_pull_request(branch_name, pr_title, pr_body):
                print("Pull request created successfully", file=sys.stderr)
            else:
                print("Failed to create pull request", file=sys.stderr)
        else:
            print("Failed to commit/push changes", file=sys.stderr)
    else:
        print("Failed to create git branch", file=sys.stderr)
    
    print("Processing complete", file=sys.stderr)


if __name__ == '__main__':
    main()
