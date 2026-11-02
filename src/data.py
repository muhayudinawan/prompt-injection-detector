"""Laster offentlige datasett for prompt injection og jailbreak til ett felles format.

Alle loadere returnerer en DataFrame med kolonnene:
    text   - prompten
    label  - 0 = benign, 1 = injection/jailbreak
    source - kortnavn på datasettet
    split  - "train" eller "test"

Kildene i TEST_ONLY_SOURCES brukes aldri til trening. De måler hvor godt
modellen generaliserer til data fra kilder den ikke har sett.
"""
import random
import re
from pathlib import Path

import pandas as pd
from datasets import load_dataset

COLUMNS = ["text", "label", "source", "split"]
TEST_ONLY_SOURCES = {"lakera_gandalf", "trustairlab", "dolly", "notinject"}


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


def load_notinject():
    # Vanlige meldinger med triggerord som «ignore». Måler falske positive.
    ds = load_dataset("leolee99/NotInject")
    return pd.concat(
        _frame(ds[s], "prompt", lambda d: pd.Series(0, index=d.index), "notinject", "test")
        for s in ds
    )


# Målet i LLMail-Inject var nesten alltid å sende «confirmation» til contact@contact.com.
# Uten maskering lærer modellen den adressen i stedet for selve manipulasjonen.
_ADDRESSES = [
    "anna.berg@firma.example", "it-support@example.com", "post@kommune.example",
    "j.smith@mailbox.example", "faktura@leverandor.example", "admin@internal.example",
]
_WORDS = ["approved", "done", "received", "OK", "status update", "payment details"]


def _mask_llmail(text, rng):
    text = re.sub(r"contact\s*@\s*contact\s*\.\s*com", lambda _: rng.choice(_ADDRESSES), text, flags=re.I)
    return re.sub(r"\bconfirmation\b", lambda _: rng.choice(_WORDS), text, flags=re.I)


def _email(subject, body):
    return f"Subject: {subject}\n\n{body}".strip()


def _llmail_texts(phase):
    ds = load_dataset("microsoft/llmail-inject-challenge", split=phase)
    df = ds.select_columns(["subject", "body"]).to_pandas().fillna("")
    return pd.Series([_email(s, b) for s, b in zip(df["subject"], df["body"])]).drop_duplicates()


def _sample_like(pool, target_lengths, seed, bins=10):
    """Trekker fra pool slik at lengdefordelingen ligner target_lengths."""
    edges = target_lengths.quantile([i / bins for i in range(bins + 1)]).to_numpy().copy()
    edges[0], edges[-1] = 0, float("inf")
    per_bin = len(target_lengths) // bins
    which = pd.cut(pool.str.len(), edges, labels=False, include_lowest=True)
    return pd.concat(pool[which == b].sample(per_bin, random_state=seed) for b in range(bins))


# Vanskelige vanlige meldinger: ekte eller oversatte instruksjoner som tilfeldigvis
# inneholder ord som ofte brukes i angrep. Hentes fra uavhengige kilder, ikke skrevet
# av oss, så de ikke ligner de egne testsettene.
_TRIGGERS_EN = re.compile(
    r"\b(?:ignor\w*|forget|disregard|pretend|act as|role[- ]?play|instructions?|rules?|system"
    r"|prompt|override|bypass|hack\w*|admin\w*|developer|password|secret|reveal"
    r"|unrestricted|uncensored|unfiltered)\b", re.I)
_TRIGGERS_NO = re.compile(
    r"\b(?:ignor\w*|glem\w*|se bort fra|late som|lat som|instruks\w*|regel|regler\w*|system\w*"
    r"|prompt\w*|overstyr\w*|omgå\w*|hack\w*|admin\w*|utvikler\w*|passord\w*|hemmelig\w*"
    r"|avslør\w*|rolle\w*)\b", re.I)
_ATTACK_MARKERS = re.compile(
    r"\bDAN\b|jailbreak|ignore (?:all |any )?(?:previous|prior|above|your)|no (?:restrictions|rules|filters)"
    r"|developer mode|disregard (?:all|your|previous)|you are (?:now )?free|unfiltered|uncensored", re.I)


