import json
import os
import pathlib
import requests
import feedparser

RSS_URL = os.environ["RSS_URL"]
KILO_WEBHOOK_URL = os.environ["KILO_WEBHOOK_URL"]

STATE_FILE = pathlib.Path(".podcast_state.json")

def load_state():
    if STATE_FILE.exists():
        return json.loads(STATE_FILE.read_text())
    return {"last_guid": None}

def save_state(state):
    STATE_FILE.write_text(json.dumps(state, indent=2))

def main():
    state = load_state()

    feed = feedparser.parse(RSS_URL)
    if not feed.entries:
        raise RuntimeError("No RSS entries found")

    latest = feed.entries[0]
    guid = latest.get("guid") or latest.get("id") or latest.get("link")

    if state.get("last_guid") == guid:
        print("No new episode. Exiting.")
        return

    title = latest.get("title", "Untitled")
    link = latest.get("link", "")
    published = latest.get("published", "")

    audio_url = None
    if "enclosures" in latest and latest.enclosures:
        audio_url = latest.enclosures[0].get("href")

    payload = {
        "taskType": "podcast_summary",
        "rssUrl": RSS_URL,
        "title": title,
        "published": published,
        "episodeUrl": link,
        "audioUrl": audio_url,
    }

    r = requests.post(
        KILO_WEBHOOK_URL,
        headers={"Content-Type": "application/json"},
        data=json.dumps(payload),
        timeout=30,
    )
    print("Kilo webhook status:", r.status_code)
    r.raise_for_status()

    state["last_guid"] = guid
    save_state(state)
    print("Triggered Kilo successfully.")

if __name__ == "__main__":
    main()
