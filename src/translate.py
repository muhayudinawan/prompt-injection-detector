"""Maskinoversetter et balansert utvalg av treningsdataene til norsk (bokmål).

Det finnes ingen åpne norske angrepsdata. Uten norske angrep i treningen lærer modellen
at «norsk = vanlig» så snart vi legger inn norske vanlige meldinger. Derfor oversettes
like mange angrep som vanlige meldinger, med samme fasit som originalen.

Kjør fra prosjektroten etter notebook 01:
    python src/translate.py

Resultatet lagres i data/translated_no.parquet. Modellen er
Helsinki-NLP/opus-mt-tc-big-en-gmq (CC-BY-4.0). Bruker GPU hvis den finnes
(ca. 5 minutter), ellers CPU (ca. 1 time).
"""
import re
import sys
import time
from pathlib import Path

import pandas as pd
import torch
from transformers import MarianMTModel, MarianTokenizer

ROOT = Path(__file__).resolve().parent.parent
MODEL = "Helsinki-NLP/opus-mt-tc-big-en-gmq"
N_PER_CLASS = 1200
MAX_CHARS = 1500


def sample(df, n_per_class, seed=0):
    """Like mange angrep og vanlige, fordelt på kildene i samme forhold som i treningen."""
    train = df[(df["split"] == "train") & (df["text"].str.len() <= MAX_CHARS)]
    parts = []
    for label in (0, 1):
        g = train[train["label"] == label]
        for source, s in g.groupby("source"):
            parts.append(s.sample(round(n_per_class * len(s) / len(g)), random_state=seed))
    return pd.concat(parts)


def chunks(text):
    """Deler opp i avsnitt, så lange tekster ikke kuttes av modellens lengdegrense."""
    return [p.strip() for p in re.split(r"\n\s*\n|\n", text) if p.strip()]


DEVICE = "cuda" if torch.cuda.is_available() else "cpu"


@torch.inference_mode()
def translate(texts, tok, mt, batch_size=16):
    parts = [(i, c) for i, t in enumerate(texts) for c in chunks(t)]
    order = sorted(range(len(parts)), key=lambda k: len(parts[k][1]))
    out = [None] * len(parts)
    start = time.time()
    for b in range(0, len(order), batch_size):
        idx = order[b:b + batch_size]
        enc = tok([">>nob<< " + parts[k][1] for k in idx], return_tensors="pt",
                  padding=True, truncation=True, max_length=512).to(DEVICE)
        dec = tok.batch_decode(mt.generate(**enc, num_beams=1, max_new_tokens=512), skip_special_tokens=True)
        for k, d in zip(idx, dec):
            out[k] = d
        if (b // batch_size) % 20 == 0:
            print(f"  {b + len(idx):,} / {len(order):,} avsnitt ({time.time() - start:.0f} s)", flush=True)
    joined = [[] for _ in texts]
    for (i, _), d in zip(parts, out):
        joined[i].append(d)
    return ["\n\n".join(p) for p in joined]


def main():
    df = pd.read_parquet(ROOT / "data" / "combined.parquet")
    s = sample(df, N_PER_CLASS)
    print(f"Oversetter {len(s):,} tekster ({s['label'].sum():,} angrep)")
    print(s.groupby(["source", "label"]).size().to_string())
    tok = MarianTokenizer.from_pretrained(MODEL)
    mt = MarianMTModel.from_pretrained(MODEL).eval().to(DEVICE)
    out = pd.DataFrame({
        "text": translate(s["text"].tolist(), tok, mt),
        "label": s["label"].to_numpy(),
        "source": s["source"].to_numpy() + "_no",
        "split": "train",
        "original": s["text"].to_numpy(),
    })
    path = ROOT / "data" / "translated_no.parquet"
    out.to_parquet(path, index=False)
    print(f"Lagret {len(out):,} rader til {path.relative_to(ROOT)}")


if __name__ == "__main__":
    sys.stdout.reconfigure(encoding="utf-8")
    main()
