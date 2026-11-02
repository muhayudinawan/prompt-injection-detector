"""Gjennomgang av de egne testsettene, én melding om gangen.

Kjør fra prosjektroten:
    python testsets/review.py              # norsk, i anbefalt rekkefølge
    python testsets/review.py --lang en    # engelsk
    python testsets/review.py --category vanskelig
    python testsets/review.py --alle       # vis også meldinger som er gjennomgått

Taster:
    g  godkjent: fasiten er riktig
    f  feil fasit: snur label (og label på tvillingen i det andre språket)
    m  skriv en merknad og marker som gjennomgått
    h  hopp over (vises igjen neste gang)
    b  tilbake til forrige melding
    q  avslutt

Alt lagres i jsonl-filen etter hver tast. Se docs/retningslinjer.md for hva fasiten betyr.
"""
import argparse
import json
import os
import sys
from pathlib import Path

HERE = Path(__file__).parent
ORDER = ["vanskelig", "dokument", "skjult", "direkte", "rollespill", "forkledd", "vanlig"]
LABEL_TEXT = {0: "VANLIG (0)", 1: "ANGREP (1)"}

try:
    import msvcrt

    def getkey():
        return msvcrt.getwch().lower()
except ImportError:
    import termios
    import tty

    def getkey():
        fd = sys.stdin.fileno()
        old = termios.tcgetattr(fd)
        try:
            tty.setraw(fd)
            return sys.stdin.read(1).lower()
        finally:
            termios.tcsetattr(fd, termios.TCSADRAIN, old)


def load(lang):
    path = HERE / f"{lang}.jsonl"
    return path, [json.loads(line) for line in path.read_text(encoding="utf-8").splitlines()]


def save(path, rows):
    tmp = path.with_suffix(".tmp")
    tmp.write_text("".join(json.dumps(r, ensure_ascii=False) + "\n" for r in rows), encoding="utf-8")
    os.replace(tmp, path)


def add_note(row, note):
    row["merknad"] = f"{row['merknad']} | {note}" if row["merknad"] else note


def flip_twin(lang, pair_id):
    other = "en" if lang == "no" else "no"
    path, rows = load(other)
    for row in rows:
        if row["pair_id"] == pair_id:
            row["label"] = 1 - row["label"]
            add_note(row, f"fasit snudd via {lang}-tvillingen, bør sjekkes")
    save(path, rows)


def show(row, pos, total, reviewed, n_rows):
    os.system("cls" if os.name == "nt" else "clear")
    print(f"[{pos + 1}/{total} i køen]   gjennomgått totalt: {reviewed}/{n_rows}")
    print(f"{row['id']}   kategori: {row['category']}")
    print(f"Fasit: {LABEL_TEXT[row['label']]}")
    if row["merknad"]:
        print(f"Merknad: {row['merknad']}")
    print("-" * 70)
    print(row["text"])
    print("-" * 70)
    print("g=godkjent  f=feil fasit  m=merknad  h=hopp over  b=tilbake  q=avslutt")


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    p = argparse.ArgumentParser(description="Gå gjennom testsettene.")
    p.add_argument("--lang", default="no", choices=["no", "en"])
    p.add_argument("--category", choices=ORDER)
    p.add_argument("--alle", action="store_true", help="vis også gjennomgåtte meldinger")
    args = p.parse_args()

    path, rows = load(args.lang)
    queue = [
        r for r in sorted(rows, key=lambda r: (ORDER.index(r["category"]), r["id"]))
        if (args.alle or not r["gjennomgatt"])
        and (args.category is None or r["category"] == args.category)
    ]
    if not queue:
        print("Ingenting å gå gjennom her.")
        return

    pos = 0
    while pos < len(queue):
        row = queue[pos]
        show(row, pos, len(queue), sum(r["gjennomgatt"] for r in rows), len(rows))
        key = getkey()
        if key == "q":
            break
        if key == "b":
            pos = max(0, pos - 1)
            continue
        if key == "h":
            pos += 1
            continue
        if key == "g":
            row["gjennomgatt"] = True
        elif key == "f":
            row["label"] = 1 - row["label"]
            row["gjennomgatt"] = True
            add_note(row, "fasit snudd ved gjennomgang")
            flip_twin(args.lang, row["pair_id"])
        elif key == "m":
            note = input("\nMerknad: ").strip()
            if not note:
                continue
            add_note(row, note)
            row["gjennomgatt"] = True
        else:
            continue
        save(path, rows)
        pos += 1

    done = sum(r["gjennomgatt"] for r in rows)
    print(f"\nLagret. {done} av {len(rows)} meldinger i {path.name} er gjennomgått.")


if __name__ == "__main__":
    main()
