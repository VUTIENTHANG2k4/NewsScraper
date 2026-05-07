from scraper.extractor import extract_article_links, extract_attribute, extract_text

SAMPLE_HTML = """
<html>
  <head>
    <meta property="og:image" content="https://img.example.com/cover.jpg" />
  </head>
  <body>
    <h1 class="title">  Tieu de bai viet  </h1>
    <div class="author">  Tac gia A  </div>
    <div class="article-list">
      <a href="/tin-1">Tin 1</a>
      <a href="https://example.com/tin-2">Tin 2</a>
      <a href="//example.com/tin-3">Tin 3</a>
      <a href="/tin-1">Tin 1 duplicate</a>
    </div>
  </body>
</html>
"""


def test_extract_text_success() -> None:
    result = extract_text(SAMPLE_HTML, ".title")
    assert result == "Tieu de bai viet"


def test_extract_text_returns_none_when_not_found() -> None:
    assert extract_text(SAMPLE_HTML, ".not-found") is None


def test_extract_attribute_success() -> None:
    result = extract_attribute(SAMPLE_HTML, "meta[property='og:image']", "content")
    assert result == "https://img.example.com/cover.jpg"


def test_extract_attribute_returns_none_when_missing() -> None:
    assert extract_attribute(SAMPLE_HTML, ".author", "content") is None


def test_extract_article_links_handles_relative_and_dedup() -> None:
    links = extract_article_links(
        SAMPLE_HTML,
        ".article-list a",
        base_url="https://example.com",
    )
    assert links == [
        "https://example.com/tin-1",
        "https://example.com/tin-2",
        "https://example.com/tin-3",
    ]


def test_extract_xpath_mode_returns_empty_or_none() -> None:
    assert extract_text(SAMPLE_HTML, "//h1", selector_type="xpath") is None
    assert extract_attribute(SAMPLE_HTML, "//meta", "content", selector_type="xpath") is None
    assert extract_article_links(SAMPLE_HTML, "//a", "https://example.com", "xpath") == []
