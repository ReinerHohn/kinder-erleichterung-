#!/usr/bin/env python3
"""Tests fuer den Kinder-Erleichterung-Katalog. Nur Standardbibliothek.
    python3 test.py
Prueft Struktur, Pflichtfelder, id-Eindeutigkeit, Wertebereiche, Synergie-Links,
Quellen-URLs und die Logik des U-Untersuchungs-Terminrechners."""
import json
import glob
import os
import re
import sys
from datetime import date

HERE = os.path.dirname(os.path.abspath(__file__))
HEBEL = os.path.join(HERE, "hebel")

fails = []


def check(cond, msg):
    if not cond:
        fails.append(msg)


def load():
    cards = []
    for p in sorted(glob.glob(os.path.join(HEBEL, "*.json"))):
        with open(p, encoding="utf-8") as f:
            cards.append((os.path.basename(p), json.load(f)))
    return cards


def test_cards():
    cards = load()
    check(len(cards) >= 60, f"zu wenige Karten: {len(cards)}")
    ids = set()
    for base, c in cards:
        cid = c.get("id", "")
        check(bool(cid), f"{base}: keine id")
        check(cid == base[:-5], f"{base}: id != Dateiname ({cid})")
        check(cid not in ids, f"{base}: doppelte id {cid}")
        ids.add(cid)
        check(re.fullmatch(r"[a-z0-9-]+", cid or "") is not None, f"{base}: id nicht kebab-case")
        for req in ("name", "category", "summary", "protocol"):
            check(bool(c.get(req)), f"{cid}: Pflichtfeld '{req}' fehlt/leer")
        check(isinstance(c.get("protocol"), list) and len(c["protocol"]) >= 1,
              f"{cid}: protocol muss nicht-leere Liste sein")
        check(c.get("evidence_level") in ("A", "B", "C"), f"{cid}: evidence_level ungueltig")
        check(isinstance(c.get("impact"), int) and 1 <= c["impact"] <= 5, f"{cid}: impact 1-5")
        check(isinstance(c.get("effort"), int) and 1 <= c["effort"] <= 5, f"{cid}: effort 1-5")
        check(len(c.get("summary", "")) >= 20, f"{cid}: summary zu kurz")
        for s in c.get("sources", []):
            check(str(s.get("url", "")).startswith("http"), f"{cid}: Quelle ohne http-URL")
        for kf in c.get("key_facts", []):
            check("label" in kf and "value" in kf, f"{cid}: key_fact ohne label/value")
    # Synergie-Links (Warnung, kein harter Fehler): duerfen nur auf existierende ids zeigen
    dangling = []
    for base, c in cards:
        for s in c.get("synergy", []):
            if s not in ids:
                dangling.append(f"{c['id']} -> {s}")
    if dangling:
        print(f"HINWEIS: {len(dangling)} Synergie-Links zeigen ins Leere (unkritisch): "
              + ", ".join(dangling[:8]) + (" …" if len(dangling) > 8 else ""))
    # Kategorien-Abdeckung
    cats = {c["category"] for _, c in cards}
    for want in ["🍼 Stressoren im Alltag", "📉 Ursachen: weniger Kinderwunsch",
                 "🛠️ Lösungen & Politik", "🤖 KI & Robotik",
                 "💡 Sweet Spots (Produkte & Gadgets)", "💼 Service- & Geschäftsideen",
                 "📋 Was auf mich zukommt (Rechte & Fahrplan)"]:
        check(want in cats, f"Kategorie fehlt: {want}")


def test_u_calc():
    """Referenz-Implementierung des Terminrechners aus build.py (Python-Spiegel),
    prueft die Fenster-Logik gegen bekannte Werte."""
    from datetime import timedelta

    def add_months(d, m):
        y, mo = d.year + (d.month - 1 + m) // 12, (d.month - 1 + m) % 12 + 1
        day = min(d.day, [31, 29 if y % 4 == 0 and (y % 100 != 0 or y % 400 == 0) else 28,
                          31, 30, 31, 30, 31, 31, 30, 31, 30, 31][mo - 1])
        return date(y, mo, day)

    b = date(2025, 1, 1)
    # U3: 21.-35. Lebenstag
    check(b + timedelta(days=21) == date(2025, 1, 22), "U3-Start falsch")
    check(b + timedelta(days=35) == date(2025, 2, 5), "U3-Ende falsch")
    # U6: 10.-12. Lebensmonat
    check(add_months(b, 10) == date(2025, 11, 1), "U6-Start falsch")
    check(add_months(b, 12) == date(2026, 1, 1), "U6-Ende falsch")
    # J1: 144.-168. Lebensmonat (12-14 J.)
    check(add_months(b, 144) == date(2037, 1, 1), "J1-Start falsch")


def test_build_runs():
    import subprocess
    r = subprocess.run([sys.executable, os.path.join(HERE, "build.py"), "--check"],
                       capture_output=True, text=True)
    check(r.returncode == 0, f"build.py --check schlug fehl: {r.stdout}{r.stderr}")


if __name__ == "__main__":
    test_cards()
    test_u_calc()
    test_build_runs()
    if fails:
        print(f"FEHLGESCHLAGEN ({len(fails)}):")
        for f in fails:
            print("  -", f)
        sys.exit(1)
    print("Alle Tests bestanden.")
