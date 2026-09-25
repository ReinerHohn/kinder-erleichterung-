#!/usr/bin/env bash
# Startet ALLES: baut den Katalog, prüft ihn, startet einen lokalen Server
# und öffnet Dashboard + Familien-Helfer im Browser.
# Beenden mit Strg+C.
set -e
cd "$(dirname "$0")"

PORT="${PORT:-8747}"

echo "==> Baue Katalog (dashboard.html + KATALOG.md) ..."
python3 build.py

echo "==> Prüfe Katalog ..."
python3 test.py || echo "(Tests meldeten etwas – Dashboard wird trotzdem gestartet)"

# Freien Port suchen, falls belegt
is_free() { ! (exec 3<>"/dev/tcp/127.0.0.1/$1") 2>/dev/null; }
while ! is_free "$PORT"; do PORT=$((PORT+1)); done

URL_DASH="http://localhost:${PORT}/dashboard.html"
URL_HELP="http://localhost:${PORT}/familien-helfer.html"

echo "==> Starte lokalen Server auf Port ${PORT} ..."
python3 -m http.server "$PORT" --bind 127.0.0.1 >/dev/null 2>&1 &
SRV=$!
trap 'echo; echo "==> Server wird beendet."; kill "$SRV" 2>/dev/null' EXIT INT TERM
sleep 1

# Browser öffnen (Linux: xdg-open, macOS: open)
opener=""
command -v xdg-open >/dev/null 2>&1 && opener="xdg-open"
[ -z "$opener" ] && command -v open >/dev/null 2>&1 && opener="open"
if [ -n "$opener" ]; then
  "$opener" "$URL_HELP"  >/dev/null 2>&1 || true
  sleep 1
  "$opener" "$URL_DASH"  >/dev/null 2>&1 || true
fi

echo
echo "   ✅ Läuft!"
echo "   👨‍👩‍👧‍👦 Familien-Helfer: ${URL_HELP}"
echo "   📚 Katalog-Dashboard: ${URL_DASH}"
echo
echo "   (Falls kein Browser aufging, Links oben manuell öffnen.)"
echo "   Zum Beenden: Strg+C"
echo
wait "$SRV"
