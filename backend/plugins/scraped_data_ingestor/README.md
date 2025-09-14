# Scraped Data Ingestor Plugin

This plugin enables Sovereign's Edict to ingest data collected from high-scraping tools, including:

1. **YouTube**: Using `yt-dlp` or `youtube-dl`
2. **LinkedIn**: Public profile scraping
3. **Instagram**: Manual copy/public profile scraping

## Features

- Supports multiple data formats (JSON, TXT, CSV)
- Automatically detects platform from data source
- Properly parses and formats scraped data for analysis
- Integrates seamlessly with the existing plugin system

## Supported Data Formats

### JSON
Supports structured data from scraping tools. The plugin automatically detects common data structures:
- `comments` array
- `items` array
- `data` array
- `entries` array

### TXT
Plain text files with content separated by double newlines.

### CSV
Comma-separated values files with automatic delimiter detection.

## Usage

To use this plugin, simply provide the path to your scraped data file:

```bash
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=/path/to/your/scraped/data.json"
```

## Data Structure

The plugin expects data to contain the following fields (when available):
- `text` or `content`: The main content/text
- `author` or `username`: The author/username
- `timestamp` or `date`: Publication date
- `likes` or `like_count`: Number of likes/upvotes
- `replies` or `reply_count`: Number of replies/comments

## Platform Detection

The plugin automatically detects the platform based on:
1. Source URL (if provided)
2. Content keywords

Supported platforms:
- YouTube
- LinkedIn
- Instagram
- Generic scraped data

## Integration with High-Scraping Tools

### YouTube (yt-dlp/youtube-dl)
```bash
# Example using yt-dlp to collect comments
yt-dlp --write-comments --comments-format json VIDEO_URL
```

### LinkedIn (Public Profile Scraping)
Collect data manually or using scraping tools, then format as JSON.

### Instagram (Manual Copy/Public Profile Scraping)
Collect data manually or using scraping tools, then format as TXT or JSON.