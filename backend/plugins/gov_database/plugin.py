"""
Government Database Plugin for Sovereign's Edict
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

class GovDatabaseIngestor(IngestorModule):
    """
    Ingestor for government consultation databases
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.api_key = self.config.get('api_key', os.environ.get('GOV_DATABASE_API_KEY', ''))
        self.base_url = self.config.get('base_url', 'https://api.gov/data')
    
    def initialize(self) -> bool:
        """
        Initialize government database ingestor
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # For now, we'll just log that initialization was attempted
            # In a real implementation, you might want to test connectivity
            logger.info("Government database ingestor initialized")
            return True
        except Exception as e:
            logger.error(f"Error initializing government database ingestor: {str(e)}")
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
        Check if this ingestor can handle government database sources
        Args:
            source_type: Type of data source
        Returns:
            bool: True if can handle, False otherwise
        """
        return source_type.lower() in ["gov_db", "government", "gov_database"]
    
    def ingest(self, source: str) -> List[Dict]:
        """
        Ingest data from government database
        Args:
            source: Database query or identifier
        Returns:
            List of ingested data items
        """
        try:
            # This implementation connects to an actual government database
            # or API and fetches the relevant data based on the source parameter
            
            # The source parameter should contain the query or identifier for the data
            # For example: "policy_consultation_id:12345" or "topic:privacy_law"
            
            # Parse the source parameter to determine what data to fetch
            if ":" in source:
                query_type, query_value = source.split(":", 1)
            else:
                # Default to searching by ID if no specific query type is provided
                query_type = "id"
                query_value = source
            
            # Construct the API request
            headers = {}
            if self.api_key:
                headers['Authorization'] = f'Bearer {self.api_key}'
            
            # Make the API request to fetch real data
            # Note: This is a placeholder URL - in a real implementation,
            # you would use the actual government database API endpoint
            url = f"{self.base_url}/{query_type}/{query_value}"
            
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # Parse the response
            data = response.json()
            
            # Transform the data into the format expected by the application
            ingested_data = []
            if isinstance(data, list):
                # If the response is a list of items
                for item in data:
                    ingested_item = {
                        "text": item.get("comment", item.get("text", "")),
                        "source": item.get("source", "Government Database"),
                        "timestamp": item.get("timestamp", item.get("date", "")),
                        "author": item.get("author", "Anonymous"),
                        "metadata": {
                            "platform": "government_database",
                            "category": item.get("category", "general"),
                            "region": item.get("region", "national")
                        }
                    }
                    ingested_data.append(ingested_item)
            elif isinstance(data, dict):
                # If the response is a single item or contains nested data
                if "comments" in data:
                    # If there's a comments field
                    for comment in data["comments"]:
                        ingested_item = {
                            "text": comment.get("text", ""),
                            "source": comment.get("source", "Government Database"),
                            "timestamp": comment.get("timestamp", comment.get("date", "")),
                            "author": comment.get("author", "Anonymous"),
                            "metadata": {
                                "platform": "government_database",
                                "category": comment.get("category", "general"),
                                "region": comment.get("region", "national")
                            }
                        }
                        ingested_data.append(ingested_item)
                else:
                    # Single item
                    ingested_item = {
                        "text": data.get("comment", data.get("text", "")),
                        "source": data.get("source", "Government Database"),
                        "timestamp": data.get("timestamp", data.get("date", "")),
                        "author": data.get("author", "Anonymous"),
                        "metadata": {
                            "platform": "government_database",
                            "category": data.get("category", "general"),
                            "region": data.get("region", "national")
                        }
                    }
                    ingested_data.append(ingested_item)
            
            logger.info(f"Successfully ingested {len(ingested_data)} records from government database")
            return ingested_data
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Network error while fetching government database data: {str(e)}")
            return []
        except Exception as e:
            logger.error(f"Error ingesting government database data: {str(e)}")
            return []

# Register the plugin
# We'll register this in the plugin manager instead
# from modules import module_registry
# module_registry.register_ingestor("gov_database", GovDatabaseIngestor())