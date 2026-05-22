import pytest
from unittest.mock import MagicMock, patch
from agents.web_scraping_agent.scraper import WebScraper
from agents.web_scraping_agent.models import ScrapedPage, ScrapedSite, SiteAnalysis


SAMPLE_HTML = """<!DOCTYPE html>
<html>
<head>
  <title>Test Site</title>
  <meta name="description" content="A test site">
  <link rel="stylesheet" href="/style.css">
</head>
<body>
  <nav><a href="/">Home</a><a href="/about">About</a></nav>
  <section class="hero">
    <h1>Welcome to Test</h1>
    <p>Build amazing things</p>
    <a href="/signup">Get Started</a>
  </section>
  <section class="features">
    <div class="card"><h3>Feature 1</h3><p>Description</p></div>
    <div class="card"><h3>Feature 2</h3><p>Description</p></div>
  </section>
  <footer><p>© 2024 Test</p></footer>
</body>
</html>"""

SAMPLE_CSS = """
:root { --primary: #6366f1; --bg: #0f172a; --text: #f8fafc; }
body { background: var(--bg); color: var(--text); font-family: Inter, sans-serif; }
.hero { padding: 80px 20px; text-align: center; }
.card { background: #1e293b; border-radius: 12px; padding: 24px; }
"""


def make_site() -> ScrapedSite:
    page = ScrapedPage(
        url="https://example.com",
        html=SAMPLE_HTML,
        title="Test Site",
        css_links=["https://example.com/style.css"],
        meta_tags={"description": "A test site"},
        links=["https://example.com/about"],
    )
    site = ScrapedSite(base_url="https://example.com", pages=[page])
    site.css_contents["https://example.com/style.css"] = SAMPLE_CSS
    return site


class TestWebScraper:
    def test_is_same_domain(self):
        scraper = WebScraper()
        assert scraper._is_same_domain("https://example.com/about", "https://example.com")
        assert not scraper._is_same_domain("https://other.com", "https://example.com")

    def test_abs_relative(self):
        scraper = WebScraper()
        result = scraper._abs("/style.css", "https://example.com", "https://example.com/page")
        assert result == "https://example.com/style.css"

    def test_abs_absolute(self):
        scraper = WebScraper()
        result = scraper._abs("https://cdn.example.com/app.js", "https://example.com", "https://example.com")
        assert result == "https://cdn.example.com/app.js"

    def test_abs_protocol_relative(self):
        scraper = WebScraper()
        result = scraper._abs("//cdn.example.com/font.woff2", "https://example.com", "https://example.com")
        assert result == "https://cdn.example.com/font.woff2"

    def test_extract_color_hints(self):
        scraper = WebScraper()
        site = make_site()
        colors = scraper.extract_color_hints(site)
        assert "#6366f1" in colors
        assert "#0f172a" in colors

    def test_get_main_css(self):
        scraper = WebScraper()
        site = make_site()
        css = scraper.get_main_css(site)
        assert "--primary" in css

    @patch("requests.Session.get")
    def test_scrape_page_returns_page(self, mock_get):
        mock_resp = MagicMock()
        mock_resp.text = SAMPLE_HTML
        mock_resp.headers = {"Content-Type": "text/html"}
        mock_resp.raise_for_status = MagicMock()
        mock_get.return_value = mock_resp

        scraper = WebScraper(max_pages=1)
        page = scraper._scrape_page("https://example.com")
        assert page is not None
        assert page.title == "Test Site"
        assert "https://example.com/style.css" in page.css_links


class TestModels:
    def test_scraped_site_defaults(self):
        site = ScrapedSite(base_url="https://example.com")
        assert site.pages == []
        assert site.assets == []
        assert site.css_contents == {}
        assert site.js_contents == {}

    def test_site_analysis_fields(self):
        analysis = SiteAnalysis(
            site_type="SaaS landing page",
            color_scheme=["#6366f1", "#0f172a"],
            typography={"primary_font": "Inter"},
            layout_structure="header/hero/features/footer",
            components=["navbar", "hero", "feature-cards", "footer"],
            tech_stack=["React", "Tailwind"],
            features=["dark-mode", "animations"],
            navigation=["Home", "About", "Pricing"],
            description="A SaaS product landing page.",
            clone_strategy="Single-page HTML with Tailwind CDN",
        )
        assert analysis.site_type == "SaaS landing page"
        assert len(analysis.color_scheme) == 2
        assert "navbar" in analysis.components
