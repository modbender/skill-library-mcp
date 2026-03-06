#!/bin/bash
set -e

FLAG="${1:---status}"

case "$FLAG" in
  --aktiva)
    echo "=== Aktiva (Vermoegenswerte) ==="
    echo "A. Anlagevermoegen"
    echo "   I.  Immaterielle Vermoegensgegenstaende ... 0,00"
    echo "   II. Sachanlagen ........................... 0,00"
    echo "   III.Finanzanlagen ......................... 0,00"
    echo "B. Umlaufvermoegen"
    echo "   I.  Vorraete .............................. 0,00"
    echo "   II. Forderungen ........................... 0,00"
    echo "   III.Kassenbestand, Bankguthaben ........... 0,00"
    echo "Summe Aktiva ................................. 0,00"
    ;;
  --passiva)
    echo "=== Passiva (Kapital + Schulden) ==="
    echo "A. Eigenkapital"
    echo "   I.  Stammkapital .......................... 0,00"
    echo "   II. Gewinnruecklagen ...................... 0,00"
    echo "B. Rueckstellungen ........................... 0,00"
    echo "C. Verbindlichkeiten"
    echo "   I.  Verbindlichkeiten gg. Kreditinstituten  0,00"
    echo "   II. Lieferantenverbindlichkeiten .......... 0,00"
    echo "Summe Passiva ................................ 0,00"
    ;;
  --status)
    echo "Bilanz Skill v0.1.0"
    echo "Copyright (c) 2026 Netsnek e.U."
    echo "Austrian UGB annual accounts generator."
    echo "Website: https://netsnek.com"
    ;;
  *)
    echo "Unknown flag: $FLAG"
    echo "Usage: bilanz-check.sh [--aktiva|--passiva|--status]"
    exit 1
    ;;
esac