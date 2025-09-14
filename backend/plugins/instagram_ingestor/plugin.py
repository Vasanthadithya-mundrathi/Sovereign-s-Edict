"""
Instagram Ingestor Plugin for Sovereign's Edict
"""
import sys
import os

# Add the parent directory to the path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Use absolute imports
from modules.base import IngestorModule
from typing import List, Dict, Any
import requests
import logging

logger = logging.getLogger(__name__)

class InstagramIngestor(IngestorModule):
    """
    Ingestor for Instagram post comments
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.access_token = self.config.get('access_token', os.environ.get('INSTAGRAM_ACCESS_TOKEN', ''))
        self.base_url = "https://graph.instagram.com"
    
    def initialize(self) -> bool:
        """
        Initialize Instagram ingestor
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Check if access token is provided
            if not self.access_token:
                logger.warning("No access token provided for Instagram ingestor")
                logger.warning("Instagram ingestor requires a valid access token for real data integration")
                logger.warning("Falling back to demo mode - no real data will be fetched")
                return False
            
            # Test the token by making a simple API call
            test_url = f"{self.base_url}/me?fields=id,username&access_token={self.access_token}"
            response = requests.get(test_url)
            
            if response.status_code == 200:
                logger.info("Instagram ingestor initialized successfully with REAL DATA access")
                return True
            else:
                logger.error(f"Failed to initialize Instagram ingestor: {response.text}")
                return False
                
        except Exception as e:
            logger.error(f"Error initializing Instagram ingestor: {str(e)}")
            return False
    
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
        Check if this ingestor can handle Instagram sources
        Args:
            source_type: Type of data source
        Returns:
            bool: True if can handle, False otherwise
        """
        return source_type.lower() in ["instagram", "ig", "insta"]
    
    def ingest(self, source: str) -> List[Dict]:
        """
        Ingest comments from Instagram post
        Args:
            source: Instagram post URL or ID
        Returns:
            List of ingested data items
        """
        try:
            # Extract post ID from URL if needed
            post_id = self._extract_post_id(source)
            if not post_id:
                raise ValueError("Could not extract post ID from source")
            
            # Get comments for the post
            comments = self._get_post_comments(post_id)
            
            # Convert to standard format
            formatted_comments = self._format_comments(comments, source)
            
            logger.info(f"Successfully ingested {len(formatted_comments)} comments from Instagram post {post_id}")
            return formatted_comments
            
        except Exception as e:
            logger.error(f"Error ingesting Instagram comments: {str(e)}")
            return []
    
    def _extract_post_id(self, source: str) -> str:
        """
        Extract post ID from Instagram URL
        Args:
            source: Instagram post URL or ID
        Returns:
            Post ID
        """
        # If it's already an ID, return it
        if "/" not in source:
            return source
        
        # Extract from URL
        # Example: https://www.instagram.com/p/C1234567890/
        try:
            parts = source.strip("/").split("/")
            if len(parts) >= 1:
                return parts[-1]
        except:
            pass
        
        return None
    
    def _get_post_comments(self, post_id: str) -> List[Dict]:
        """
        Get comments for an Instagram post
        Args:
            post_id: Instagram post ID
        Returns:
            List of comments
        """
        comments = []
        url = f"{self.base_url}/{post_id}/comments"
        params = {
            "access_token": self.access_token,
            "fields": "id,text,timestamp,username,like_count,replies"
        }
        
        while url:
            response = requests.get(url, params=params)
            
            if response.status_code != 200:
                raise Exception(f"Instagram API error: {response.text}")
            
            data = response.json()
            comments.extend(data.get("data", []))
            
            # Handle pagination
            paging = data.get("paging", {})
            url = paging.get("next") if paging else None
            params = {}  # Params are included in the next URL
        
        return comments
    
    def _format_comments(self, comments: List[Dict], source: str) -> List[Dict]:
        """
        Format Instagram comments to standard format
        Args:
            comments: List of Instagram comments
            source: Original source URL
        Returns:
            List of formatted comments
        """
        formatted = []
        
        for comment in comments:
            formatted.append({
                "text": comment.get("text", ""),
                "source": source,
                "timestamp": comment.get("timestamp", ""),
                "author": comment.get("username", "unknown"),
                "likes": comment.get("like_count", 0),
                "metadata": {
                    "platform": "instagram",
                    "post_id": comment.get("id", ""),
                    "replies": comment.get("replies", {}).get("count", 0)
                }
            })
        
        return formatted

# Register the plugin
# We'll register this in the plugin manager instead
# from modules import module_registry
# module_registry.register_ingestor("instagram", InstagramIngestor())