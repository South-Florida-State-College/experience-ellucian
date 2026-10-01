# Automated Ellucian Content Synchronization

## Purpose

This repository keeps selected Ellucian Experience Page Designer pages aligned
with public South Florida State College webpages. Each managed page contains a
current embedded copy for reliability and a runtime loader for automatic
updates.

## Managed Pages

| Experience HTML | Public source | Generated snapshot | Workflow |
|---|---|---|---|
| `Pages/community.html` | Corporate Education | `docs/corporate_education.json` | `Sync Corporate Education page` |
| `Pages/BrightSpace.html` | Brightspace Tutorials | `docs/brightspace_tutorials.json` | `Sync Brightspace tutorials` |

Employee directory synchronization is separate and writes
`docs/employee_directory.csv`.

## Data Flow

```text
Public SFSC webpage
        |
        v
Scheduled GitHub Action
        |
        +--> validated embedded HTML in Pages/
        |
        +--> public JSON snapshot in docs/
                         |
                         v
              Ellucian sandboxed iframe
```

The Ellucian page fetches its JSON snapshot from the public repository `main`
branch whenever it opens. A timestamp query bypasses normal raw-file caching.
Only content enclosed by matching `AUTO-SYNC` comments is replaced.

If the request, JSON validation, or marker replacement fails, the runtime loader
logs a browser warning and retains the last embedded HTML. Students should not
receive an empty page because GitHub or the network is temporarily unavailable.

## Schedule

| Automation | UTC schedule | Approximate Eastern time |
|---|---:|---:|
| Employee directory | 10:15 daily | 5:15/6:15 a.m. |
| Corporate Education | 10:45 daily | 5:45/6:45 a.m. |
| Brightspace Tutorials | 11:00 daily | 6:00/7:00 a.m. |

GitHub schedules use UTC; Eastern time changes with daylight saving time.

## Content Ownership

### Corporate Education

Automatically managed:

- Corporate program navigation
- Career-assessment banner
- Catalog filters, covers, and PDF links
- Corporate Education description and training lists
- Corporate contact information

The custom Community Education content outside the markers remains
hand-maintained.

New PDF/image catalog tiles are discovered across additional table rows or
tables. Known topics receive an existing filter category; unfamiliar topics
receive `Other`.

### Brightspace Tutorials

Automatically managed:

- Introduction and support contact
- Student tutorial description and links
- Instructor tutorial description and links
- Contact panel

Every direct link in the source Student and Instructor lists is discovered, so
new tutorials do not require a code change.

## Local Operation

Install the shared dependencies:

```powershell
python -m pip install -r scripts/requirements-directory.txt
```

Check whether either page has drifted without writing files:

```powershell
python scripts/sync_corporate_education.py --check
python scripts/sync_brightspace_tutorials.py --check
```

Refresh files locally by omitting `--check`. Run the same command again with
`--check`; it must report that both HTML and JSON are current.

Run regression tests:

```powershell
python -m unittest tests.test_sync_corporate_education -v
python -m unittest tests.test_sync_brightspace_tutorials -v
```

## GitHub Operation

Each workflow can be started from **Actions > workflow name > Run workflow**.
Scheduled workflows run only from the default branch. They commit only when the
managed HTML or JSON snapshot changes.

A source layout change that violates expected selectors or safety counts fails
the workflow before files are overwritten. Investigate the live source markup,
update the parser and fixture, run the live sync twice, and review the generated
diff before merging.

## Adding Another Managed Page

1. Mark only source-owned HTML with unique `BEGIN AUTO-SYNC` and
   `END AUTO-SYNC` comments.
2. Add a scraper with retries, absolute HTTPS URL normalization, validation
   bounds, deterministic JSON, `--check`, and idempotent writes.
3. Add an offline fixture proving a newly introduced source item is rendered.
4. Add a runtime loader that validates `schema_version` and retains embedded
   content on failure.
5. Add a scheduled and manually dispatchable workflow with `contents: write`.
6. Verify the public raw snapshot returns `Access-Control-Allow-Origin: *`.
7. Follow `ELLUCIAN_REPUBLISH_CHECKLIST.md` once after the loader is merged.

## Security Boundaries

- Snapshots and source pages are public. Never include secrets or regulated
  information.
- Do not add authentication tokens to HTML, JSON, workflow files, or URLs.
- Keep `allow-top-navigation` disabled in Ellucian.
- Enable only the sandbox capabilities required by the page.
- Treat scraper failures as content-maintenance alerts, not permission to bypass
  source validation.

## Troubleshooting

| Symptom | Check |
|---|---|
| Embedded content never changes | Confirm the loader-enabled HTML was republished in Ellucian. |
| Browser console reports HTTP 404 | Confirm the JSON snapshot exists on `main`, not only on a feature branch. |
| Browser console reports a CORS or CSP error | Verify the raw URL CORS header and Ellucian iframe policy. |
| PDF link does not open | Enable popups and, when needed, downloads in Ellucian Content Options. |
| Workflow produces no commit | No source content changed, or the workflow did not run from `main`. |
| Workflow fails before writing | The source markup or result count changed; update and test the parser. |
