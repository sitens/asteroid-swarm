"""Assemble the final self-contained site/index.html:
template + inlined data.js + base64 planet/galaxy imagery."""
import base64, json, os

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, "..")
TPL = os.path.join(ROOT, "src", "template.html")
DATA = os.path.join(ROOT, "site", "data.js")
IMGDIR = os.path.join(ROOT, "data", "raw", "img")
OUT = os.path.join(ROOT, "site", "index.html")

with open(TPL, encoding="utf-8") as f:
    html = f.read()
with open(DATA, encoding="utf-8") as f:
    data_js = f.read()

imgs = {}
for fn in sorted(os.listdir(IMGDIR)):
    if not fn.endswith((".jpg", ".png")):
        continue
    key = os.path.splitext(fn)[0]
    with open(os.path.join(IMGDIR, fn), "rb") as f:
        b64 = base64.b64encode(f.read()).decode()
    mime = "image/png" if fn.endswith(".png") else "image/jpeg"
    imgs[key] = f"data:{mime};base64,{b64}"

assert "/*__DATA_JS__*/" in html and "__IMG_JSON__" in html
html = html.replace("/*__DATA_JS__*/", data_js)
html = html.replace("__IMG_JSON__", json.dumps(imgs))

with open(OUT, "w", encoding="utf-8") as f:
    f.write(html)
print(f"wrote {OUT} ({os.path.getsize(OUT)/1024:.0f} KB, {len(imgs)} images inlined)")
