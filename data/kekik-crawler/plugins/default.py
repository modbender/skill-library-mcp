from urllib.parse import urljoin


def extract(url: str, html: str, tree):
    title = tree.css_first("title")
    links = []
    for a in tree.css("a[href]")[:80]:
        raw = a.attributes.get("href")
        href = (raw or "").strip()
        if not href or href.startswith("#"):
            continue
        links.append(urljoin(url, href))

    text_blocks = [n.text(strip=True) for n in tree.css("p, h1, h2, h3")]
    text = "\n".join([t for t in text_blocks if t][:60])

    return {
        "title": title.text(strip=True) if title else None,
        "text": text,
        "links": links,
    }
