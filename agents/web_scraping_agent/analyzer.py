import json
import logging
from typing import Optional

import anthropic
from bs4 import BeautifulSoup

from .models import ScrapedSite, SiteAnalysis

logger = logging.getLogger(__name__)

ANALYZE_PROMPT = """You are an expert web developer and UI/UX analyst.

Analyze the following website data and extract detailed information about it.

Website URL: {url}
Page Title: {title}

HTML structure (first page, truncated):
{html_snippet}

CSS content (truncated):
{css_snippet}

JavaScript content (truncated):
{js_snippet}

Inline styles found:
{inline_styles}

Meta tags:
{meta_tags}

Detected colors from CSS: {colors}

Return a JSON object with exactly these fields:
{{
  "site_type": "e.g. SaaS landing page, portfolio, e-commerce, blog, dashboard, etc.",
  "color_scheme": ["#hex1", "#hex2", "#hex3", "...up to 5 main colors"],
  "typography": {{
    "primary_font": "font name or 'system default'",
    "heading_style": "bold/serif/sans-serif/etc",
    "body_style": "description"
  }},
  "layout_structure": "Description of overall layout: header/hero/sections/footer pattern",
  "components": ["list", "of", "UI", "components", "found", "e.g. navbar, hero, feature-cards, CTA, testimonials, footer"],
  "tech_stack": ["list of technologies/frameworks detected e.g. React, Tailwind, Vue, vanilla JS"],
  "features": ["list of functional features e.g. dark-mode, animations, form, video, carousel"],
  "navigation": ["list of nav links found"],
  "description": "2-3 sentence description of what this site does and who it's for",
  "clone_strategy": "Detailed technical strategy for cloning this site: what HTML structure, CSS approach, and JS to use"
}}

Return ONLY valid JSON, no markdown code blocks.
"""


class SiteAnalyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def analyze(self, site: ScrapedSite) -> SiteAnalysis:
        if not site.pages:
            raise ValueError("No pages to analyze")

        main_page = site.pages[0]
        soup = BeautifulSoup(main_page.html, "html.parser")

        html_snippet = self._clean_html(soup)
        css_snippet = self._truncate("\n\n".join(list(site.css_contents.values())[:3]), 4000)
        js_snippet = self._truncate("\n\n".join(list(site.js_contents.values())[:2]), 2000)
        inline_styles = self._truncate("\n".join(main_page.inline_styles), 1000)
        meta_tags_str = json.dumps(main_page.meta_tags, indent=2)

        from .scraper import WebScraper
        scraper = WebScraper()
        colors = scraper.extract_color_hints(site)

        prompt = ANALYZE_PROMPT.format(
            url=main_page.url,
            title=main_page.title,
            html_snippet=html_snippet,
            css_snippet=css_snippet,
            js_snippet=js_snippet,
            inline_styles=inline_styles,
            meta_tags=meta_tags_str,
            colors=", ".join(colors[:20]),
        )

        logger.info("Analyzing site with Claude...")
        message = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}],
        )

        raw = message.content[0].text.strip()
        data = json.loads(raw)

        return SiteAnalysis(
            site_type=data.get("site_type", "website"),
            color_scheme=data.get("color_scheme", []),
            typography=data.get("typography", {}),
            layout_structure=data.get("layout_structure", ""),
            components=data.get("components", []),
            tech_stack=data.get("tech_stack", []),
            features=data.get("features", []),
            navigation=data.get("navigation", []),
            description=data.get("description", ""),
            clone_strategy=data.get("clone_strategy", ""),
        )

    def _clean_html(self, soup: BeautifulSoup) -> str:
        for tag in soup(["script", "style", "noscript"]):
            tag.decompose()
        text = soup.prettify()
        return self._truncate(text, 6000)

    def _truncate(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n... [truncated, {len(text) - max_chars} more chars]"
