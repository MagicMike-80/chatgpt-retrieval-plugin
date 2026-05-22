import re
import time
import logging
from urllib.parse import urljoin, urlparse, urldefrag
from typing import Optional

import requests
from bs4 import BeautifulSoup

from .models import ScrapedAsset, ScrapedPage, ScrapedSite

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
}

ASSET_CONTENT_TYPES = {
    "text/css",
    "application/javascript",
    "text/javascript",
    "image/png",
    "image/jpeg",
    "image/gif",
    "image/svg+xml",
    "image/webp",
    "image/x-icon",
    "font/woff",
    "font/woff2",
    "font/ttf",
    "application/font-woff",
}


class WebScraper:
    def __init__(
        self,
        max_pages: int = 10,
        max_depth: int = 2,
        timeout: int = 15,
        delay: float = 0.5,
    ):
        self.max_pages = max_pages
        self.max_depth = max_depth
        self.timeout = timeout
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update(HEADERS)

    def scrape(self, url: str) -> ScrapedSite:
        parsed = urlparse(url)
        base_url = f"{parsed.scheme}://{parsed.netloc}"
        site = ScrapedSite(base_url=base_url)

        visited: set[str] = set()
        queue: list[tuple[str, int]] = [(url, 0)]

        while queue and len(site.pages) < self.max_pages:
            current_url, depth = queue.pop(0)
            clean_url, _ = urldefrag(current_url)

            if clean_url in visited:
                continue
            visited.add(clean_url)

            page = self._scrape_page(clean_url)
            if not page:
                continue

            site.pages.append(page)
            logger.info(f"Scraped: {clean_url} (depth={depth})")

            if depth < self.max_depth:
                for link in page.links:
                    if link not in visited and self._is_same_domain(link, base_url):
                        queue.append((link, depth + 1))

            time.sleep(self.delay)

        self._fetch_assets(site)
        return site

    def _scrape_page(self, url: str) -> Optional[ScrapedPage]:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
        except requests.RequestException as e:
            logger.warning(f"Failed to fetch {url}: {e}")
            return None

        if "text/html" not in resp.headers.get("Content-Type", ""):
            return None

        soup = BeautifulSoup(resp.text, "html.parser")
        base = urlparse(url)
        base_str = f"{base.scheme}://{base.netloc}"

        page = ScrapedPage(
            url=url,
            html=resp.text,
            title=self._extract_title(soup),
        )

        for tag in soup.find_all("link", rel="stylesheet"):
            href = tag.get("href", "")
            if href:
                page.css_links.append(self._abs(href, base_str, url))

        for tag in soup.find_all("script", src=True):
            src = tag.get("src", "")
            if src:
                page.js_links.append(self._abs(src, base_str, url))

        for tag in soup.find_all("img"):
            src = tag.get("src") or tag.get("data-src", "")
            if src:
                page.image_links.append(self._abs(src, base_str, url))

        for tag in soup.find_all("link", rel=lambda r: r and any("font" in v for v in r)):
            href = tag.get("href", "")
            if href:
                page.font_links.append(self._abs(href, base_str, url))

        for tag in soup.find_all("style"):
            if tag.string:
                page.inline_styles.append(tag.string)

        for tag in soup.find_all("script", src=False):
            if tag.string and len(tag.string.strip()) > 10:
                page.inline_scripts.append(tag.string)

        for meta in soup.find_all("meta"):
            name = meta.get("name") or meta.get("property", "")
            content = meta.get("content", "")
            if name and content:
                page.meta_tags[name] = content

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if href.startswith(("mailto:", "tel:", "javascript:", "#")):
                continue
            abs_href = self._abs(href, base_str, url)
            if abs_href:
                page.links.append(abs_href)

        return page

    def _fetch_assets(self, site: ScrapedSite) -> None:
        all_css_urls: set[str] = set()
        all_js_urls: set[str] = set()
        all_image_urls: set[str] = set()

        for page in site.pages:
            all_css_urls.update(page.css_links)
            all_js_urls.update(page.js_links)
            all_image_urls.update(page.image_links)

        for url in all_css_urls:
            content = self._fetch_text(url)
            if content is not None:
                site.css_contents[url] = content

        for url in all_js_urls:
            content = self._fetch_text(url)
            if content is not None:
                site.js_contents[url] = content

        for url in list(all_image_urls)[:20]:
            asset = self._fetch_binary(url)
            if asset:
                site.assets.append(asset)

    def _fetch_text(self, url: str) -> Optional[str]:
        try:
            resp = self.session.get(url, timeout=self.timeout)
            resp.raise_for_status()
            return resp.text
        except Exception as e:
            logger.debug(f"Could not fetch {url}: {e}")
            return None

    def _fetch_binary(self, url: str) -> Optional[ScrapedAsset]:
        try:
            resp = self.session.get(url, timeout=self.timeout, stream=True)
            resp.raise_for_status()
            content_type = resp.headers.get("Content-Type", "").split(";")[0].strip()
            parsed = urlparse(url)
            local_path = parsed.path.lstrip("/") or "asset"
            return ScrapedAsset(
                url=url,
                content_type=content_type,
                content=resp.content,
                local_path=local_path,
            )
        except Exception as e:
            logger.debug(f"Could not fetch binary {url}: {e}")
            return None

    def _extract_title(self, soup: BeautifulSoup) -> str:
        tag = soup.find("title")
        return tag.string.strip() if tag and tag.string else ""

    def _abs(self, href: str, base: str, page_url: str) -> str:
        if href.startswith("//"):
            parsed = urlparse(page_url)
            return f"{parsed.scheme}:{href}"
        if href.startswith("http"):
            return href
        return urljoin(page_url, href)

    def _is_same_domain(self, url: str, base_url: str) -> bool:
        try:
            return urlparse(url).netloc == urlparse(base_url).netloc
        except Exception:
            return False

    def get_main_css(self, site: ScrapedSite) -> str:
        return "\n\n".join(site.css_contents.values())

    def get_main_js(self, site: ScrapedSite) -> str:
        return "\n\n".join(site.js_contents.values())

    def get_inline_styles(self, site: ScrapedSite) -> str:
        styles = []
        for page in site.pages:
            styles.extend(page.inline_styles)
        return "\n\n".join(styles)

    def extract_color_hints(self, site: ScrapedSite) -> list[str]:
        all_css = self.get_main_css(site) + self.get_inline_styles(site)
        hex_colors = re.findall(r"#(?:[0-9a-fA-F]{3}){1,2}\b", all_css)
        rgb_colors = re.findall(r"rgba?\([^)]+\)", all_css)
        return list(dict.fromkeys(hex_colors + rgb_colors))[:30]
