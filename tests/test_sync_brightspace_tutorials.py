from __future__ import annotations

import sys
import unittest
from pathlib import Path


REPOSITORY_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPOSITORY_ROOT / "scripts"))

from sync_brightspace_tutorials import build_payload, parse_source  # noqa: E402


def links(prefix: str, count: int) -> str:
    return "".join(
        f'<li><a href="/{prefix}/tutorial-{number}.pdf">Tutorial {number}</a></li>'
        for number in range(1, count + 1)
    )


SOURCE_FIXTURE = f"""
<div class="subpageContent">
  <div class="col-md-9 col-sm-8">
    <div id="iContent">
      <p id="mainContent_fv_PageContent_p_t_Std">Tutorial introduction. Call 863-784-7016 or email
        <a href="mailto:BrightspaceSupport@southflorida.edu">Brightspace Support</a>.</p>
      <h2>Student Tutorials</h2>
      <p>Student description.</p>
    </div>
    <ul>{links('student', 6)}</ul>
    <h2>Instructor Tutorials</h2>
    <p>Instructor description.</p>
    <ul>{links('instructor', 5)}</ul>
  </div>
</div>
"""


class BrightspaceDiscoveryTests(unittest.TestCase):
    def test_new_tutorial_links_are_included_in_snapshot(self) -> None:
        source = parse_source(SOURCE_FIXTURE)

        self.assertEqual(6, len(source.student.links))
        self.assertEqual(5, len(source.instructor.links))
        self.assertTrue(source.student.links[-1][1].endswith("tutorial-6.pdf"))

        payload = build_payload(source)
        self.assertEqual(1, payload["schema_version"])
        self.assertIn(
            "tutorial-6.pdf", payload["sections"]["brightspace-student"]
        )


if __name__ == "__main__":
    unittest.main()
