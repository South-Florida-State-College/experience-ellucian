from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from sync_corporate_education import parse_source, render_catalogs  # noqa: E402


def navigation_fixture() -> str:
    return "".join(
        f'<li><a href="/program-{number}">Program {number}</a></li>'
        for number in range(1, 11)
    )


SOURCE_FIXTURE = f"""
<div class="subpageContent">
  <div class="sideNav">
    <li class="pagenav"><ul>{navigation_fixture()}</ul></li>
  </div>
  <div class="col-md-9 col-sm-8">
    <table>
      <tr><td>Choose a path at <a href="https://example.edu">example.edu</a>.
        Use Activation Code: TEST123</td></tr>
      <tr><td>No application is required.</td></tr>
    </table>
    <table>
      <tr>
        <td><a href="/catalogs/business.pdf"><img src="/covers/business.png" alt="Business Catalog"></a></td>
        <td><a href="/catalogs/health.pdf"><picture><img data-lazy-src="/covers/health.png" alt="Health Catalog"></picture></a></td>
        <td><a href="/catalogs/cdl.pdf"><img src="/covers/cdl.png" alt="CDL Catalog"></a></td>
      </tr>
    </table>
    <table>
      <tr><td><a href="/catalogs/new-topic.pdf"><img data-src="/covers/new-topic.png" alt="New Topic Catalog"></a></td></tr>
    </table>
    <p>Introduction one.</p>
    <p>Introduction two.</p>
    <h2>Continuing Education</h2><ul><li>Continuing item.</li></ul>
    <h2>Customized Training</h2><ul><li>Customized item.</li></ul>
    <h2>Contract Training</h2><ul><li>Contract item.</li></ul>
    <h3>Contact us:</h3>
    <p>Corporate Education<br>South Florida State College<br>600 West College Drive<br>
      Avon Park, FL 33825<br>Phone: 863-784-7034<br>
      Email: <a href="mailto:CorporateTraining@southflorida.edu">CorporateTraining@southflorida.edu</a>
    </p>
  </div>
</div>
"""


class NewCatalogTests(unittest.TestCase):
    def test_new_catalog_in_an_additional_table_is_rendered(self) -> None:
        source = parse_source(SOURCE_FIXTURE)

        self.assertEqual(4, len(source.catalogs))
        new_catalog = next(
            catalog for catalog in source.catalogs if catalog.href.endswith("new-topic.pdf")
        )
        self.assertEqual("other", new_catalog.category)
        self.assertTrue(new_catalog.image.endswith("new-topic.png"))

        rendered = render_catalogs(source)
        self.assertIn('<option value="other">Other</option>', rendered)
        self.assertIn("new-topic.pdf", rendered)
        self.assertIn("new-topic.png", rendered)


if __name__ == "__main__":
    unittest.main()
