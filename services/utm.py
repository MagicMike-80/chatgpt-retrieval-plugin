from typing import Optional
from urllib.parse import urlparse, parse_qs


def extract_utm_params(url: Optional[str]) -> dict:
    """Parse UTM tracking parameters from a URL string.

    Returns a dict with only the UTM keys that were present in the URL.
    Non-UTM query parameters (e.g. fbclid) are ignored.
    """
    if not url:
        return {}

    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query, keep_blank_values=False)
    except Exception:
        return {}

    utm_keys = ("utm_source", "utm_medium", "utm_campaign", "utm_content", "utm_term", "utm_id")
    result = {}
    for key in utm_keys:
        values = params.get(key)
        if values:
            result[key] = values[0]
    return result
