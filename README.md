# Experience_Ellucian

Custom development for Ellucian Experience at SFSC. This repo contains:

- 🎴 Custom Cards (React, HTML)
- ⚙️ Power Automate Workflows & Integration Scripts
- 📄 Documentation and SOPs for internal use

## Folder Structure

- `/cards`: Source code for Experience cards
- `/scripts`: Power Automate scripts, API calls, automation logic
- `/docs`: End-user guides, internal SOPs
- `/assets`: Images, logos, and UI resources

## Getting Started

1. Clone this repo locally
2. Open in VS Code
3. Install required dependencies per card’s README
4. Push any changes to GitHub regularly

## Automated content syncs

`Pages/community.html` keeps its Corporate Education content aligned with the
public SFSC website. The `Sync Corporate Education page` GitHub Action runs
daily and can also be started manually from the Actions tab. It refreshes only
the sections enclosed by `AUTO-SYNC` comments; the custom Community Education
content remains hand-maintained. New PDF/image catalog tiles are discovered
across additional rows or tables, and previously unknown topics are placed in
an automatically displayed `Other` filter.

To preview the refresh locally:

```powershell
python -m pip install -r scripts/requirements-directory.txt
python scripts/sync_corporate_education.py --check
```

Run the script without `--check` to update the file. The scraper validates the
source layout and minimum result counts before it writes anything, so a source
site redesign fails the workflow instead of replacing the page with incomplete
content.

### Ellucian runtime updates

The sync also publishes `docs/corporate_education.json`. The loader embedded in
`Pages/community.html` requests that public snapshot from the repository's
`main` branch whenever the Ellucian page opens, then replaces only the five
marked Corporate Education sections. A cache-busting query ensures page loads
do not wait for GitHub's normal raw-file cache. If the request fails, the page
keeps the last embedded HTML instead of showing empty content.

Deployment order:

1. Merge the automation pull request into `main`.
2. Confirm `docs/corporate_education.json` is available on `main`.
3. Paste the merged `Pages/community.html` into Ellucian Page Designer and
   republish it once.
4. Keep `allow-scripts`, `allow-popups`, and
   `allow-popups-to-escape-sandbox` enabled. Enable `allow-downloads` if catalog
   PDFs should download rather than open in a browser tab.

After that one-time republish, scheduled snapshot changes appear the next time
the Ellucian page is loaded. The runtime URL is intentionally public and must
never contain credentials or student data.

### Brightspace tutorial sync

`Pages/BrightSpace.html` follows the same embedded-fallback and runtime-snapshot
pattern. `Sync Brightspace tutorials` runs daily at 11:00 UTC and publishes
`docs/brightspace_tutorials.json`. It discovers every link in the Student and
Instructor Tutorial lists, so newly added tutorials and revised PDF URLs flow
into Ellucian automatically.

To deploy it, merge its automation pull request, paste the merged
`Pages/BrightSpace.html` into the matching Ellucian Page Designer page, and
republish once with scripts and popup permissions enabled. `allow-downloads`
is recommended for tutorial PDFs. To preview locally, run:

```powershell
python scripts/sync_brightspace_tutorials.py --check
```

---

> 🔐 Internal Use Only – Do not upload files containing sensitive student data.
