"""
Scraped Data Ingestor Plugin for Sovereign's Edict
Handles data collected from high-scraping tools like yt-dlp, youtube-dl, and manual scraping
"""
import sys
import os
import json
import logging
from typing import List, Dict, Any
import re

# Add the parent directory to the path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Use absolute imports
from backend.modules.base import IngestorModule

logger = logging.getLogger(__name__)

class ScrapedDataIngestor(IngestorModule):
    """
    Ingestor for data collected from high-scraping tools
    Supports YouTube (yt-dlp/youtube-dl), LinkedIn (public scraping), and Instagram (manual copy/public scraping)
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.supported_formats = self.config.get('supported_formats', ['json', 'txt', 'csv'])
    
    def initialize(self) -> bool:
        """
        Initialize scraped data ingestor
        Returns:
            bool: True if initialization successful, False otherwise
        """
        logger.info("Scraped data ingestor initialized")
        return True
    
    def process(self, data: Any) -> Any:
        """
        Process data through the module
        Args:
            data: Input data to process
        Returns:
            Processed data
        """
        # For an ingestor, processing might mean ingesting if the data is a source
        if isinstance(data, str):
            return self.ingest(data)
        return data
    
    def can_handle(self, source_type: str) -> bool:
        """
        Check if this ingestor can handle scraped data sources
        Args:
            source_type: Type of data source
        Returns:
            bool: True if can handle, False otherwise
        """
        return source_type.lower() in ["scraped_data", "scraped", "yt-dlp", "youtube-dl", "manual_scrape"]
    
    def ingest(self, source: str) -> List[Dict]:
        """
        Ingest data from scraped sources
        Args:
            source: Path to scraped data file or identifier
        Returns:
            List of ingested data items
        """
        try:
            # If source is a file path, read the file
            if os.path.exists(source):
                file_extension = source.split('.')[-1].lower()
                if file_extension == 'json':
                    data = self._parse_json_data(source)
                elif file_extension == 'txt':
                    data = self._parse_text_data(source)
                elif file_extension == 'csv':
                    data = self._parse_csv_data(source)
                else:
                    raise ValueError(f"Unsupported file format: {file_extension}")
            else:
                # If source is an identifier, handle accordingly
                data = self._handle_identifier(source)
            
            # Convert to standard format
            formatted_data = self._format_scraped_data(data, source)
            
            logger.info(f"Successfully ingested {len(formatted_data)} items from scraped data source")
            return formatted_data
            
        except Exception as e:
            logger.error(f"Error ingesting scraped data: {str(e)}")
            return []
    
    def _parse_json_data(self, file_path: str) -> List[Dict]:
        """
        Parse JSON data from scraping tools
        Args:
            file_path: Path to JSON file
        Returns:
            List of data items
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        # Handle different JSON structures
        if isinstance(data, list):
            return data
        elif isinstance(data, dict):
            # If it's a dict, look for common keys that contain the data
            for key in ['comments', 'items', 'data', 'entries']:
                if key in data and isinstance(data[key], list):
                    return data[key]
            # If no known structure, return the dict as a single item
            return [data]
        else:
            return [{'text': str(data)}]
    
    def _parse_text_data(self, file_path: str) -> List[Dict]:
        """
        Parse text data from scraping tools
        Args:
            file_path: Path to text file
        Returns:
            List of data items
        """
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Split by double newlines or other common separators
        items = re.split(r'\n\s*\n|\r\n\s*\r\n', content.strip())
        
        # Convert to dict format
        result = []
        for i, item in enumerate(items):
            if item.strip():
                result.append({
                    'id': str(i),
                    'text': item.strip()
                })
        
        return result
    
    def _parse_csv_data(self, file_path: str) -> List[Dict]:
        """
        Parse CSV data from scraping tools
        Args:
            file_path: Path to CSV file
        Returns:
            List of data items
        """
        import csv
        
        result = []
        with open(file_path, 'r', encoding='utf-8') as f:
            # Try to detect delimiter
            sample = f.read(1024)
            f.seek(0)
            sniffer = csv.Sniffer()
            delimiter = sniffer.sniff(sample).delimiter
            
            reader = csv.DictReader(f, delimiter=delimiter)
            for i, row in enumerate(reader):
                # Convert row to our standard format
                item = {
                    'id': str(i),
                    'text': ' '.join(str(v) for v in row.values() if v)
                }
                
                # Add any other fields from the CSV
                for key, value in row.items():
                    if key.lower() not in ['text', 'content']:
                        item[key] = value
                
                result.append(item)
        
        return result
    
    def _handle_identifier(self, source: str) -> List[Dict]:
        """
        Handle identifier-based data sources
        Args:
            source: Identifier string
        Returns:
            List of data items
        """
        # This would handle cases where source is not a file path
        # For example, if we're integrating with a scraping service
        logger.warning(f"Identifier-based data source not implemented: {source}")
        return []
    
    def _format_scraped_data(self, data: List[Dict], source: str) -> List[Dict]:
        """
        Format scraped data to standard format
        Args:
            data: List of scraped data items
            source: Original source
        Returns:
            List of formatted data items
        """
        formatted = []
        
        for i, item in enumerate(data):
            # Extract common fields
            text = item.get('text') or item.get('content') or item.get('comment') or ''
            author = item.get('author') or item.get('username') or item.get('name') or 'unknown'
            timestamp = item.get('timestamp') or item.get('date') or item.get('publishedAt') or ''
            likes = item.get('likes') or item.get('like_count') or item.get('upvotes') or 0
            replies = item.get('replies') or item.get('reply_count') or item.get('comments') or 0
            
            # Determine platform from source or item
            platform = self._detect_platform(source, item)
            
            formatted.append({
                "text": str(text),
                "source": source,
                "timestamp": str(timestamp),
                "author": str(author),
                "likes": int(likes) if str(likes).isdigit() else 0,
                "metadata": {
                    "platform": platform,
                    "item_id": item.get('id', str(i)),
                    "replies": int(replies) if str(replies).isdigit() else 0,
                    "raw_data": item  # Keep original data for reference
                }
            })
        
        return formatted
    
    def _detect_platform(self, source: str, item: Dict) -> str:
        """
        Detect platform from source or item data
        Args:
            source: Source string
            item: Data item
        Returns:
            Platform name
        """
        # Check source URL
        if 'youtube.com' in source or 'youtu.be' in source:
            return 'youtube'
        elif 'linkedin.com' in source:
            return 'linkedin'
        elif 'instagram.com' in source:
            return 'instagram'
        
        # Check item data for platform indicators
        if 'youtube' in str(item).lower():
            return 'youtube'
        elif 'linkedin' in str(item).lower():
            return 'linkedin'
        elif 'instagram' in str(item).lower():
            return 'instagram'
        
        return 'scraped_data'

# Register the plugin
# We'll register this in the plugin manager instead