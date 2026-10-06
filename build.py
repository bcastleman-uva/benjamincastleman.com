#!/usr/bin/env python3
"""Build benjamincastleman.com.

Reads content/*.yaml, writes the finished site to docs/ (served by GitHub Pages).
Usage:  python build.py
"""
import html
import re
import shutil
from pathlib import Path
from string import Template

import yaml

ROOT = Path(__file__).parent
CONTENT = ROOT / "content"
OUT = ROOT / "docs"

NAV = [
    ("About", "/"),
    ("Research", "/research/"),
    ("Partnerships", "/partnerships/"),
    ("Public Writing", "/writing/"),
    ("CV", None),  # filled in from site.yaml
]


def load(name):
    with open(CONTENT / f"{name}.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def inline(text):
    """Escape text, then apply tiny markup: [text](url), **bold**, *italic*."""
    s = html.escape(str(text), quote=False)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\*(.+?)\*", r"<em>\1</em>", s)
    return s


def authors(text):
    return html.escape(text)


def end_punct(text):
    """Return text with a trailing period unless it already ends in . ? or !"""
    return text if text[-1] in ".?!" else text + "."


def link(label, url):
    return f'<a href="{html.escape(url)}">{label}</a>' if url else label


def citation(e, venue_key):
    """Author. Year. "Title." *Venue.* [Ungated]"""
    parts = [authors(end_punct(e["authors"]))]
    if e.get("year"):
        parts.append(f'{html.escape(str(e["year"]))}.')
    if e.get("title"):
        title = html.escape(e["title"])
        # Keep the title's own ? or ! inside the quotes; otherwise add a period.
        if title[-1] in "?!":
            parts.append(f"“{link(title, e.get('url'))}”")
        else:
            parts.append(f"“{link(title, e.get('url'))}.”")
    elif e.get("description"):
        parts.append(link(html.escape(end_punct(e["description"])), e.get("url")))
    if e.get(venue_key):
        parts.append(f"<em>{html.escape(e[venue_key])}.</em>")
    if e.get("ungated"):
        parts.append(f'<a class="ungated" href="{html.escape(e["ungated"])}">[Ungated]</a>')
    return " ".join(parts)


def cite_list(entries, venue_key):
    items = "\n".join(f"  <li>{citation(e, venue_key)}</li>" for e in entries)
    return f'<ul class="cites">\n{items}\n</ul>'


def page(site, template, slug, title, content, headshot):
    cv = site["cv"]
    nav = []
    for label, href in NAV:
        href = href or cv
        current = ' aria-current="page"' if href == f"/{slug}" else ""
        nav.append(f'    <a href="{href}"{current}>{label}</a>')
    out = template.substitute(
        title=html.escape(title),
        description=html.escape(site["description"]),
        name=html.escape(site["name"]),
        subtitle="<br>".join(html.escape(line) for line in site["subtitle"]),
        site_url=site["url"],
        page_url=f'{site["url"]}/{slug}',
        headshot=headshot,
        nav="\n".join(nav),
        content=content,
        year=site["year"],
    )
    dest = OUT / slug / "index.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")


def main():
    site = load("site")
    template = Template((ROOT / "templates" / "base.html").read_text(encoding="utf-8"))
    cv_link = f'<a href="{site["cv"]}">CV</a>'

    # Fresh output folder
    if OUT.exists():
        shutil.rmtree(OUT)
    OUT.mkdir()
    shutil.copytree(ROOT / "assets", OUT / "assets")
    shutil.copy(ROOT / "CNAME", OUT / "CNAME")
    (OUT / ".nojekyll").touch()

    headshot = "headshot.jpg" if (ROOT / "assets" / "headshot.jpg").exists() else "headshot-placeholder.svg"
    name = site["name"]

    # About
    about = load("about")
    bio = "\n".join(f"  <p>{inline(p)}</p>" for p in about["paragraphs"])
    email = html.escape(site["email"])
    content = f"""<h1 class="visually-hidden">About</h1>
<div class="about">
  <img src="/assets/{headshot}" alt="Headshot of {html.escape(name)}" width="240" height="300">
  <div class="bio">
{bio}
  <p>email: <a href="mailto:{email}">{email}</a></p>
  </div>
</div>"""
    page(site, template, "", f"{name} | Professor of Public Policy and Education", content, headshot)

    # Research
    research = load("research")
    content = f"""<h1 class="visually-hidden">Research</h1>
<h2>Recent Publications</h2>
{cite_list(research["publications"], "journal")}
<h2>Working Papers</h2>
{cite_list(research["working_papers"], "journal")}
<p class="note">Full list of publications in my {cv_link}.</p>"""
    page(site, template, "research/", f"Research | {name}", content, headshot)

    # Partnerships
    p = load("partnerships")
    groups = "\n".join(
        f'<p class="partner-group"><strong>{inline(g["heading"])}</strong> {inline(g["text"])}</p>'
        for g in p["groups"]
    )
    closing = inline(p["closing"]).replace("{cv}", cv_link)
    content = f"""<h1>Partnerships</h1>
<p>{inline(p["intro"])}</p>
{groups}
<p>{closing}</p>"""
    page(site, template, "partnerships/", f"Partnerships | {name}", content, headshot)

    # Public Writing
    w = load("writing")
    content = f"""<h1>{html.escape(w["heading"])}</h1>
{cite_list(w["columns"], "outlet")}
<p class="note">{inline(w["closing"]).replace("{cv}", cv_link)}</p>"""
    page(site, template, "writing/", f"Public Writing | {name}", content, headshot)

    # Simple 404 page
    page(site, template, "404/", f"Page not found | {name}",
         '<h1>Page not found</h1>\n<p><a href="/">Return to the homepage.</a></p>', headshot)
    (OUT / "404" / "index.html").rename(OUT / "404.html")
    (OUT / "404").rmdir()

    print(f"Built site in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
