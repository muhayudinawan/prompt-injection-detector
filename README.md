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

Training data: `deepset/prompt-injections`, `jackhhao/jailbreak-classification`, `xTRam1/safe-guard-prompt-injection`, and emails: 4,000 human-written indirect attacks from `microsoft/llmail-inject-challenge` (Phase1) balanced by 4,000 ordinary Enron emails from `Yale-LILY/aeslc`.

The email attacks are sampled so their lengths match the ordinary emails, and their target (`contact@contact.com` and the word "confirmation") is masked, so the model cannot recognise them by length or by one address. Without the ordinary emails the model learned that "document = attack" and blocked 59 % of harmless Norwegian documents in the custom test set. The license of `Yale-LILY/aeslc` is listed as unknown; the underlying Enron corpus was made public by the US Federal Energy Regulatory Commission.

`reshabhs/SPML_Chatbot_Prompt_Injection` was used at first but has been removed. Its authors advise against training detection models on it, and it made up two thirds of the training data. Without it the baseline improved clearly on the custom test sets: ROC AUC went from 0.75 to 0.81 in Norwegian and from 0.83 to 0.91 in English.

Test data from sources the model never trains on: `Lakera/gandalf_ignore_instructions`, the jailbreak part of `TrustAIRLab/in-the-wild-jailbreak-prompts`, `databricks/databricks-dolly-15k` as ordinary questions, and `leolee99/NotInject` (harmless messages containing trigger words such as "ignore"). The "regular" part of TrustAIRLab is left out because many of its prompts are obvious jailbreaks. About 9 % of the TrustAIRLab test prompts have near-duplicates in `jackhhao`, since both come from the same source, so TrustAIRLab is not fully unseen. 1,000 attacks from LLMail-Inject Phase2 are also kept for testing.

**Custom test sets:** 596 messages each in Norwegian and English, written as parallel pairs, so differences between languages come from the language and not the content. They cover ordinary questions, harmless messages that look like attacks, documents with and without hidden instructions, and direct, role-play and obfuscated attacks. They were written with an LLM (Claude) and reviewed by a human: all borderline categories in Norwegian in full, plus samples from the rest and from English, 393 messages in total. No label had to be changed. They are only used for testing, never training.

## Results so far

Baseline (TF-IDF + logistic regression), threshold set for at most 1 % false positives on validation data:

| Test set | Recall | False positive rate | ROC AUC |
|---|---|---|---|
| Public, sources seen in training | 0.97 | 0.6 % | 1.00 |
| Public, unseen sources | 0.88 | 2.5 % | 0.98 |
| NotInject (harmless, with trigger words) | – | **34 %** | – |
| Custom, English | 0.70 | 6.2 % | 0.92 |
| Custom, **Norwegian** | 0.69 | **12.7 %** | 0.87 |

The public test sets make the baseline look excellent. The custom sets and NotInject show the real gaps: it blocks far too many harmless messages that only look like attacks (32 % of them in Norwegian, 34 % of NotInject), and harmless Norwegian documents are often flagged.

The threshold is chosen for 1 % false positives on validation data from the training sources. Those are easier than the custom test sets, so the false positive rate there ends up much higher than 1 %. ROC AUC, which does not depend on the threshold, is the more reliable comparison. A separate Norwegian calibration set would give a better threshold.

`protectai/deberta-v3-base-prompt-injection-v2` on the custom test sets, at its default threshold of 0.5:

| Test set | Recall | False positive rate | ROC AUC |
|---|---|---|---|
| Custom, English | 0.71 | 4.8 % | 0.96 |
| Custom, Norwegian | 0.74 | **13.2 %** | 0.87 |

With the email data in training, the baseline has caught up in Norwegian (ROC AUC 0.87 for both) but not in English (0.92 against 0.96). ProtectAI catches almost all obfuscated attacks, while the baseline is much better at instructions hidden in emails and documents (99 % against 29 % on LLMail-Inject Phase2). Both block many harmless messages that only look like attacks: 43 % of NotInject for ProtectAI.

ProtectAI cannot be calibrated fairly on our validation data, because that data comes from our training sources and ProtectAI was partly trained on the same sources (including jackhhao). ROC AUC is therefore the main comparison.

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
