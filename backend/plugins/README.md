# Plugin System

The plugin system in Sovereign's Edict allows for modular extensions to support various data sources. All plugins are designed to work with real data from actual sources rather than sample or mock data.

## Available Plugins

### 1. YouTube Ingestor (`youtube_ingestor`)
Ingests comments from YouTube videos using the official YouTube Data API.
- Requires a valid YouTube Data API key
- Works with real political debate videos and policy discussion content
- No mock or sample data used

### 2. Instagram Ingestor (`instagram_ingestor`)
Ingests comments from Instagram posts using the Instagram Graph API.
- Requires a valid Instagram access token
- Works with real social media content
- No mock or sample data used

### 3. LinkedIn Ingestor (`linkedin_ingestor`)
Ingests comments from LinkedIn posts using the LinkedIn API.
- Requires a valid LinkedIn access token
- Works with real professional discussion content
- No mock or sample data used

### 4. Government Database Ingestor (`gov_database`)
Accesses government consultation databases for real policy feedback.
- Connects to actual government data sources
- No mock or sample data used

### 5. Scraped Data Ingestor (`scraped_data_ingestor`)
Processes data collected from high-scraping tools like yt-dlp, youtube-dl, and manual scraping.
- Works with real data collected from various sources
- Supports multiple formats (JSON, TXT, CSV)
- No mock or sample data used

### 6. Indian Legal Policy Ingestor (`indian_legal_policy`)
Processes Indian legal policy documents for analysis.
- Works with real policy documents like the Digital Personal Data Protection Act, 2023
- No mock or sample data used

## Plugin Architecture

All plugins inherit from the `IngestorModule` base class and implement the required methods:
- `initialize()`: Initialize the plugin with required credentials
- `can_handle()`: Check if the plugin can handle a specific source type
- `ingest()`: Ingest data from the source
- `process()`: Process the ingested data

## Configuration

Each plugin can be configured through environment variables or configuration files. See `.env.example` for required configuration parameters.

## Adding New Plugins

To add a new plugin:
1. Create a new directory in the `plugins` folder
2. Implement a class that inherits from `IngestorModule`
3. Register the plugin in the plugin manager

All plugins must work with real data sources and should not include any mock or sample data functionality.
