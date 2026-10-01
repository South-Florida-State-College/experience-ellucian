# Ellucian Page Designer Republish Checklist

Use this checklist once for each page after its runtime loader is merged. Future
managed-content updates should not require another republish.

## Before Republish

- [ ] Merge the automation changes into the repository `main` branch.
- [ ] Confirm the matching JSON snapshot exists on `main`.
- [ ] Open the raw snapshot URL and confirm it returns valid JSON.
- [ ] Copy the complete merged HTML file, including all `AUTO-SYNC` comments and
      the runtime loader script.

## Page Mapping

| Ellucian page | HTML file | Snapshot |
|---|---|---|
| Corporate and Community Education | `Pages/community.html` | `docs/corporate_education.json` |
| Brightspace Help and Tutorials | `Pages/BrightSpace.html` | `docs/brightspace_tutorials.json` |

## Content Options

- [ ] Enable `allow-scripts`.
- [ ] Enable `allow-popups`.
- [ ] Enable `allow-popups-to-escape-sandbox`.
- [ ] Enable `allow-downloads` for PDF behavior.
- [ ] Enable `allow-forms` only when the page or embedded support tool requires
      forms.
- [ ] Leave `allow-top-navigation` disabled.
- [ ] Leave `allow-modals` disabled unless a tested feature requires it.

## Publish and Validate

- [ ] Replace the Page Designer HTML with the complete merged file.
- [ ] Preview the page before publishing.
- [ ] Click **Republish**.
- [ ] Reload the published page in a new browser session.
- [ ] Confirm current text and link counts match the public SFSC source.
- [ ] Open at least one PDF from every managed group.
- [ ] Confirm the browser console has no JSON, CORS, CSP, or marker errors.
- [ ] Confirm the page still renders acceptably on a narrow/mobile viewport.

## Fallback Test

- [ ] Temporarily block the raw GitHub request in browser developer tools or
      test with the network offline.
- [ ] Reload and confirm the embedded content remains visible.
- [ ] Restore network access and confirm live content returns on the next load.

## Ongoing Operations

- [ ] Record the Ellucian page name, HTML path, owner, and republish date in the
      team change record.
- [ ] Review failed scheduled workflows and GitHub security alerts.
- [ ] Re-run this checklist whenever loader code, marker names, or sandbox
      permissions change.
