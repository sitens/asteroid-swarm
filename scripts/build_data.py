"""Process raw JPL SBDB + CNEOS CAD pulls into compact site/data.js.

Selection: every potentially hazardous asteroid (PHA) + the largest of the
remaining NEOs (lowest absolute magnitude H) up to ~4,500 total, plus any
object appearing in the close-approach list so fly-to always resolves.
"""
import json, math, os

HERE = os.path.dirname(os.path.abspath(__file__))
RAW = os.path.join(HERE, "..", "data", "raw")
OUT = os.path.join(HERE, "..", "site", "data.js")

TARGET_TOTAL = 4500
J2000 = 2451545.0
LD_AU = 0.002569555  # 1 lunar distance in au

CLASSES = ["APO", "ATE", "AMO", "IEO"]  # Apollo, Aten, Amor, Atira
CLASS_IDX = {c: i for i, c in enumerate(CLASSES)}

with open(os.path.join(RAW, "sbdb_raw.json")) as f:
    sbdb = json.load(f)
with open(os.path.join(RAW, "cad_raw.json")) as f:
    cad = json.load(f)

fi = {name: i for i, name in enumerate(sbdb["fields"])}

def fnum(row, key):
    v = row[fi[key]]
    if v is None or v == "":
        return None
    try:
        return float(v)
    except ValueError:
        return None

rows = []
for r in sbdb["data"]:
    e = fnum(r, "e"); a = fnum(r, "a"); i = fnum(r, "i")
    om = fnum(r, "om"); w = fnum(r, "w"); ma = fnum(r, "ma")
    ep = fnum(r, "epoch"); per = fnum(r, "per"); H = fnum(r, "H")
    cls = r[fi["class"]]; pha = 1 if r[fi["pha"]] == "Y" else 0
    if None in (e, a, i, om, w, ma, ep, per) or cls not in CLASS_IDX:
        continue
    if e >= 0.995 or a <= 0 or per <= 0:
        continue
    if H is None:
        H = 28.0  # unknown -> assume tiny
    pdes = r[fi["pdes"]]; name = r[fi["name"]]
    label = f"{pdes} {name}".strip() if name else pdes
    rows.append({
        "des": pdes, "label": label, "a": a, "e": e, "i": i, "om": om,
        "w": w, "ma": ma, "ep": ep, "per": per, "H": H,
        "cls": CLASS_IDX[cls], "pha": pha,
    })

print(f"usable NEO rows: {len(rows)}")

cad_des = {r[0] for r in cad["data"]}
pha_rows = [r for r in rows if r["pha"]]
rest = sorted((r for r in rows if not r["pha"]), key=lambda r: r["H"])
selected = list(pha_rows)
sel_des = {r["des"] for r in selected}
for r in rest:
    if len(selected) >= TARGET_TOTAL:
        break
    selected.append(r); sel_des.add(r["des"])
# force-include every close-approach object
by_des = {r["des"]: r for r in rows}
for d in sorted(cad_des):
    if d not in sel_des and d in by_des:
        selected.append(by_des[d]); sel_des.add(d)

selected.sort(key=lambda r: r["H"])
index_of = {r["des"]: i for i, r in enumerate(selected)}
print(f"selected: {len(selected)}  (PHA {sum(r['pha'] for r in selected)})")

def rnd(x, n):
    v = round(x, n)
    return int(v) if v == int(v) else v

ast = []
for r in selected:
    ast.append([
        r["label"],
        rnd(r["a"], 5), rnd(r["e"], 5), rnd(r["i"], 3), rnd(r["om"], 3),
        rnd(r["w"], 3), rnd(r["ma"], 3), rnd(r["ep"] - J2000, 2),
        rnd(r["per"], 2), rnd(r["H"], 2), r["cls"], r["pha"],
    ])

cfi = {name: i for i, name in enumerate(cad["fields"])}
capp = []
for r in cad["data"]:
    des = r[cfi["des"]]
    jd = float(r[cfi["jd"]])
    dist_ld = float(r[cfi["dist"]]) / LD_AU
    vrel = float(r[cfi["v_rel"]])
    h = r[cfi["h"]]
    capp.append([
        rnd(jd - J2000, 3), index_of.get(des, -1), des,
        rnd(dist_ld, 2), rnd(vrel, 1),
        rnd(float(h), 1) if h not in (None, "") else None,
    ])
capp.sort(key=lambda x: x[0])
print(f"close approaches kept: {len(capp)}  (matched {sum(1 for c in capp if c[1] >= 0)})")

payload = {
    "generated": "2026-07-27",
    "source": "NASA/JPL SBDB Query API + CNEOS CAD API",
    "classes": CLASSES,
    "ast": ast,
    "cad": capp,
}
js = "window.NEO_DATA=" + json.dumps(payload, separators=(",", ":")) + ";\n"
with open(OUT, "w") as f:
    f.write(js)
print(f"wrote {OUT}  ({len(js)/1024:.0f} KB)")
