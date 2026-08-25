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
content remains hand-maintained.

To preview the refresh locally:

```powershell
python -m pip install -r scripts/requirements-directory.txt
python scripts/sync_corporate_education.py --check
```

Run the script without `--check` to update the file. The scraper validates the
source layout and minimum result counts before it writes anything, so a source
site redesign fails the workflow instead of replacing the page with incomplete
content.

---

> 🔐 Internal Use Only – Do not upload files containing sensitive student data.
