"""
LinkedIn Ingestor Plugin for Sovereign's Edict
"""
import sys
import os
import re
import logging
from typing import List, Dict, Any
import requests

# Add the parent directory to the path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Use absolute imports
from backend.modules.base import IngestorModule

logger = logging.getLogger(__name__)

class LinkedInIngestor(IngestorModule):
    """
    Ingestor for LinkedIn posts and articles with real API integration
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        # For real implementation, you would use the LinkedIn API
        self.access_token = self.config.get('access_token', os.environ.get('LINKEDIN_ACCESS_TOKEN', ''))
        self.max_comments = self.config.get('max_comments', 50)
    
    def initialize(self) -> bool:
        """
        Initialize LinkedIn ingestor
        Returns:
            bool: True if initialization successful, False otherwise
        """
        # Check if access token is provided
        if not self.access_token:
            logger.error("LinkedIn access token is required for real data integration")
            return False
        
        # Test the token by making a simple API call
        try:
            url = "https://api.linkedin.com/v2/me"
            headers = {
                'Authorization': f'Bearer {self.access_token}'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                logger.info("LinkedIn ingestor initialized successfully with REAL DATA access")
                return True
            else:
                logger.error(f"Failed to validate LinkedIn access token: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"Error validating LinkedIn access token: {str(e)}")
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
        Check if this ingestor can handle LinkedIn sources
        Args:
            source_type: Type of data source
        Returns:
            bool: True if can handle, False otherwise
        """
        return source_type.lower() in ["linkedin", "linked_in", "professional_network", "default"]
    
    def ingest(self, source: str) -> List[Dict]:
        """
        Ingest comments from LinkedIn post
        Args:
            source: LinkedIn post URL
        Returns:
            List of ingested data items
        """
        try:
            # Extract post ID from URL if needed
            post_id = self._extract_post_id(source)
            if not post_id:
                raise ValueError("Could not extract post ID from source")
            
            # Check if we have a valid access token
            if not self.access_token:
                raise ValueError("LinkedIn access token is required for real data integration")
            
            # Get comments for the post using real API
            comments = self._get_linkedin_comments(post_id)
            
            # Convert to standard format
            formatted_comments = self._format_comments(comments, source)
            
            logger.info(f"Successfully ingested {len(formatted_comments)} comments from LinkedIn post {post_id}")
            return formatted_comments
            
        except Exception as e:
            logger.error(f"Error ingesting LinkedIn comments: {str(e)}")
            return []
    
    def _extract_post_id(self, url: str) -> str:
        """
        Extract post ID from LinkedIn URL
        Args:
            url: LinkedIn post URL
        Returns:
            Post ID
        """
        # Regular expression for LinkedIn post URL
        pattern = r'(?:https?:\/\/)?(?:www\.)?linkedin\.com\/feed\/update\/urn:li:activity:(\d+)'
        
        match = re.search(pattern, url)
        if match:
            return match.group(1)
            
        return None
    
    def _get_linkedin_comments(self, post_id: str) -> List[Dict]:
        """
        Get comments from LinkedIn post using the LinkedIn API
        Args:
            post_id: LinkedIn post ID
        Returns:
            List of comments
        """
        comments = []
        
        # LinkedIn API endpoint for comments (simplified example)
        # Note: Actual implementation would require proper OAuth and API access
        url = f"https://api.linkedin.com/v2/comments"
        headers = {
            'Authorization': f'Bearer {self.access_token}',
            'X-Restli-Protocol-Version': '2.0.0'
        }
        params = {
            'q': 'comments',
            'parentComment': f'urn:li:activity:{post_id}'
        }
        
        try:
            response = requests.get(url, headers=headers, params=params)
            response.raise_for_status()
            
            data = response.json()
            
            # Extract comments from response
            for item in data.get('elements', []):
                comments.append({
                    "id": item.get('id', ''),
                    "text": item.get('message', {}).get('text', ''),
                    "author": item.get('actor', 'unknown'),
                    "timestamp": item.get('created', {}).get('time', ''),
                    "like_count": item.get('likesSummary', {}).get('aggregatedTotalLikes', 0),
                    "reply_count": len(item.get('comments', []))
                })
                
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching LinkedIn comments: {str(e)}")
        
        return comments
    
    def _format_comments(self, comments: List[Dict], source: str) -> List[Dict]:
        """
        Format LinkedIn comments to standard format
        Args:
            comments: List of LinkedIn comments
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
                "author": comment.get("author", "unknown"),
                "likes": comment.get("like_count", 0),
                "metadata": {
                    "platform": "linkedin",
                    "post_id": comment.get("id", ""),
                    "replies": comment.get("reply_count", 0),
                    "category": "professional_discussion"
                }
            })
        
        return formatted

# Register the plugin
# We'll register this in the plugin manager instead