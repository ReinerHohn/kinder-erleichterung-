#!/usr/bin/env python3
"""Baut aus hebel/*.json ein durchsuchbares, self-contained dashboard.html
sowie KATALOG.md. Nur Python-Standardbibliothek.

    python3 build.py           # baut dashboard.html + KATALOG.md
    python3 build.py --check   # nur validieren, nichts schreiben
"""
import json
import glob
import html
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
HEBEL_DIR = os.path.join(HERE, "hebel")
OUT_HTML = os.path.join(HERE, "dashboard.html")
OUT_MD = os.path.join(HERE, "KATALOG.md")

REQUIRED = ["id", "name", "category", "summary", "protocol"]
LEVELS = {"A", "B", "C"}

# Reihenfolge der Kategorien im Dashboard (alles andere danach, alphabetisch)
CAT_ORDER = [
    "🧭 Strategie & Synthese",
    "🍼 Stressoren im Alltag",
    "📉 Ursachen: weniger Kinderwunsch",
    "🛠️ Lösungen & Politik",
    "🤖 KI & Robotik",
    "🚀 Frontier & Zukunftstechnik",
    "💡 Sweet Spots (Produkte & Gadgets)",
    "💼 Service- & Geschäftsideen",
    "📋 Was auf mich zukommt (Rechte & Fahrplan)",
]


def load():
    cards, errors = [], []
    for path in sorted(glob.glob(os.path.join(HEBEL_DIR, "*.json"))):
        base = os.path.basename(path)
        try:
            with open(path, encoding="utf-8") as f:
                d = json.load(f)
        except json.JSONDecodeError as e:
            errors.append(f"{base}: ungueltiges JSON ({e})")
            continue
        for field in REQUIRED:
            if not d.get(field):
                errors.append(f"{base}: Pflichtfeld '{field}' fehlt/leer")
        if d.get("id") and d["id"] != base[:-5]:
            errors.append(f"{base}: id '{d['id']}' != Dateiname")
        if d.get("evidence_level") and d["evidence_level"] not in LEVELS:
            errors.append(f"{base}: evidence_level '{d['evidence_level']}' nicht in A/B/C")
        d.setdefault("impact", 3)
        d.setdefault("effort", 3)
        d.setdefault("evidence_level", "C")
        cards.append(d)
    return cards, errors


def cat_key(cat):
    return (CAT_ORDER.index(cat), "") if cat in CAT_ORDER else (len(CAT_ORDER), cat)


def render_html(cards):
    cats = sorted({c["category"] for c in cards}, key=cat_key)
    data_json = json.dumps(cards, ensure_ascii=False)
    names = {c["id"]: c.get("name", c["id"]) for c in cards}
    names_json = json.dumps(names, ensure_ascii=False)
    cat_opts = "".join(
        f'<option value="{html.escape(c, True)}">{html.escape(c, True)}</option>' for c in cats
    )
    counts = {c: sum(1 for x in cards if x["category"] == c) for c in cats}
    chips = "".join(
        f'<button class="catchip" data-cat="{html.escape(c, True)}">{html.escape(c, True)} '
        f'<span class="n">{counts[c]}</span></button>'
        for c in cats
    )
    return (
        TEMPLATE.replace("__DATA__", data_json)
        .replace("__NAMES__", names_json)
        .replace("__CATOPTS__", cat_opts)
        .replace("__CHIPS__", chips)
        .replace("__COUNT__", str(len(cards)))
        .replace("__NCATS__", str(len(cats)))
    )


def render_md(cards):
    out = ["# Kinder-Erleichterung — Katalog\n",
           f"> {len(cards)} evidenzbasierte Karten. Automatisch aus `hebel/*.json` gebaut — nicht von Hand editieren.\n",
           "> ⚠️ Wissenswerkzeug, kein medizinischer/rechtlicher/steuerlicher Rat. Evidenzgrad (A/B/C) und Risiken stehen pro Karte.\n"]
    for cat in sorted({c["category"] for c in cards}, key=cat_key):
        cc = [c for c in cards if c["category"] == cat]
        cc.sort(key=lambda x: -(x["impact"] / max(1, x["effort"])))
        out.append(f"\n## {cat}  ({len(cc)})\n")
        for c in cc:
            out.append(f"### {c['name']}")
            out.append(f"*Wirkung {c['impact']}/5 · Aufwand {c['effort']}/5 · Evidenz {c['evidence_level']}*\n")
            out.append(c["summary"] + "\n")
            for kf in c.get("key_facts", []):
                src = f" ({kf['source']})" if kf.get("source") else ""
                out.append(f"- **{kf['label']}:** {kf['value']}{src}")
            if c.get("deep_dive"):
                out.append("\n" + c["deep_dive"])
            if c.get("protocol"):
                out.append("\n**Konkret:**")
                out += [f"- {p}" for p in c["protocol"]]
            if c.get("risks"):
                out.append(f"\n**Risiken:** {c['risks']}")
            if c.get("sources"):
                out.append("\n**Quellen:** " + " · ".join(
                    f"[{html.escape(s.get('title',''))}]({s.get('url','')})" for s in c["sources"]))
            out.append("\n---\n")
    return "\n".join(out)


