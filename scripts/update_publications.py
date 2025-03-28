from scholarly import scholarly
import os
import re
import datetime
from pathlib import Path

# === CONFIGURATION ===
SCHOLAR_ID = "3OHEhO0AAAAJ"  # Your Google Scholar ID

# Get absolute path to _publications relative to this script
SCRIPT_DIR = Path(__file__).resolve().parent
PUBLICATIONS_DIR = SCRIPT_DIR.parent / "_publications"


# === HELPERS ===

def slugify(title):
    """Make permalink-safe title (for permalink only, not filename)"""
    return title.strip()

def md_filename(title):
    """Generate safe filename from title"""
    clean = re.sub(r'[^a-z0-9\-]+', '',
                   re.sub(r'\s+', '-', title.lower()))
    return clean.strip('-') + ".md"

def publication_exists(title):
    return os.path.exists(os.path.join(PUBLICATIONS_DIR, md_filename(title)))

def format_date(pub_year):
    try:
        year = int(pub_year)
    except:
        year = datetime.datetime.now().year
    # default to March 2nd (you can customize this per-paper later)
    return f"02.03.{year}"

def format_citation(bib):
    raw_authors = bib.get("author", "")
    year = bib.get("pub_year", "n.d.")
    title = bib.get("title", "Untitled")
    venue = bib.get("venue", "Preprint")

    # Split authors and abbreviate
    authors = [a.strip() for a in raw_authors.split(" and ")]
    formatted_authors = []

    for a in authors:
        parts = a.split()
        if len(parts) >= 2:
            last = parts[-1]
            initials = ''.join([f"{p[0]}." for p in parts[:-1]])
            formatted_authors.append(f"{last}, {initials}")
        else:
            formatted_authors.append(a)  # fallback

    if len(formatted_authors) > 10:
        # Truncate with "et al." after first 10 authors
        formatted_authors = formatted_authors[:10] + ["et al."]

    author_str = ', '.join(formatted_authors)
    citation = f"{author_str} ({year}). {title}. {venue}."
    return citation

# === MAIN LOGIC ===

def create_md(pub):
    bib = pub['bib']
    title = bib.get("title", "Untitled")
    authors = bib.get("author", "Unknown authors")
    year = bib.get("pub_year", "n.d.")
    venue = bib.get("venue", "Unknown venue")
    abstract = bib.get("abstract", "Coming soon.")
    url = pub.get("pub_url", "")

    filename = md_filename(title)
    permalink = slugify(title)

    citation = format_citation(bib)
    date = format_date(year)

    md_content = f"""---
title: "{title}"
collection: publications
category: manuscripts
permalink: /publication/{permalink}
excerpt: '{abstract}'
date: {date}
venue: '{venue}'
# slidesurl: ''
paperurl: '{url}'
# bibtexurl: ''
citation: '{citation}'
---
"""

    filepath = os.path.join(PUBLICATIONS_DIR, filename)
    with open(filepath, "w") as f:
        f.write(md_content)
    print(f"✅ Created: {filename}")

# === RUN ===

def main():
    print(f"🔍 Fetching Google Scholar profile: {SCHOLAR_ID}")
    author = scholarly.search_author_id(SCHOLAR_ID)
    author = scholarly.fill(author)

    publications = author.get("publications", [])

    if not publications:
        print("⚠️ No publications found.")
        return

    for pub in publications:
        title = pub["bib"]["title"]
        if not publication_exists(title):
            print(f"📄 New publication: {title}")
            pub = scholarly.fill(pub)
            create_md(pub)
        else:
            print(f"✔ Already exists: {title}")

if __name__ == "__main__":
    if not os.path.exists(PUBLICATIONS_DIR):
        os.makedirs(PUBLICATIONS_DIR)
    main()
