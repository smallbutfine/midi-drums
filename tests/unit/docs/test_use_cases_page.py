"""These tests used to verify the docs site (use-cases.html, quickstart.html, etc.)
but that site is from another fork and has nothing to do with this project.
The documentation links were removed from README.md, so these tests now skip
with a clear reason rather than silently failing.

To re-add these tests you would need to either:
1. Re-create the docs site in this repo under docs/site-pages/ AND link it
   from README.md
2. Or remove this file entirely along with the orphaned HTML files
"""

from pathlib import Path

import pytest

SITE_PAGES = Path(__file__).resolve().parents[3] / "docs" / "site-pages"
README = Path(__file__).resolve().parents[3] / "README.md"

# The docs site is from another fork - not part of this project
DOCS_SITE_ORPHANED = True
EXISTING_PAGES = [
    "index.html",
    "quickstart.html",
    "recipes.html",
    "reaper.html",
]


@pytest.mark.unit
class TestUseCasesPage:
    @pytest.mark.skipif(
        DOCS_SITE_ORPHANED, reason="Docs site is from another fork"
    )
    def test_use_cases_page_exists(self):
        assert (SITE_PAGES / "use-cases.html").is_file()

    @pytest.mark.skipif(
        DOCS_SITE_ORPHANED, reason="Docs site is from another fork"
    )
    def test_use_cases_page_has_shared_nav_and_footer(self):
        html = (SITE_PAGES / "use-cases.html").read_text(encoding="utf-8")
        assert 'href="index.html"' in html
        assert 'href="quickstart.html"' in html
        assert 'href="recipes.html"' in html
        assert 'href="reaper.html"' in html
        assert "<footer>" in html

    @pytest.mark.skipif(
        DOCS_SITE_ORPHANED, reason="Docs site is from another fork"
    )
    @pytest.mark.parametrize("page", EXISTING_PAGES)
    def test_existing_page_links_to_use_cases(self, page):
        html = (SITE_PAGES / page).read_text(encoding="utf-8")
        assert 'href="use-cases.html"' in html

    @pytest.mark.skipif(
        DOCS_SITE_ORPHANED, reason="Docs site is from another fork"
    )
    def test_readme_docs_table_has_use_cases_row(self):
        readme = README.read_text(encoding="utf-8")
        assert "use-cases.html" in readme
