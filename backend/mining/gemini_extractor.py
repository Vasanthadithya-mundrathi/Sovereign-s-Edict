"""
Gemini API based argument extractor for Sovereign's Edict
"""
import google.generativeai as genai
from typing import List, Dict, Optional
import os
import json
import uuid
import logging
import sys
import os

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))

# Use absolute imports
from models.comment import Comment
from models.argument import Argument, ArgumentType

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GeminiArgumentExtractor:
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the Gemini extractor
        
        Args:
            api_key: Google Gemini API key. If not provided, will try to get from environment variable.
        """
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")
        if not self.api_key:
            raise ValueError("Gemini API key is required. Set GEMINI_API_KEY environment variable.")
        
        genai.configure(api_key=self.api_key)
        
        # Initialize the model
        self.model = genai.GenerativeModel('gemini-pro')
        
    def extract_arguments(self, comments: List[Comment]) -> List[Argument]:
        """
        Extract arguments from comments using Gemini API
        
        Args:
            comments: List of Comment objects
            
        Returns:
            List of Argument objects
        """
        arguments = []
        
        for comment in comments:
            try:
                argument = self._extract_single_argument(comment)
                if argument:
                    arguments.append(argument)
            except Exception as e:
                logger.error(f"Error extracting argument from comment {comment.id}: {str(e)}")
                # Create a fallback argument using the basic extractor
                fallback_argument = self._create_fallback_argument(comment)
                arguments.append(fallback_argument)
        
        return arguments
    
    def _extract_single_argument(self, comment: Comment) -> Optional[Argument]:
        """
        Extract a single argument from a comment using Gemini API
        """
        prompt = self._create_extraction_prompt(comment)
        
        # Generate response from Gemini
        response = self.model.generate_content(prompt)
        
        # Parse the response
        extracted_data = self._parse_gemini_response(response.text)
        
        # Create Argument object
        argument = Argument(
            id=str(uuid.uuid4()),
            comment_id=comment.id,
            text=comment.text,
            type=extracted_data.get("type", ArgumentType.NEUTRAL),
            themes=extracted_data.get("themes", ["general"]),
            clause=comment.policy_clause,
            confidence=extracted_data.get("confidence", 0.8),
            citations=extracted_data.get("citations", [])
        )
        
        return argument
    
    def _create_extraction_prompt(self, comment: Comment) -> str:
        """
        Create a prompt for Gemini to extract argument information
        """
        prompt = f"""
        Analyze the following public comment on a policy document and extract structured information about the argument presented.
        
        Comment: "{comment.text}"
        Policy Clause: {comment.policy_clause}
        
        Please analyze this comment and provide the following information in JSON format:
        1. The type of argument (support, objection, or neutral)
        2. Key themes or topics discussed (as an array of strings)
        3. Confidence level in your analysis (0.0 to 1.0)
        4. Any relevant citations that support or contradict this argument (as an array of strings)
        
        Respond ONLY with a valid JSON object in this exact format:
        {{
            "type": "support|objection|neutral",
            "themes": ["theme1", "theme2"],
            "confidence": 0.95,
            "citations": ["citation1", "citation2"]
        }}
        
        Do not include any other text in your response.
        """
        
        return prompt
    
    def _parse_gemini_response(self, response_text: str) -> Dict:
        """
        Parse the JSON response from Gemini
        """
        try:
            # Clean the response text in case there's extra formatting
            cleaned_response = response_text.strip()
            if cleaned_response.startswith("```json"):
                cleaned_response = cleaned_response[7:]
            if cleaned_response.endswith("```"):
                cleaned_response = cleaned_response[:-3]
            
            # Parse JSON
            data = json.loads(cleaned_response)
            
            # Validate and convert argument type
            arg_type_str = data.get("type", "neutral")
            if arg_type_str == "support":
                data["type"] = ArgumentType.SUPPORT
            elif arg_type_str == "objection":
                data["type"] = ArgumentType.OBJECTION
            else:
                data["type"] = ArgumentType.NEUTRAL
            
            # Ensure themes is a list
            if not isinstance(data.get("themes", []), list):
                data["themes"] = [str(data["themes"])]
            
            # Ensure citations is a list
            if not isinstance(data.get("citations", []), list):
                data["citations"] = [str(data["citations"])]
                
            return data
        except json.JSONDecodeError as e:
            logger.error(f"Error parsing Gemini response: {str(e)}")
            logger.error(f"Response text: {response_text}")
            # Return default values
            return {
                "type": ArgumentType.NEUTRAL,
                "themes": ["general"],
                "confidence": 0.5,
                "citations": []
            }
    
    def _create_fallback_argument(self, comment: Comment) -> Argument:
        """
        Create a fallback argument using basic keyword analysis
        """
        # Simple keyword-based argument detection
        support_keywords = ['support', 'agree', 'good', 'benefit', 'positive', 'favor']
        objection_keywords = ['against', 'disagree', 'bad', 'negative', 'concern', 'problem', 'issue']
        
        text_lower = comment.text.lower()
        
        support_count = sum(1 for keyword in support_keywords if keyword in text_lower)
        objection_count = sum(1 for keyword in objection_keywords if keyword in text_lower)
        
        if support_count > objection_count:
            arg_type = ArgumentType.SUPPORT
        elif objection_count > support_count:
            arg_type = ArgumentType.OBJECTION
        else:
            arg_type = ArgumentType.NEUTRAL
        
        # Simple theme extraction
        themes = []
        theme_keywords = {
            'privacy': ['privacy', 'personal data', 'surveillance', 'monitoring'],
            'economic': ['cost', 'expense', 'money', 'financial', 'economy'],
            'legal': ['law', 'legal', 'constitution', 'rights'],
            'technical': ['technology', 'technical', 'system', 'software'],
            'implementation': ['implement', 'process', 'procedure', 'execute']
        }
        
        for theme, keywords in theme_keywords.items():
            if any(keyword in text_lower for keyword in keywords):
                themes.append(theme)
        
        if not themes:
            themes = ['general']
        
        return Argument(
            id=str(uuid.uuid4()),
            comment_id=comment.id,
            text=comment.text,
            type=arg_type,
            themes=themes,
            clause=comment.policy_clause,
            confidence=0.5
        )