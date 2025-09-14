"""
Indian Legal Policy Plugin for Sovereign's Edict
"""
import sys
import os

# Add the parent directory to the path to enable absolute imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__)))))

# Use absolute imports
from backend.modules.base import IngestorModule
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

class IndianLegalPolicyIngestor(IngestorModule):
    """
    Ingestor for Indian legal policy documents
    Works with real policy documents and integrates with scraped social media data
    """
    
    def __init__(self, config: Dict = None):
        super().__init__(config)
        self.policy_directory = self.config.get('policy_directory', '/Users/vasanthadithya/SIH 2025/Sovereign\'s Edict/data')
    
    def initialize(self) -> bool:
        """
        Initialize Indian legal policy ingestor
        Returns:
            bool: True if initialization successful, False otherwise
        """
        try:
            # Check if policy directory exists
            if not os.path.exists(self.policy_directory):
                logger.warning(f"Policy directory not found: {self.policy_directory}")
                # Create directory if it doesn't exist
                os.makedirs(self.policy_directory, exist_ok=True)
            
            logger.info("Indian legal policy ingestor initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Error initializing Indian legal policy ingestor: {str(e)}")
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
        Check if this ingestor can handle Indian legal policy sources
        Args:
            source_type: Type of data source
        Returns:
            bool: True if can handle, False otherwise
        """
        return source_type.lower() in ["indian_legal", "indian_policy", "legal_policy", "default"]
    
    def ingest(self, source: str) -> List[Dict]:
        """
        Ingest Indian legal policy document
        Args:
            source: Path to policy document or identifier
        Returns:
            List of policy sections as data items
        """
        try:
            # If source is a file path, read the file
            if os.path.exists(source):
                with open(source, 'r', encoding='utf-8') as f:
                    content = f.read()
            else:
                # If source is "default" or an identifier, use the real policy document
                real_policy_path = os.path.join(self.policy_directory, "indian_digital_privacy_act_2023.txt")
                if os.path.exists(real_policy_path):
                    with open(real_policy_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                else:
                    logger.error(f"Real policy document not found: {real_policy_path}")
                    return []
            
            # Parse policy content into sections
            sections = self._parse_policy_content(content)
            
            # Convert to standard format
            formatted_sections = self._format_policy_sections(sections, source)
            
            logger.info(f"Successfully ingested Indian legal policy with {len(formatted_sections)} sections")
            return formatted_sections
            
        except Exception as e:
            logger.error(f"Error ingesting Indian legal policy: {str(e)}")
            return []
    
    def _parse_policy_content(self, content: str) -> List[Dict]:
        """
        Parse policy content into sections
        Args:
            content: Policy document content
        Returns:
            List of policy sections
        """
        sections = []
        lines = content.split('\n')
        
        current_chapter = None
        current_section = None
        current_subsection = None
        current_content = []
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
                
            # Check for chapters (CHAPTER)
            if line.startswith('CHAPTER'):
                # Save previous section if exists
                if current_section and current_content:
                    sections.append({
                        'chapter': current_chapter,
                        'title': current_section,
                        'subtitle': current_subsection,
                        'content': '\n'.join(current_content),
                        'type': 'section'
                    })
                
                # Start new chapter
                current_chapter = line
                current_section = None
                current_subsection = None
                current_content = []
                
            # Check for sections with numbers (e.g., "1. Short title and commencement")
            elif line[0].isdigit() and '. ' in line[:10]:
                # Save previous section if exists
                if current_section and current_content:
                    sections.append({
                        'chapter': current_chapter,
                        'title': current_section,
                        'subtitle': current_subsection,
                        'content': '\n'.join(current_content),
                        'type': 'section'
                    })
                
                # Start new section
                current_section = line
                current_subsection = None
                current_content = []
                
            # Check for subsections with parentheses (e.g., "(a) ...")
            elif line.startswith('(') and ')' in line[:5]:
                current_content.append(line)
                
            # Regular content
            else:
                if line and not line.startswith('#'):
                    current_content.append(line)
        
        # Save last section
        if current_section and current_content:
            sections.append({
                'chapter': current_chapter,
                'title': current_section,
                'subtitle': current_subsection,
                'content': '\n'.join(current_content),
                'type': 'section'
            })
        
        return sections
    
    def _format_policy_sections(self, sections: List[Dict], source: str) -> List[Dict]:
        """
        Format policy sections to standard format
        Args:
            sections: List of policy sections
            source: Original source
        Returns:
            List of formatted sections
        """
        formatted = []
        
        for i, section in enumerate(sections):
            formatted.append({
                "text": f"{section.get('chapter', '')}\n{section.get('title', '')}\n{section.get('subtitle', '')}\n{section.get('content', '')}",
                "source": source,
                "timestamp": "2023-08-11T00:00:00Z",  # Date of Act passage
                "author": "Government of India",
                "metadata": {
                    "platform": "legal_policy",
                    "section_type": section.get('type', 'general'),
                    "chapter": section.get('chapter', ''),
                    "title": section.get('title', ''),
                    "subtitle": section.get('subtitle', '')
                }
            })
        
        return formatted

# Register the plugin
# We'll register this in the plugin manager instead