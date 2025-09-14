# High-Scraping Tools Integration Guide

This document explains how to integrate high-scraping tools with Sovereign's Edict for collecting real social media data for policy analysis.

## Overview

Sovereign's Edict supports integration with high-scraping tools for collecting real data from:
- YouTube (yt-dlp or youtube-dl)
- LinkedIn (public profile scraping)
- Instagram (manual copy/public profile scraping)

## 1. YouTube Data Collection

### Using yt-dlp

yt-dlp is a youtube-dl fork with additional features and fixes.

#### Installation
```bash
pip install yt-dlp
```

#### Collecting Comments
```bash
# Collect comments in JSON format
yt-dlp --write-comments --comments-format json "YOUTUBE_VIDEO_URL"

# Collect metadata and comments
yt-dlp --write-info-json --write-comments --comments-format json "YOUTUBE_VIDEO_URL"
```

#### Processing for Sovereign's Edict
The scraped data can be directly used with our Scraped Data Ingestor plugin:
```bash
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=/path/to/video_comments.json"
```

### Using youtube-dl

youtube-dl is the original tool for downloading YouTube videos and metadata.

#### Installation
```bash
pip install youtube-dl
```

#### Collecting Comments
```bash
# Collect comments in JSON format
youtube-dl --write-comments --comments-format json "YOUTUBE_VIDEO_URL"
```

## 2. LinkedIn Data Collection

LinkedIn data collection requires public profile scraping since LinkedIn restricts API access.

### Manual Collection
1. Navigate to the LinkedIn post or profile
2. Copy the content manually
3. Save as structured data (JSON) or plain text

### Automated Scraping
For automated collection, you can use tools like:
- BeautifulSoup with Selenium for web scraping
- LinkedIn scraping services (ensure compliance with terms of service)

### Example JSON Structure
```json
{
  "posts": [
    {
      "id": "unique_post_id",
      "text": "Post content here",
      "author": "Author Name",
      "timestamp": "2023-08-20T09:00:00Z",
      "like_count": 25,
      "comment_count": 5
    }
  ]
}
```

## 3. Instagram Data Collection

Instagram data can be collected through manual copying or public profile scraping.

### Manual Collection
1. Navigate to the Instagram post or profile
2. Copy the content manually
3. Save as structured data (JSON) or plain text

### Automated Scraping
For automated collection, you can use tools like:
- Instagram scraping libraries
- Web scraping tools with proper headers

### Example Text Format
```
This is an Instagram post content. #hashtag1 #hashtag2

Another Instagram post with different content. #instagood #photooftheday
```

### Example JSON Structure
```json
{
  "posts": [
    {
      "id": "unique_post_id",
      "text": "Post content with #hashtags",
      "author": "username",
      "timestamp": "2023-08-20T09:00:00Z",
      "like_count": 100
    }
  ]
}
```

## 4. Using Scraped Data with Sovereign's Edict

### Data Ingestion
Once you have collected data using high-scraping tools, you can ingest it using our Scraped Data Ingestor plugin:

```bash
# For JSON data
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=/path/to/data.json"

# For text data
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=/path/to/data.txt"

# For CSV data
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=/path/to/data.csv"
```

### Data Format Requirements
The Scraped Data Ingestor plugin supports flexible data formats:

#### JSON
- Supports nested structures
- Automatically detects common keys (comments, items, data, entries)
- Maps fields to standard format

#### Text
- Items separated by double newlines
- Each item becomes a separate data point

#### CSV
- Automatic delimiter detection
- Header row used for field mapping

## 5. Integration Workflow

1. **Collect Data**: Use appropriate high-scraping tools for each platform
2. **Format Data**: Ensure data is in a supported format (JSON, TXT, CSV)
3. **Ingest Data**: Use the Scraped Data Ingestor plugin to load data
4. **Analyze Data**: Run analysis with Indian legal policy documents
5. **Review Results**: Examine arguments and suggestions generated

## 6. Best Practices

### Data Quality
- Ensure data is clean and relevant to the policy being analyzed
- Remove spam or irrelevant content before ingestion
- Validate data formats before processing

### Legal Compliance
- Respect platform terms of service
- Only collect publicly available data
- Anonymize personal data when required

### Performance
- Process large datasets in batches
- Monitor API rate limits
- Use appropriate error handling

## 7. Example Usage

### Collecting YouTube Comments
```bash
# Collect comments using yt-dlp
yt-dlp --write-comments --comments-format json "https://www.youtube.com/watch?v=example"

# Ingest into Sovereign's Edict
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=example.info.json"
```

### Collecting LinkedIn Posts
```bash
# After scraping LinkedIn data to linkedin_data.json
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=linkedin_data.json"
```

### Collecting Instagram Posts
```bash
# After collecting Instagram data to instagram_data.txt
curl -X POST "http://localhost:8001/ingest/plugin/scraped_data_ingestor?source=instagram_data.txt"
```

## 8. Troubleshooting

### Common Issues
1. **File not found**: Ensure the file path is correct and accessible
2. **Format errors**: Validate JSON files with a JSON validator
3. **Encoding issues**: Ensure files are saved with UTF-8 encoding

### Support
For issues with the Scraped Data Ingestor plugin, check the logs for detailed error messages.