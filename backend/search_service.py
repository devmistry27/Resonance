"""
Search Service
Handles web search via DuckDuckGo with retry logic and result processing.
"""
import logging
import time
from typing import List, Dict, Any, Optional
from ddgs import DDGS

import config

logger = logging.getLogger(__name__)


class SearchService:
    """Web search service using DuckDuckGo."""
    
    def __init__(self):
        self._ddgs: Optional[DDGS] = None
        self._available = True
        
    @property
    def ddgs(self) -> DDGS:
        """Lazy initialization of DDGS client."""
        if self._ddgs is None:
            try:
                self._ddgs = DDGS()
            except Exception as e:
                logger.error(f"Failed to initialize DDGS: {e}")
                self._available = False
                raise
        return self._ddgs
    
    @property
    def is_available(self) -> bool:
        """Check if search service is available."""
        return self._available and config.SEARCH_ENABLED

    def search(
        self, 
        query: str, 
        max_results: int = None
    ) -> List[Dict[str, Any]]:
        """
        Search the web using DuckDuckGo with retry logic.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of dictionaries containing 'title', 'href', and 'body'
        """
        if not self.is_available:
            logger.warning("Search service is disabled or unavailable")
            return []
            
        max_results = max_results or config.SEARCH_MAX_RESULTS
        
        # Clean up the query
        clean_query = self._clean_query(query)
        logger.info(f"Searching web for: {clean_query}")
        
        # Try with retries
        for attempt in range(config.SEARCH_RETRY_ATTEMPTS):
            try:
                # Try default backend first
                results = list(self.ddgs.text(
                    clean_query, 
                    max_results=max_results
                ))
                
                if results:
                    logger.info(f"Found {len(results)} results")
                    return self._validate_results(results)
                
                # If empty, try 'lite' backend
                if attempt == 0:
                    logger.warning("Default search empty, trying 'lite' backend")
                    results = list(self.ddgs.text(
                        clean_query, 
                        max_results=max_results, 
                        backend="lite"
                    ))
                    
                    if results:
                        return self._validate_results(results)
                        
            except Exception as e:
                logger.error(f"Search attempt {attempt + 1} failed: {e}")
                if attempt < config.SEARCH_RETRY_ATTEMPTS - 1:
                    time.sleep(1)  # Brief pause before retry
                continue
                
        logger.warning(f"No results found for: {clean_query}")
        return []
    
    def _clean_query(self, query: str) -> str:
        """Clean and optimize search query."""
        # Remove common question prefixes that don't help search
        prefixes_to_remove = [
            "can you tell me",
            "please tell me",
            "i want to know",
            "what do you know about",
            "search for",
            "look up",
            "find out",
        ]
        
        clean = query.lower().strip()
        for prefix in prefixes_to_remove:
            if clean.startswith(prefix):
                clean = clean[len(prefix):].strip()
                break
                
        return clean if clean else query
    
    def _validate_results(
        self, 
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, Any]]:
        """Validate and clean search results."""
        validated = []
        for res in results:
            if res.get("title") and res.get("href") and res.get("body"):
                validated.append({
                    "title": str(res["title"]).strip(),
                    "href": str(res["href"]).strip(),
                    "body": str(res["body"]).strip()[:500]  # Limit snippet length
                })
        return validated

    def format_results_for_prompt(
        self, 
        results: List[Dict[str, Any]]
    ) -> str:
        """
        Format search results into a structured string for the LLM.
        Designed to be easy for the model to parse and extract facts from.
        """
        if not results:
            return "No search results available."
            
        formatted_parts = ["=== WEB SEARCH RESULTS ===\n"]
        
        for i, res in enumerate(results, 1):
            formatted_parts.append(f"[Source {i}]")
            formatted_parts.append(f"Title: {res.get('title', 'Unknown')}")
            formatted_parts.append(f"URL: {res.get('href', 'Unknown')}")
            formatted_parts.append(f"Content: {res.get('body', 'No content')}")
            formatted_parts.append("")  # Empty line between results
            
        formatted_parts.append("=== END SEARCH RESULTS ===")
        return "\n".join(formatted_parts)
    
    def extract_sources_for_response(
        self, 
        results: List[Dict[str, Any]]
    ) -> List[Dict[str, str]]:
        """Extract clean source information for API response."""
        return [
            {
                "title": res.get("title", "Unknown"),
                "url": res.get("href", "#"),
                "snippet": res.get("body", "")[:200]
            }
            for res in results
        ]


# Global instance
search_service = SearchService()