def load_hard_negatives_en():
    """Engelske førstemeldinger fra OpenAssistant (Apache-2.0) med triggerord."""
    o = load_dataset("OpenAssistant/oasst2", split="train").to_pandas()
    p = o[(o["role"] == "prompter") & (o["lang"] == "en") & o["parent_id"].isna()]["text"].drop_duplicates()
    p = p[p.str.contains(_TRIGGERS_EN) & ~p.str.contains(_ATTACK_MARKERS)]
    return pd.DataFrame({"text": p.tolist(), "label": 0, "source": "oasst2", "split": "train"})


def load_hard_negatives_no():
    """Norske instruksjoner med triggerord fra NbAiLab/norwegian-alpaca (CC-BY-4.0, maskinoversatt)."""
    n = load_dataset("NbAiLab/norwegian-alpaca", split="train").to_pandas()
    text = (n["instruction"].fillna("") + "\n\n" + n["input"].fillna("")).str.strip().drop_duplicates()
    text = text[text.str.contains(_TRIGGERS_NO) & ~text.str.contains(_ATTACK_MARKERS)]
    return pd.DataFrame({"text": text.tolist(), "label": 0, "source": "norwegian_alpaca", "split": "train"})


def load_translated_no(root="."):
    """Maskinoversatte treningsdata (angrep og vanlige) laget av src/translate.py."""
    path = Path(root) / "data" / "translated_no.parquet"
    return pd.read_parquet(path)[COLUMNS]


def load_emails(n=4000, n_test=1000, seed=0):
    """Skjulte instrukser i e-post (LLMail-Inject) og vanlige e-poster (Enron/AESLC) som motvekt.

    Uten vanlige e-poster lærer modellen at «e-post = angrep». LLMail-angrepene trekkes
    slik at lengdene ligner de vanlige e-postene, så lengde ikke avslører fasiten.
    Phase1 brukes til trening og Phase2 til test.
    AESLC-lisensen er oppgitt som ukjent. Enron-korpuset ble offentliggjort av FERC.
    """
    rng = random.Random(seed)
    aeslc = load_dataset("Yale-LILY/aeslc", split="train").to_pandas().drop_duplicates("email_body")
    aeslc = aeslc.sample(n, random_state=seed)
    benign = pd.Series([_email(s, b) for s, b in zip(aeslc["subject_line"], aeslc["email_body"])])

    train_attacks = _sample_like(_llmail_texts("Phase1"), benign.str.len(), seed)
    test_attacks = _llmail_texts("Phase2").sample(n_test, random_state=seed)

    def frame(texts, label, source, split):
        return pd.DataFrame({"text": list(texts), "label": label, "source": source, "split": split})

    return pd.concat([
        frame(benign, 0, "aeslc", "train"),
        frame((_mask_llmail(t, rng) for t in train_attacks), 1, "llmail", "train"),
        frame((_mask_llmail(t, rng) for t in test_attacks), 1, "llmail_phase2", "test"),
    ])


# load_spml er ikke med: forfatterne fraråder å trene deteksjonsmodeller på SPML,
# og baselinen ble klart bedre på de egne testsettene uten (se README).
LOADERS = [
    load_deepset,
    load_jackhhao,
    load_safeguard,
    load_lakera_gandalf,
    load_trustairlab,
    load_dolly,
    load_notinject,
    load_emails,
    load_hard_negatives_en,
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


def load_training_data(root):
    """data/combined.parquet pluss de oversatte norske treningsdataene, hvis de finnes.

    Oversettelsen lages av src/translate.py etter notebook 01. Uten den mangler
    treningen norske eksempler, og modellen blir klart dårligere på norsk.
    """
    df = pd.read_parquet(Path(root) / "data" / "combined.parquet")
    if not (Path(root) / "data" / "translated_no.parquet").exists():
        print("Advarsel: data/translated_no.parquet mangler. Kjør src/translate.py for norske treningsdata.")
        return df
    return clean(pd.concat([df, load_translated_no(root)], ignore_index=True))


def load_own_testsets(root):
    """De egne testsettene (testsets/no.jsonl og en.jsonl). Bare til test, aldri trening."""
    return pd.concat(
        pd.read_json(Path(root) / "testsets" / f"{lang}.jsonl", lines=True)
        for lang in ("no", "en")
    ).reset_index(drop=True)
