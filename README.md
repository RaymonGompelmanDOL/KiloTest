# Podcast Summarization Agent

An automated system for receiving podcast episode information via webhook, generating markdown summaries, and creating GitHub Pull Requests.

## Overview

This project provides a complete workflow for:
1. Receiving podcast episode metadata via webhook or scheduled RSS checks
2. Optionally downloading and transcribing audio content
3. Generating structured markdown summaries
4. Creating GitHub branches and Pull Requests automatically

## Architecture

### Components

1. **RSS Fetcher** ([`scripts/podcast_to_kilo.py`](scripts/podcast_to_kilo.py))
   - Polls RSS feed on a schedule
   - Detects new episodes
   - Sends webhook to trigger summarization

2. **Summarization Agent** ([`scripts/summarize_podcast.py`](scripts/summarize_podcast.py))
   - Receives episode metadata via webhook
   - Downloads audio (if URL provided)
   - Attempts transcription (if tools available)
   - Generates structured markdown summary
   - Creates git branch and Pull Request

3. **GitHub Actions Workflows**
   - [`podcast-summary.yml`](.github/workflows/podcast-summary.yml) - Scheduled RSS polling
   - [`podcast-webhook.yml`](.github/workflows/podcast-webhook.yml) - Webhook handler

## Setup

### Prerequisites

- GitHub repository with Actions enabled
- Python 3.11+
- GitHub CLI (`gh`) for PR creation
- (Optional) OpenAI Whisper for audio transcription

### Configuration

1. **Set up GitHub Secrets**
   
   Add the following secret to your repository:
   - `KILO_WEBHOOK_URL` - The webhook URL to trigger summarization

2. **Configure RSS Feed**
   
   Edit [`.github/workflows/podcast-summary.yml`](.github/workflows/podcast-summary.yml):
   ```yaml
   env:
     RSS_URL: "https://your-podcast-feed.com/rss"
   ```

3. **Enable GitHub Actions**
   
   Ensure Actions have write permissions:
   - Go to Settings → Actions → General
   - Under "Workflow permissions", select "Read and write permissions"
   - Check "Allow GitHub Actions to create and approve pull requests"

### Installation

Install Python dependencies:

```bash
pip install feedparser requests
```

For transcription support (optional):

```bash
pip install openai-whisper
```

## Usage

### Webhook Payload Format

Send a POST request with JSON payload:

```json
{
  "title": "Episode Title",
  "published": "2026-02-13T10:00:00Z",
  "episodeUrl": "https://example.com/episode",
  "audioUrl": "https://example.com/audio.mp3"
}
```

### Manual Trigger

You can manually trigger the workflow via GitHub Actions UI:

1. Go to Actions → Podcast Summary (Webhook)
2. Click "Run workflow"
3. Fill in the episode details
4. Click "Run workflow"

### Scheduled Execution

The RSS fetcher runs daily at 08:00 UTC (configurable in [`podcast-summary.yml`](.github/workflows/podcast-summary.yml)).

## Summary Format

Summaries are created in [`summaries/`](summaries/) with the format:

```
summaries/YYYY-MM-DD-episode-title-slug.md
```

Each summary includes:

- **Title** - Episode title
- **Published** - Publication date
- **Source** - Link to episode
- **Short Summary** - 5 bullet points max
- **Detailed Summary** - 5-12 bullet points
- **Key Takeaways** - 5 bullet points
- **Action Items** - Practical next steps (if applicable)

See [`summaries/2026-02-13-example-podcast-episode.md`](summaries/2026-02-13-example-podcast-episode.md) for an example.

## Transcription

The agent attempts to transcribe audio if:
1. An `audioUrl` is provided in the payload
2. Transcription tools are available (e.g., Whisper CLI)

If transcription is not available, the summary will note:
> **Note:** Transcript not available; summary is limited.

### Adding Transcription Support

To enable transcription, install Whisper:

```bash
pip install openai-whisper
```

Or modify [`scripts/summarize_podcast.py`](scripts/summarize_podcast.py) to use your preferred transcription service.

## Git Workflow

For each podcast episode, the agent:

1. Creates a branch: `ai/podcast-YYYY-MM-DD-episode-slug`
2. Commits the summary file
3. Pushes to remote
4. Creates a Pull Request with:
   - Title: "Podcast Summary: [Episode Title]"
   - Description: Short summary + link to full summary

## Customization

### Modifying Summary Format

Edit the [`generate_summary()`](scripts/summarize_podcast.py) and [`create_markdown_summary()`](scripts/summarize_podcast.py) functions in [`scripts/summarize_podcast.py`](scripts/summarize_podcast.py).

### Adding AI/LLM Integration

To use AI for better summaries, modify the [`generate_summary()`](scripts/summarize_podcast.py) function to:
1. Send transcript to your LLM API (OpenAI, Anthropic, etc.)
2. Parse the response into summary sections
3. Return structured summary data

Example integration point:

```python
def generate_summary(title: str, published: str, episode_url: str, 
                     transcript: Optional[str] = None) -> Dict[str, Any]:
    if transcript:
        # Add your LLM API call here
        llm_response = call_llm_api(transcript)
        summary = parse_llm_response(llm_response)
        return summary
    # ... rest of function
```

### Changing File Naming

Modify the [`sanitize_filename()`](scripts/summarize_podcast.py) and [`format_date_for_filename()`](scripts/summarize_podcast.py) functions in [`scripts/summarize_podcast.py`](scripts/summarize_podcast.py).

## Troubleshooting

### Summaries Not Being Created

1. Check GitHub Actions logs for errors
2. Verify webhook payload format
3. Ensure `summaries/` directory exists

### Pull Requests Not Created

1. Verify GitHub Actions has write permissions
2. Check that `gh` CLI is authenticated
3. Review git configuration in workflow

### Transcription Failing

1. Check if Whisper is installed
2. Verify audio URL is accessible
3. Check audio file format compatibility

## File Structure

```
.
├── .github/
│   └── workflows/
│       ├── podcast-summary.yml      # Scheduled RSS polling
│       └── podcast-webhook.yml      # Webhook handler
├── scripts/
│   ├── podcast_to_kilo.py          # RSS fetcher
│   └── summarize_podcast.py        # Summarization agent
├── summaries/                       # Generated summaries
│   └── YYYY-MM-DD-title.md
├── index.html                       # Project homepage
└── README.md                        # This file
```

## Contributing

To contribute:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a Pull Request

## License

This project is provided as-is for podcast summarization automation.

## Support

For issues or questions:
1. Check the GitHub Actions logs
2. Review the troubleshooting section
3. Open an issue in the repository
