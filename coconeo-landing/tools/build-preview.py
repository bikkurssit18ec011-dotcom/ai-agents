"""Build a single-page preview (CSS + JS inlined) for hosting as a claude.ai artifact.
Images stay as separate files next to the page. Output: dist/preview.html"""
import re, pathlib
root = pathlib.Path(__file__).resolve().parent.parent
html = (root / "index.html").read_text()
css = (root / "assets/css/styles.css").read_text().replace('url("../img/', 'url("assets/img/')
head = re.search(r"<head>(.*?)</head>", html, re.S).group(1)
body = re.search(r"<body>(.*)</body>", html, re.S).group(1)
title = re.search(r"<title>.*?</title>", head).group(0)
fonts = re.search(r'<link href="https://fonts.googleapis.com[^>]+>', head).group(0)
scripts = "".join(f"<script>\n{(root / p).read_text()}\n</script>\n" for p in re.findall(r'<script src="([^"]+)"></script>', body))
body = re.sub(r'<script src="[^"]+"></script>\s*', "", body)
schema = '<script type="application/ld+json" id="product-schema"></script>'
out = f"""<title>Coco Neo Coconut Oil</title>
<meta name="claude:viewport-fit-sides" content="cover">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
{fonts}
<style>
{css}
</style>
{schema}
{body}
{scripts}"""
(root / "dist").mkdir(exist_ok=True)
(root / "dist/preview.html").write_text(out)
print("wrote dist/preview.html", len(out))
