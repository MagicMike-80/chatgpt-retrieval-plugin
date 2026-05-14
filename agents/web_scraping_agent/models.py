from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ScrapedAsset:
    url: str
    content_type: str
    content: bytes
    local_path: str


@dataclass
class ScrapedPage:
    url: str
    html: str
    title: str
    css_links: list[str] = field(default_factory=list)
    js_links: list[str] = field(default_factory=list)
    image_links: list[str] = field(default_factory=list)
    font_links: list[str] = field(default_factory=list)
    inline_styles: list[str] = field(default_factory=list)
    inline_scripts: list[str] = field(default_factory=list)
    meta_tags: dict = field(default_factory=dict)
    links: list[str] = field(default_factory=list)


@dataclass
class ScrapedSite:
    base_url: str
    pages: list[ScrapedPage] = field(default_factory=list)
    assets: list[ScrapedAsset] = field(default_factory=list)
    css_contents: dict[str, str] = field(default_factory=dict)
    js_contents: dict[str, str] = field(default_factory=dict)


@dataclass
class SiteAnalysis:
    site_type: str
    color_scheme: list[str]
    typography: dict
    layout_structure: str
    components: list[str]
    tech_stack: list[str]
    features: list[str]
    navigation: list[str]
    description: str
    clone_strategy: str


@dataclass
class CloneResult:
    output_dir: str
    files: list[str]
    index_path: str
    summary: str
