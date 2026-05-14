import logging
import os
from typing import Optional

from .analyzer import SiteAnalyzer
from .cloner import SiteCloner
from .models import CloneResult, ScrapedSite, SiteAnalysis
from .scraper import WebScraper

logger = logging.getLogger(__name__)


class WebScrapingAgent:
    """
    Agent that scrapes a website, analyzes its structure with Claude,
    and generates a functional clone.

    Usage:
        agent = WebScrapingAgent()
        result = agent.run("https://emergent.sh", output_dir="./clones/emergent")
        print(result.summary)
    """

    def __init__(
        self,
        anthropic_api_key: Optional[str] = None,
        max_pages: int = 10,
        max_depth: int = 2,
        scrape_delay: float = 0.5,
    ):
        api_key = anthropic_api_key or os.environ.get("ANTHROPIC_API_KEY")
        self.scraper = WebScraper(
            max_pages=max_pages,
            max_depth=max_depth,
            delay=scrape_delay,
        )
        self.analyzer = SiteAnalyzer(api_key=api_key)
        self.cloner = SiteCloner(api_key=api_key)

    def run(
        self,
        url: str,
        output_dir: Optional[str] = None,
        skip_analysis: bool = False,
    ) -> CloneResult:
        """
        Full pipeline: scrape → analyze → clone.

        Args:
            url: Target website URL (e.g. "https://emergent.sh")
            output_dir: Where to save the clone (default: ./clones/<domain>)
            skip_analysis: If True, uses heuristic analysis instead of Claude API

        Returns:
            CloneResult with output path and summary
        """
        if not url.startswith(("http://", "https://")):
            url = "https://" + url

        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")

        if output_dir is None:
            output_dir = os.path.join("clones", domain)

        logger.info(f"[1/3] Scraping {url} ...")
        site = self.scrape(url)
        logger.info(f"      → {len(site.pages)} pages, {len(site.assets)} assets")

        logger.info("[2/3] Analyzing site structure...")
        analysis = self.analyze(site)
        logger.info(f"      → {analysis.site_type}: {analysis.description[:80]}...")

        logger.info(f"[3/3] Generating clone → {output_dir}")
        result = self.clone(site, analysis, output_dir)
        logger.info(f"      → Done: {result.index_path}")

        return result

    def scrape(self, url: str) -> ScrapedSite:
        return self.scraper.scrape(url)

    def analyze(self, site: ScrapedSite) -> SiteAnalysis:
        return self.analyzer.analyze(site)

    def clone(
        self,
        site: ScrapedSite,
        analysis: SiteAnalysis,
        output_dir: str,
    ) -> CloneResult:
        return self.cloner.clone(site, analysis, output_dir)
