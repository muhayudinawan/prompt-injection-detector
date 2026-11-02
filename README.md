# prompt-injection-detector
A classifier that flags prompt injection and jailbreak attempts before they reach an LLM. Built to explore how public services can deploy AI chatbots safely.

The target setting is a chatbot for a Norwegian public service (benefits, tax, municipal services). Most code comments, notebooks and docs are in Norwegian.

## What counts as an attack

A message is an attack if it tries to make the chatbot break, bypass or replace its own instructions, or reveal what it has been told to keep hidden. This includes hidden instructions inside documents the user asks the chatbot to process. Harmful questions without any manipulation are *not* attacks for this filter. See [docs/retningslinjer.md](docs/retningslinjer.md) for the full labelling guidelines.

## Project layout

| Path | Contents |
|---|---|
| `src/data.py` | Loads six public datasets from Hugging Face into one format, removes duplicates, conflicting labels and train/test leakage |
| `src/evaluate.py` | Per-source evaluation and threshold selection, so every model is measured the same way |
| `notebooks/01_load_data.ipynb` | Builds `data/combined.parquet` |
| `notebooks/02_baseline.ipynb` | TF-IDF + logistic regression baseline |
| `notebooks/03_egne_testsett.ipynb` | Baseline on the custom Norwegian and English test sets |
| `notebooks/04_protectai.ipynb` | `protectai/deberta-v3-base-prompt-injection-v2` compared with the baseline |
| `testsets/` | Custom parallel test sets in Norwegian and English (`no.jsonl`, `en.jsonl`), the source files, a build script and a review tool |
| `docs/` | Labelling guidelines and notes on model choice |

## Data

Training data: `deepset/prompt-injections`, `jackhhao/jailbreak-classification`, `xTRam1/safe-guard-prompt-injection` and `reshabhs/SPML_Chatbot_Prompt_Injection`.

Test data from sources the model never trains on: `Lakera/gandalf_ignore_instructions`, the jailbreak part of `TrustAIRLab/in-the-wild-jailbreak-prompts`, and `databricks/databricks-dolly-15k` as ordinary questions. The "regular" part of TrustAIRLab is left out because many of its prompts are obvious jailbreaks.

**Custom test sets:** 596 messages each in Norwegian and English, written as parallel pairs, so differences between languages come from the language and not the content. They cover ordinary questions, harmless messages that look like attacks, documents with and without hidden instructions, and direct, role-play and obfuscated attacks. They are a first draft written with an LLM (Claude) and are being reviewed by a human. They are only used for testing, never training.

## Results so far

Baseline (TF-IDF + logistic regression), threshold set for at most 1 % false positives on validation data:

| Test set | Recall | False positive rate | ROC AUC |
|---|---|---|---|
| Public, sources seen in training | 0.93 | 0.8 % | 0.99 |
| Public, unseen sources | 0.85 | 0.3 % | 0.99 |
| Custom, English | 0.36 | 1.7 % | 0.83 |
| Custom, **Norwegian** | **0.05** | 0.3 % | 0.75 |

The public test sets make the baseline look excellent. The custom sets show the real gaps: it is almost blind to Norwegian attacks, and it misses obfuscated attacks and instructions hidden in documents in both languages.

`protectai/deberta-v3-base-prompt-injection-v2` on the custom test sets, with the same 1 % false positive target on validation data (threshold 0.994):

| Test set | Recall | False positive rate | ROC AUC |
|---|---|---|---|
| Custom, English | 0.61 | 3.7 % | 0.96 |
| Custom, Norwegian | 0.62 | **8.7 %** | 0.87 |

It catches far more Norwegian attacks than the baseline, but it also blocks many harmless Norwegian messages, especially those that only look like attacks (28 % of them). Instructions hidden in documents remain the weakest category for both models.

## Getting started

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; use source .venv/bin/activate elsewhere
pip install -r requirements.txt
```

Then run the notebooks in order. Notebook 04 also needs `torch` and `transformers`.

To rebuild the custom test sets after editing the source files (review results are kept):

```bash
python testsets/build.py
```

To review the test sets one message at a time:

```bash
python testsets/review.py
```
