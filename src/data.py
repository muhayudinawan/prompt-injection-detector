"""Laster offentlige datasett for prompt injection og jailbreak til ett felles format.

Alle loadere returnerer en DataFrame med kolonnene:
    text   - prompten
    label  - 0 = benign, 1 = injection/jailbreak
    source - kortnavn på datasettet
    split  - "train" eller "test"

Kildene i TEST_ONLY_SOURCES brukes aldri til trening. De måler hvor godt
modellen generaliserer til data fra kilder den ikke har sett.
"""
from pathlib import Path

import pandas as pd
from datasets import load_dataset

COLUMNS = ["text", "label", "source", "split"]
TEST_ONLY_SOURCES = {"lakera_gandalf", "trustairlab", "dolly"}


def _frame(ds, text_col, labels, source, split):
    df = ds.to_pandas()
    out = pd.DataFrame({
        "text": df[text_col].astype(str),
        "label": labels(df).astype(int),
    })
    out["source"] = source
    out["split"] = split
    return out


def load_deepset():
    ds = load_dataset("deepset/prompt-injections")
    return pd.concat(
        _frame(ds[s], "text", lambda d: d["label"], "deepset", s)
        for s in ("train", "test")
    )


def load_jackhhao():
    ds = load_dataset("jackhhao/jailbreak-classification")
    return pd.concat(
        _frame(ds[s], "prompt", lambda d: d["type"] == "jailbreak", "jackhhao", s)
        for s in ("train", "test")
    )


def load_safeguard():
    ds = load_dataset("xTRam1/safe-guard-prompt-injection")
    return pd.concat(
        _frame(ds[s], "text", lambda d: d["label"], "safeguard", s)
        for s in ("train", "test")
    )


def load_spml():
    # Har ingen egen testsplitt, så alt brukes til trening.
    ds = load_dataset("reshabhs/SPML_Chatbot_Prompt_Injection", split="train")
    return _frame(ds, "User Prompt", lambda d: d["Prompt injection"], "spml", "train")


def load_lakera_gandalf():
    # Inneholder bare angrep.
    ds = load_dataset("Lakera/gandalf_ignore_instructions")
    return pd.concat(
        _frame(ds[s], "text", lambda d: pd.Series(1, index=d.index), "lakera_gandalf", "test")
        for s in ds
    )


def load_trustairlab():
    # Bare jailbreak-delen. "regular"-delen er utelatt fordi mange av promptene
    # der er tydelige jailbreaks, så fasiten er ikke til å stole på.
    ds = load_dataset("TrustAIRLab/in-the-wild-jailbreak-prompts", "jailbreak_2023_12_25", split="train")
    return _frame(ds, "prompt", lambda d: d["jailbreak"], "trustairlab", "test")


def load_dolly():
    # Vanlige spørsmål og oppgaver skrevet av mennesker. Erstatter trustairlab
    # "regular" som kilde til benigne meldinger fra en ukjent kilde.
    ds = load_dataset("databricks/databricks-dolly-15k", split="train")
    return _frame(ds, "instruction", lambda d: pd.Series(0, index=d.index), "dolly", "test")


LOADERS = [
    load_deepset,
    load_jackhhao,
    load_safeguard,
    load_spml,
    load_lakera_gandalf,
    load_trustairlab,
    load_dolly,
]


def _normalize(text):
    return " ".join(text.lower().split())


def clean(df):
    """Fjerner tomme tekster, motstridende labels, duplikater og lekkasje fra test til train."""
    df = df.copy()
    df["text"] = df["text"].str.strip()
    df = df[df["text"].str.len() > 0]
    df["_key"] = df["text"].map(_normalize)

    # Samme tekst med ulike labels (ofte på tvers av kilder) kan ikke læres riktig.
    n_labels = df.groupby("_key")["label"].nunique()
    df = df[~df["_key"].isin(n_labels[n_labels > 1].index)]

    df = df.drop_duplicates(["_key", "split"])

    # En tekst som finnes i et testsett skal ikke være med i treningen.
    test_keys = set(df.loc[df["split"] == "test", "_key"])
    df = df[~((df["split"] == "train") & df["_key"].isin(test_keys))]

    return df.drop(columns="_key").reset_index(drop=True)


def load_all():
    raw = pd.concat([load() for load in LOADERS], ignore_index=True)[COLUMNS]
    return raw, clean(raw)


def load_own_testsets(root):
    """De egne testsettene (testsets/no.jsonl og en.jsonl). Bare til test, aldri trening."""
    return pd.concat(
        pd.read_json(Path(root) / "testsets" / f"{lang}.jsonl", lines=True)
        for lang in ("no", "en")
    ).reset_index(drop=True)
