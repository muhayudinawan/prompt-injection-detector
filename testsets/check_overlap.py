"""Sjekker at nye norske treningsdata ikke ligner for mye på test- og kalibreringssettene.

Hvert avsnitt, hver instruks og hver melding i treningsfilene sammenlignes med alle
avsnitt i testsettene og kalibreringssettet (cosinuslikhet på bokstav-n-gram).
Treff over terskelen skrives ut og bør skrives om eller fjernes før trening.

    python testsets/check_overlap.py
"""
import sys
from pathlib import Path

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer

ROOT = Path(__file__).resolve().parent
THRESHOLD = 0.8


def paragraphs(texts):
    return [p.strip() for t in texts for p in t.split("\n\n") if len(p.strip()) >= 20]


def training_pieces():
    pieces = []
    for name in ("treningsdata_triggerord_no.jsonl",):
        path = ROOT / name
        if path.exists():
            pieces += [(name, t) for t in pd.read_json(path, lines=True)["text"]]
    path = ROOT / "treningsdata_dokumenter_no.jsonl"
    if path.exists():
        for doc in pd.read_json(path, lines=True).itertuples():
            pieces += [(path.name, p) for p in [doc.foresporsel, *doc.avsnitt, doc.instruks]]
    return pd.DataFrame(pieces, columns=["fil", "tekst"])


def main():
    train = training_pieces()
    if train.empty:
        sys.exit("Fant ingen nye treningsfiler.")
    held_out = paragraphs(pd.concat(
        pd.read_json(ROOT / f, lines=True)["text"] for f in ("no.jsonl", "en.jsonl", "kalibrering_no.jsonl")
    ))
    vec = TfidfVectorizer(analyzer="char_wb", ngram_range=(3, 5)).fit(held_out + train["tekst"].tolist())
    sim = (vec.transform(train["tekst"]) @ vec.transform(held_out).T).toarray()
    train["likhet"] = sim.max(axis=1)
    train["ligner"] = [held_out[i] for i in sim.argmax(axis=1)]

    hits = train[train["likhet"] >= THRESHOLD].sort_values("likhet", ascending=False)
    print(f"{len(train)} biter sjekket, {len(hits)} over {THRESHOLD}.")
    with pd.option_context("display.max_colwidth", 120, "display.width", 250):
        if len(hits):
            print(hits[["fil", "likhet", "tekst", "ligner"]].to_string())


if __name__ == "__main__":
    main()
