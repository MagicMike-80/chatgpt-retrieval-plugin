import json
import logging
import os
import re
from pathlib import Path
from typing import Optional
from urllib.parse import urlparse

import anthropic
from bs4 import BeautifulSoup

from .models import CloneResult, ScrapedSite, SiteAnalysis

logger = logging.getLogger(__name__)

CLONE_SYSTEM_PROMPT = """You are an expert full-stack web developer specializing in pixel-perfect website recreation.
Your task is to generate clean, standalone, production-quality HTML/CSS/JS code that clones the given website.
Use modern CSS features, Flexbox, Grid. Make it fully responsive. Include smooth animations where appropriate.
Output semantic, accessible HTML. Do NOT use external dependencies unless they are CDN links for fonts or icons.
"""

CLONE_PROMPT = """Clone this website as a single, self-contained HTML file.

## Site Analysis
- Type: {site_type}
- Description: {description}
- Components: {components}
- Color Scheme: {colors}
- Typography: {typography}
- Layout: {layout}
- Features: {features}
- Navigation items: {navigation}
- Clone Strategy: {strategy}

## Original HTML Structure (main page)
{html_structure}

## Original CSS Styles
{css_styles}

## Original JavaScript
{js_snippet}

## All pages found (titles/URLs)
{pages_summary}

---

Generate a COMPLETE, self-contained HTML file that:
1. Faithfully recreates the visual design and layout
2. Includes ALL sections visible on the original page
3. Uses the exact same color palette, spacing, and typography
4. Implements all interactive features (mobile menu, animations, hover effects, etc.)
5. Is fully responsive (mobile, tablet, desktop)
6. Uses Google Fonts CDN if custom fonts are needed
7. Includes Font Awesome CDN if icons are needed
8. Has smooth scroll, proper meta tags, favicon, and Open Graph tags

Output ONLY the complete HTML file content, starting with <!DOCTYPE html>.
No explanations, no markdown, just the HTML.
"""


class SiteCloner:
    def __init__(self, api_key: Optional[str] = None):
        self.client = anthropic.Anthropic(api_key=api_key) if api_key else anthropic.Anthropic()

    def clone(
        self,
        site: ScrapedSite,
        analysis: SiteAnalysis,
        output_dir: str,
    ) -> CloneResult:
        Path(output_dir).mkdir(parents=True, exist_ok=True)

        main_page = site.pages[0] if site.pages else None
        if not main_page:
            raise ValueError("No pages scraped to clone")

        soup = BeautifulSoup(main_page.html, "html.parser")
        for tag in soup(["script"]):
            tag.decompose()
        html_structure = self._truncate(soup.prettify(), 8000)

        css_styles = self._truncate(
            "\n\n".join(list(site.css_contents.values())[:5])
            + "\n\n"
            + "\n\n".join(main_page.inline_styles),
            6000,
        )

        js_snippet = self._truncate(
            "\n\n".join(list(site.js_contents.values())[:2])
            + "\n\n"
            + "\n\n".join(main_page.inline_scripts),
            3000,
        )

        pages_summary = "\n".join(
            f"- {p.title or 'Untitled'}: {p.url}" for p in site.pages
        )

        prompt = CLONE_PROMPT.format(
            site_type=analysis.site_type,
            description=analysis.description,
            components=", ".join(analysis.components),
            colors=", ".join(analysis.color_scheme),
            typography=json.dumps(analysis.typography),
            layout=analysis.layout_structure,
            features=", ".join(analysis.features),
            navigation=", ".join(analysis.navigation),
            strategy=analysis.clone_strategy,
            html_structure=html_structure,
            css_styles=css_styles,
            js_snippet=js_snippet,
            pages_summary=pages_summary,
        )

        logger.info("Generating clone with Claude...")
        message = self.client.messages.create(
            model="claude-opus-4-7",
            max_tokens=8000,
            system=CLONE_SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )

        html_content = message.content[0].text.strip()
        html_content = self._clean_html_response(html_content)

        index_path = os.path.join(output_dir, "index.html")
        with open(index_path, "w", encoding="utf-8") as f:
            f.write(html_content)

        self._save_images(site, output_dir)

        readme_path = os.path.join(output_dir, "CLONE_INFO.md")
        readme = self._generate_readme(site, analysis, output_dir)
        with open(readme_path, "w", encoding="utf-8") as f:
            f.write(readme)

        files = [index_path, readme_path]
        images_dir = os.path.join(output_dir, "images")
        if os.path.exists(images_dir):
            for img in os.listdir(images_dir):
                files.append(os.path.join(images_dir, img))

        return CloneResult(
            output_dir=output_dir,
            files=files,
            index_path=index_path,
            summary=(
                f"Cloned {analysis.site_type} from {site.base_url}. "
                f"Generated {len(files)} files. "
                f"Open {index_path} in a browser to view the clone."
            ),
        )

    def _save_images(self, site: ScrapedSite, output_dir: str) -> None:
        if not site.assets:
            return
        images_dir = os.path.join(output_dir, "images")
        os.makedirs(images_dir, exist_ok=True)
        for asset in site.assets:
            if not asset.content_type.startswith("image/"):
                continue
            filename = os.path.basename(urlparse(asset.url).path) or "image"
            safe_name = re.sub(r"[^\w\-.]", "_", filename)
            dest = os.path.join(images_dir, safe_name)
            try:
                with open(dest, "wb") as f:
                    f.write(asset.content)
            except OSError as e:
                logger.warning(f"Could not save image {asset.url}: {e}")

    def _clean_html_response(self, text: str) -> str:
        text = re.sub(r"^```html\s*", "", text, flags=re.MULTILINE)
        text = re.sub(r"^```\s*$", "", text, flags=re.MULTILINE)
        if "<!DOCTYPE html>" in text:
            idx = text.index("<!DOCTYPE html>")
            text = text[idx:]
        return text.strip()

    def _generate_readme(
        self, site: ScrapedSite, analysis: SiteAnalysis, output_dir: str
    ) -> str:
        return f"""# Clone: {site.base_url}

## Site Analysis
- **Type**: {analysis.site_type}
- **Description**: {analysis.description}
- **Pages scraped**: {len(site.pages)}

## Color Scheme
{chr(10).join(f"- `{c}`" for c in analysis.color_scheme)}

## Typography
{json.dumps(analysis.typography, indent=2)}

## Components Found
{chr(10).join(f"- {c}" for c in analysis.components)}

## Tech Stack
{chr(10).join(f"- {t}" for t in analysis.tech_stack)}

## Features
{chr(10).join(f"- {f}" for f in analysis.features)}

## Pages
{chr(10).join(f"- [{p.title or p.url}]({p.url})" for p in site.pages)}

## How to view
Open `index.html` in a web browser.
"""

    def _truncate(self, text: str, max_chars: int) -> str:
        if len(text) <= max_chars:
            return text
        return text[:max_chars] + f"\n... [truncated]"
