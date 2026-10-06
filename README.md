# benjamincastleman.com

Static personal website. Content lives in `content/*.yaml`; `build.py` turns it into HTML in `docs/`, which GitHub Pages serves.

```
content/        ← edit these
  site.yaml          name, subtitle, email, footer year
  about.yaml         homepage bio
  research.yaml      publications + working papers
  partnerships.yaml  partnerships page
  writing.yaml       public writing
assets/         ← headshot.jpg, Castleman_CV.pdf, style.css, favicon
templates/base.html  page shell (header, nav, footer)
build.py        ← run this after any edit
docs/           ← generated output; erased and rebuilt every time — never put files here
```

Requires Python 3 and PyYAML (`pip install pyyaml`).

## Add a paper

Open `content/research.yaml` and paste a new entry at the top of `publications:` (or `working_papers:`):

```yaml
  - authors: Bird, Kelli A., and Benjamin L. Castleman
    year: 2026
    title: "Title of the Paper"
    journal: Journal Name
    url: https://link-to-paper
    ungated: https://link-to-free-version   # optional; delete the line if none
```

- Indentation matters: two spaces before `-`, four before the other fields.
- Put the title in quotes if it contains a colon.
- Leave out the final period. The build adds it (a `?` at the end is kept as is).
- For a paper that has no title yet, use `description:` instead of `title:`.
- Moving a paper from working papers to publications means cutting the entry from one list and pasting it into the other.

## Add a column

Add an entry at the top of `content/writing.yaml`:

```yaml
  - authors: Castleman, Benjamin L.
    year: 2026
    title: Title of the Column
    outlet: Brookings Brown Center Chalkboard
    url: https://link-to-column
```

## Edit other text

In `about.yaml` and `partnerships.yaml`, `*text*` makes italics, `**text**` makes bold, and `[text](https://url)` makes a link.

## Replace the headshot or CV

Save files with exactly these names, then rebuild:
- `assets/headshot.jpg` (portrait orientation, about 4:5; the build uses a gray placeholder until this file exists)
- `assets/Castleman_CV.pdf`

## Rebuild, preview, publish

```bash
python3 build.py
python3 -m http.server 8000 -d docs     # then open http://localhost:8000
git add -A && git commit -m "Update site" && git push
```

GitHub Pages updates about a minute after you push.

## Check links

```bash
grep -rhoE 'href="https?://[^"]+"' docs | sed 's/href="//;s/"$//' | sort -u | while read u; do echo "$(curl -s -o /dev/null -L --max-time 20 -w '%{http_code}' "$u") $u"; done
```

`200` means OK. Some publishers (Wiley, T&F, AEA, UChicago) block automated requests and return `403` even when the link works in a browser. Open those links by hand to confirm.

## One-time setup: GitHub Pages and domain

1. Create the GitHub repo and push this folder to its `main` branch.
2. In the repo, go to **Settings → Pages**. Under **Build and deployment**, choose **Deploy from a branch**, branch `main`, folder `/docs`, then **Save**.
3. Under **Custom domain**, enter `benjamincastleman.com` and **Save**. (`docs/CNAME` already contains this.)
4. At your domain registrar, add these DNS records:

   | Type  | Host/Name | Value |
   |-------|-----------|-------|
   | A     | @   | 185.199.108.153 |
   | A     | @   | 185.199.109.153 |
   | A     | @   | 185.199.110.153 |
   | A     | @   | 185.199.111.153 |
   | AAAA  | @   | 2606:50c0:8000::153 |
   | AAAA  | @   | 2606:50c0:8001::153 |
   | AAAA  | @   | 2606:50c0:8002::153 |
   | AAAA  | @   | 2606:50c0:8003::153 |
   | CNAME | www | `bcastleman-uva.github.io` |

   Delete any existing "parking" A or CNAME records for `@` or `www` that the registrar created.
5. DNS can take from a few minutes to 24 hours to propagate. Once the Pages settings show the DNS check passed, tick **Enforce HTTPS**.