TEMPLATE = r"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Kinder-Erleichterung — Katalog</title>
<style>
  :root { --bg:#0f1117; --card:#1a1d27; --fg:#e6e8ee; --mut:#9aa0b4; --acc:#6ea8fe; --warn:#ffb454; --ok:#7ee2a8; --bad:#ff8b8b; --line:#262a38; }
  * { box-sizing:border-box; }
  body { margin:0; font:15px/1.55 system-ui,-apple-system,sans-serif; background:var(--bg); color:var(--fg); }
  header { padding:22px 20px 6px; }
  h1 { margin:0 0 4px; font-size:23px; }
  .sub { color:var(--mut); font-size:13px; max-width:72ch; }
  .disc { margin:10px 20px; padding:9px 12px; background:#241d10; border:1px solid #4a3a17; border-radius:8px; color:var(--warn); font-size:12.5px; }
  .controls { position:sticky; top:0; background:var(--bg); padding:11px 20px; display:flex; gap:8px; flex-wrap:wrap; border-bottom:1px solid var(--line); z-index:20; }
  input, select { background:var(--card); color:var(--fg); border:1px solid #2c3040; border-radius:8px; padding:8px 10px; font-size:14px; }
  input#q { flex:1; min-width:200px; }
  .chips { padding:12px 20px 2px; display:flex; gap:8px; flex-wrap:wrap; }
  .catchip { background:var(--card); color:var(--fg); border:1px solid #2c3040; border-radius:999px; padding:6px 12px; font-size:12.5px; cursor:pointer; }
  .catchip.active { border-color:var(--acc); color:var(--acc); }
  .catchip .n { color:var(--mut); font-size:11px; }
  .grid { display:grid; grid-template-columns:repeat(auto-fill,minmax(340px,1fr)); gap:14px; padding:14px 20px 60px; }
  .card { background:var(--card); border:1px solid var(--line); border-radius:12px; padding:14px 15px; cursor:pointer; transition:border-color .15s; }
  .card:hover { border-color:#3b445e; }
  .card h3 { margin:0 0 6px; font-size:16px; line-height:1.3; }
  .badges { display:flex; gap:6px; flex-wrap:wrap; margin-bottom:8px; }
  .b { font-size:11px; padding:2px 7px; border-radius:6px; border:1px solid #333; color:var(--mut); }
  .b.A { color:var(--ok); border-color:#2c5b41; } .b.B { color:var(--warn); border-color:#5b4a22; } .b.C { color:var(--bad); border-color:#5b2f2f; }
  .b.ratio { color:var(--acc); border-color:#2c456b; }
  .card p.sum { margin:6px 0 0; color:#cfd3e0; font-size:13.5px; }
  .cat-tag { font-size:11px; color:var(--mut); }
  dialog { background:var(--card); color:var(--fg); border:1px solid #33384a; border-radius:14px; max-width:760px; width:94vw; padding:0; }
  dialog::backdrop { background:rgba(0,0,0,.6); }
  .modal-in { padding:20px 22px 26px; }
  .modal-in h2 { margin:0 0 8px; font-size:20px; }
  .modal-in h4 { margin:16px 0 6px; font-size:13px; text-transform:uppercase; letter-spacing:.05em; color:var(--acc); }
  .kf { display:grid; grid-template-columns:auto 1fr; gap:4px 12px; font-size:13.5px; }
  .kf .l { color:var(--mut); }
  .kf .s { color:var(--mut); font-size:11px; }
  ul.tight { margin:4px 0; padding-left:18px; } ul.tight li { margin:3px 0; font-size:13.5px; }
  .risks { background:#2a1a1a; border:1px solid #5b2f2f; border-radius:8px; padding:9px 11px; font-size:13px; color:#ffbcbc; }
  .src a { color:var(--acc); font-size:12.5px; }
  .close { float:right; background:none; border:none; color:var(--mut); font-size:22px; cursor:pointer; }
  .syn button { background:none; border:none; color:var(--acc); cursor:pointer; font-size:12.5px; padding:0; text-decoration:underline; }
  .empty { color:var(--mut); padding:40px 20px; text-align:center; }
  .tool { margin:12px 20px; background:var(--card); border:1px solid #2c3a4a; border-radius:12px; padding:14px 16px; }
  .tool h3 { margin:0 0 4px; font-size:16px; }
  .tool .hint { color:var(--mut); font-size:12.5px; margin-bottom:10px; }
  table.u { border-collapse:collapse; width:100%; font-size:13px; margin-top:8px; }
  table.u th, table.u td { text-align:left; padding:6px 9px; border-bottom:1px solid var(--line); }
  table.u th { color:var(--mut); font-size:11px; text-transform:uppercase; }
  tr.due { background:#17241a; } tr.soon { background:#241f10; } tr.past td { color:var(--mut); }
  .pill { font-size:11px; padding:1px 7px; border-radius:999px; }
  .pill.due { background:#1f4a2f; color:var(--ok); } .pill.soon { background:#4a3a17; color:var(--warn); } .pill.past { background:#2a2d38; color:var(--mut); }
  label { font-size:13.5px; }
</style>
</head>
<body>
<header>
  <h1>🍼 Kinder-Erleichterung — Katalog</h1>
  <div class="sub"><b id="shown">__COUNT__</b> von __COUNT__ evidenzbasierten Karten in __NCATS__ Kategorien: was Kinder stressig macht, warum viele weniger Kinder wollen, was hilft — und wo KI, Robotik &amp; clevere Produkte real entlasten. Standard-Sortierung: <b>Sweet Spots zuerst</b> (viel Wirkung ÷ wenig Aufwand).</div>
</header>
<div class="disc">⚠️ Wissenswerkzeug, kein medizinischer, rechtlicher oder steuerlicher Rat. Evidenzgrad (A = mehrere Studien/Gesetz · B = einzelne Studien/offiziell · C = plausibel/variiert) und Risiken stehen pro Karte. Im Einzelfall Fachperson hinzuziehen.</div>

<div class="tool" id="u-tool">
  <h3>📅 U-Untersuchungs-Terminrechner (U1–U9, J1)</h3>
  <div class="hint">Es gibt keine offizielle API dafür — die Zeitfenster (G-BA/BZgA) sind hier fest hinterlegt. Geburtsdatum eingeben → alle Fälligkeiten inkl. „jetzt fällig"-Markierung. Läuft komplett offline im Browser.</div>
  <label>Geburtsdatum des Kindes: <input type="date" id="birth"></label>
  <div id="u-out"></div>
</div>

<div class="controls">
  <input id="q" placeholder="Suche: Schlaf, Kita, Elterngeld, SNOO, Betreuung, Steuer …">
  <select id="cat"><option value="">Alle Kategorien</option>__CATOPTS__</select>
  <select id="ev"><option value="">Evidenz: alle</option><option value="A">nur A</option><option value="A,B">A + B</option></select>
  <select id="sort">
    <option value="ratio">Sortierung: Sweet Spots (Wirkung÷Aufwand)</option>
    <option value="impact">Wirkung/Relevanz</option>
    <option value="effort-asc">geringster Aufwand</option>
    <option value="evidence">beste Evidenz</option>
    <option value="name">Name (A–Z)</option>
  </select>
</div>
<div class="chips" id="chips"><button class="catchip active" data-cat="">Alle</button>__CHIPS__</div>
<div class="grid" id="grid"></div>

<dialog id="modal"><div class="modal-in" id="modal-in"></div></dialog>

<script>
const DATA = __DATA__;
const NAMES = __NAMES__;
const EVRANK = {A:3,B:2,C:1};
const esc = s => (s==null?"":String(s)).replace(/[&<>"]/g,c=>({"&":"&amp;","<":"&lt;",">":"&gt;",'"':"&quot;"}[c]));
let curCat="", curEv="", curSort="ratio", curQ="";

function ratio(c){ return c.impact/Math.max(1,c.effort); }
function sortCards(a){
  const f={
    ratio:(x,y)=>ratio(y)-ratio(x)||y.impact-x.impact,
    impact:(x,y)=>y.impact-x.impact||ratio(y)-ratio(x),
    "effort-asc":(x,y)=>x.effort-y.effort||ratio(y)-ratio(x),
    evidence:(x,y)=>EVRANK[y.evidence_level]-EVRANK[x.evidence_level]||y.impact-x.impact,
    name:(x,y)=>x.name.localeCompare(y.name,"de"),
  }[curSort];
  return a.slice().sort(f);
}
function matches(c){
  if(curCat && c.category!==curCat) return false;
  if(curEv){ const ok=curEv.split(","); if(!ok.includes(c.evidence_level)) return false; }
  if(curQ){ const h=(c.name+" "+c.summary+" "+(c.tags||[]).join(" ")+" "+c.category+" "+(c.deep_dive||"")).toLowerCase();
            if(!curQ.toLowerCase().split(/\s+/).every(t=>h.includes(t))) return false; }
  return true;
}
function card(c){
  return `<div class="card" data-id="${esc(c.id)}">
    <div class="cat-tag">${esc(c.category)}</div>
    <h3>${esc(c.name)}</h3>
    <div class="badges">
      <span class="b ratio">Wirkung ${c.impact} · Aufwand ${c.effort}</span>
      <span class="b ${c.evidence_level}">Evidenz ${c.evidence_level}</span>
    </div>
    <p class="sum">${esc(c.summary)}</p></div>`;
}
function draw(){
  const list=sortCards(DATA.filter(matches));
  document.getElementById("grid").innerHTML = list.length
    ? list.map(card).join("")
    : '<div class="empty">Keine Karte passt zu Filter/Suche.</div>';
  document.getElementById("shown").textContent=list.length;
}
function kfRow(k){ return `<div class="l">${esc(k.label)}</div><div>${esc(k.value)}${k.source?` <span class="s">(${esc(k.source)})</span>`:""}</div>`; }
function openCard(id){
  const c=DATA.find(x=>x.id===id); if(!c) return;
  let h=`<button class="close" onclick="document.getElementById('modal').close()">×</button>`;
  h+=`<div class="cat-tag">${esc(c.category)}</div><h2>${esc(c.name)}</h2>`;
  h+=`<div class="badges"><span class="b ratio">Wirkung ${c.impact}/5 · Aufwand ${c.effort}/5</span><span class="b ${c.evidence_level}">Evidenz ${c.evidence_level}</span>`;
  (c.tags||[]).forEach(t=>h+=`<span class="b">${esc(t)}</span>`); h+=`</div>`;
  h+=`<p>${esc(c.summary)}</p>`;
  if(c.key_facts&&c.key_facts.length){ h+=`<h4>Kennzahlen</h4><div class="kf">`+c.key_facts.map(kfRow).join("")+`</div>`; }
  if(c.deep_dive){ h+=`<h4>Hintergrund</h4><p>${esc(c.deep_dive)}</p>`; }
  if(c.mechanism){ h+=`<h4>Warum es wirkt</h4><p>${esc(c.mechanism)}</p>`; }
  if(c.protocol&&c.protocol.length){ h+=`<h4>Konkret tun</h4><ul class="tight">`+c.protocol.map(p=>`<li>${esc(p)}</li>`).join("")+`</ul>`; }
  if(c.mistakes&&c.mistakes.length){ h+=`<h4>Häufige Fehler</h4><ul class="tight">`+c.mistakes.map(p=>`<li>${esc(p)}</li>`).join("")+`</ul>`; }
  if(c.evidence&&c.evidence.length){ h+=`<h4>Belege</h4><ul class="tight">`+c.evidence.map(e=>`<li>${esc(e.source)}${e.year?` (${e.year})`:""}: ${esc(e.finding)}</li>`).join("")+`</ul>`; }
  if(c.risks){ h+=`<h4>Risiken &amp; Grenzen</h4><div class="risks">${esc(c.risks)}</div>`; }
  if(c.synergy&&c.synergy.length){ const links=c.synergy.map(s=>NAMES[s]?`<button onclick="openCard('${esc(s)}')">${esc(NAMES[s])}</button>`:"").filter(Boolean).join(" · "); if(links) h+=`<h4>Verwandt</h4><div class="syn">`+links+`</div>`; }
  if(c.sources&&c.sources.length){ h+=`<h4>Quellen</h4><div class="src">`+c.sources.map(s=>`<a href="${esc(s.url)}" target="_blank" rel="noopener">${esc(s.title||s.url)}</a>`).join("<br>")+`</div>`; }
  document.getElementById("modal-in").innerHTML=h;
  document.getElementById("modal").showModal();
}
document.getElementById("grid").addEventListener("click",e=>{const el=e.target.closest(".card"); if(el) openCard(el.dataset.id);});
document.getElementById("q").addEventListener("input",e=>{curQ=e.target.value;draw();});
document.getElementById("cat").addEventListener("change",e=>{curCat=e.target.value;syncChips();draw();});
document.getElementById("ev").addEventListener("change",e=>{curEv=e.target.value;draw();});
document.getElementById("sort").addEventListener("change",e=>{curSort=e.target.value;draw();});
function syncChips(){ document.querySelectorAll(".catchip").forEach(b=>b.classList.toggle("active",b.dataset.cat===curCat)); }
document.getElementById("chips").addEventListener("click",e=>{const b=e.target.closest(".catchip"); if(!b)return; curCat=b.dataset.cat; document.getElementById("cat").value=curCat; syncChips(); draw();});

// ---- U-Untersuchungs-Terminrechner (Zeitfenster G-BA/BZgA) ----
const U=[
 ["U1","direkt nach der Geburt",0,0,"d"],
 ["U2","3.–10. Lebenstag",3,10,"d"],
 ["U3","4.–5. Lebenswoche",21,35,"d"],
 ["U4","3.–4. Lebensmonat",3,4,"m"],
 ["U5","6.–7. Lebensmonat",6,7,"m"],
 ["U6","10.–12. Lebensmonat",10,12,"m"],
 ["U7","21.–24. Lebensmonat",21,24,"m"],
 ["U7a","34.–36. Lebensmonat",34,36,"m"],
 ["U8","46.–48. Lebensmonat",46,48,"m"],
 ["U9","60.–64. Lebensmonat",60,64,"m"],
 ["J1","12.–14. Lebensjahr",144,168,"m"],
];
function addM(d,m){const x=new Date(d);x.setMonth(x.getMonth()+m);return x;}
function addD(d,n){const x=new Date(d);x.setDate(x.getDate()+n);return x;}
function fmt(d){return d.toLocaleDateString("de-DE",{day:"2-digit",month:"2-digit",year:"numeric"});}
function calcU(){
  const v=document.getElementById("birth").value; const out=document.getElementById("u-out");
  if(!v){ out.innerHTML=""; return; }
  const b=new Date(v+"T00:00:00"); const now=new Date(); now.setHours(0,0,0,0);
  let rows="";
  for(const [name,win,a,z,unit] of U){
    const s = unit==="d"?addD(b,a):addM(b,a);
    const e = unit==="d"?addD(b,z):addM(b,z);
    let cls="",pill="";
    if(now>e){ cls="past"; pill='<span class="pill past">vorbei</span>'; }
    else if(now>=s&&now<=e){ cls="due"; pill='<span class="pill due">JETZT fällig</span>'; }
    else { const soon=addD(now,42); if(e>=now&&s<=soon){ cls="soon"; pill='<span class="pill soon">bald</span>'; } }
    rows+=`<tr class="${cls}"><td><b>${name}</b></td><td>${win}</td><td>${fmt(s)} – ${fmt(e)}</td><td>${pill}</td></tr>`;
  }
  out.innerHTML=`<table class="u"><thead><tr><th>Termin</th><th>Zeitfenster</th><th>Fällig ca.</th><th></th></tr></thead><tbody>${rows}</tbody></table>
    <div class="hint" style="margin-top:8px">Fenster gerundet auf Lebenstage/-monate; verbindlich ist das „gelbe Heft". U10/U11/J2 sind Zusatzleistungen (nicht überall Kassenleistung) und hier nicht enthalten.</div>`;
}
document.getElementById("birth").addEventListener("change",calcU);

draw();
</script>
</body>
</html>
"""


def main():
    cards, errors = load()
    if errors:
        print("VALIDIERUNGSFEHLER:")
        for e in errors:
            print("  -", e)
        sys.exit(1)
    if "--check" in sys.argv:
        print(f"OK: {len(cards)} Karten valide.")
        return
    with open(OUT_HTML, "w", encoding="utf-8") as f:
        f.write(render_html(cards))
    with open(OUT_MD, "w", encoding="utf-8") as f:
        f.write(render_md(cards))
    print(f"dashboard.html + KATALOG.md gebaut ({len(cards)} Karten).")


if __name__ == "__main__":
    main()
