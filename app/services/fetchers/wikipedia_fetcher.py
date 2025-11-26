# app/stage_1/fetchers/wikipedia_fetcher.py
import requests
import logging
from typing import Optional
# Setup module-level logger
logger = logging.getLogger(__name__)

# Setup module-level logger
WIKI_API_SUMMARY_URL = "https://{lang}.wikipedia.org/api/rest_v1/page/summary/{title}"
WIKI_API_SEARCH_URL = "https://{lang}.wikipedia.org/w/api.php"

# Wikipedia REST API endpoints
HEADERS = {
    "User-Agent": "AmitContentAgent/1.0 (contact@amit.org)"
}


def resolve_wikipedia_title(topic: str, lang: str = "he") -> Optional[str]:
    """    Resolve the most relevant Wikipedia article title for a given topic name.
    
    This function uses the Wikipedia search API to find the most relevant 
    article title based on the user's query. It's useful for handling spelling
    variations, redirects, or approximate matches.
    
    Args:
        topic (str): The topic or keyword to search.
        lang (str): Language code (e.g., "he", "en").
    
    Returns:
        Optional[str]: The resolved article title, or None if no match is found."""
    params = {
        "action": "query",
        "list": "search",
        "srsearch": topic,
        "format": "json"
    }
    try:
        res = requests.get(WIKI_API_SEARCH_URL.format(lang=lang), headers=HEADERS, params=params, timeout=5)
        res.raise_for_status()
        results = res.json().get("query", {}).get("search", [])
        if results:
            return results[0]["title"]
    except Exception as e:
        logger.warning(f"[Wikipedia] Error resolving title for '{topic}': {e}")
    return None


def fetch_wikipedia_summary(topic: str, lang: str = "he") -> Optional[str]:
    """    Fetch a short summary paragraph for a given topic from Wikipedia.
    
    The summary is retrieved from Wikipedia's REST API, and provides a high-level
    overview suitable as an initial "source chunk" in the content_corpus.
    
    Args:
        topic (str): The topic or concept to fetch information about.
        lang (str): Wikipedia language code (default is "he" for Hebrew).
    
    Returns:
        Optional[str]: A short summary of the topic, or None if retrieval fails."""
    title = resolve_wikipedia_title(topic, lang)
    if not title:
        return None

    try:
        url = WIKI_API_SUMMARY_URL.format(lang=lang, title=title.replace(" ", "_"))
        res = requests.get(url, headers=HEADERS, timeout=5)
        res.raise_for_status()
        data = res.json()
        return data.get("extract")
    except Exception as e:
        logger.warning(f"[Wikipedia] Error fetching summary for '{title}': {e}")
        return None
