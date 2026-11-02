# prompt-injection-detector
A classifier that flags prompt injection and jailbreak attempts before they reach an LLM. Built to explore how public services can deploy AI chatbots safely.

The target setting is a chatbot for a Norwegian public service (benefits, tax, municipal services). Most code comments, notebooks and docs are in Norwegian.

## What counts as an attack

A message is an attack if it tries to make the chatbot break, bypass or replace its own instructions, or reveal what it has been told to keep hidden. This includes hidden instructions inside documents the user asks the chatbot to process. Harmful questions without any manipulation are *not* attacks for this filter. See [docs/retningslinjer.md](docs/retningslinjer.md) for the full labelling guidelines.

## Project layout

| Path | Contents |
|---|---|
| `src/data.py` | Loads six public datasets from Hugging Face into one format, removes duplicates, conflicting labels and train/test leakage |
| `src/translate.py` | Machine-translates a balanced sample of the training data to Norwegian |
| `src/evaluate.py` | Per-source evaluation and threshold selection, so every model is measured the same way |
| `notebooks/01_load_data.ipynb` | Builds `data/combined.parquet` |
| `notebooks/02_baseline.ipynb` | TF-IDF + logistic regression baseline |
| `notebooks/03_egne_testsett.ipynb` | Baseline on the custom Norwegian and English test sets |
| `notebooks/04_protectai.ipynb` | `protectai/deberta-v3-base-prompt-injection-v2` compared with the baseline |
| `notebooks/05_mdeberta_colab.ipynb` | Fine-tunes `microsoft/mdeberta-v3-base` in Google Colab (GPU) |
| `testsets/` | Custom parallel test sets in Norwegian and English (`no.jsonl`, `en.jsonl`), the source files, a build script and a review tool |
| `docs/` | Labelling guidelines and notes on model choice |

## Data

Training data: `deepset/prompt-injections`, `jackhhao/jailbreak-classification`, `xTRam1/safe-guard-prompt-injection`, and emails: 4,000 human-written indirect attacks from `microsoft/llmail-inject-challenge` (Phase1) balanced by 4,000 ordinary Enron emails from `Yale-LILY/aeslc`.

Two more sources were added after measuring their effect on the custom test sets:

- 277 real English first messages from `OpenAssistant/oasst2` that contain trigger words such as "ignore" or "act as", as harmless examples that look like attacks.
- **Machine-translated Norwegian training data:** a balanced sample of 2,401 training texts (about half attacks, half harmless) translated to Norwegian Bokmål with `Helsinki-NLP/opus-mt-tc-big-en-gmq` by `src/translate.py`. This raised Norwegian ROC AUC from 0.87 to 0.90 without hurting English. Translating both classes matters: adding Norwegian harmless messages alone made the model learn that "Norwegian = harmless" and it caught only 12 % of Norwegian attacks.
- **Norwegian training data written directly in Norwegian** (`testsets/treningsdata_no.jsonl`): 598 messages written with ChatGPT, 300 attacks and 298 harmless, many of them harmless messages that look like attacks. This raised Norwegian ROC AUC from 0.89 to 0.95, the largest single improvement so far, without changing English.

**Calibration set** (`testsets/kalibrering_no.jsonl`): 398 Norwegian messages (120 attacks) written with ChatGPT in a separate session, used only to choose the threshold. Less than 1 % of them have a near-duplicate in the training data or the test sets.

The email attacks are sampled so their lengths match the ordinary emails, and their target (`contact@contact.com` and the word "confirmation") is masked, so the model cannot recognise them by length or by one address. Without the ordinary emails the model learned that "document = attack" and blocked 59 % of harmless Norwegian documents in the custom test set. The license of `Yale-LILY/aeslc` is listed as unknown; the underlying Enron corpus was made public by the US Federal Energy Regulatory Commission.

`reshabhs/SPML_Chatbot_Prompt_Injection` was used at first but has been removed. Its authors advise against training detection models on it, and it made up two thirds of the training data. Without it the baseline improved clearly on the custom test sets: ROC AUC went from 0.75 to 0.81 in Norwegian and from 0.83 to 0.91 in English.

Test data from sources the model never trains on: `Lakera/gandalf_ignore_instructions`, the jailbreak part of `TrustAIRLab/in-the-wild-jailbreak-prompts`, `databricks/databricks-dolly-15k` as ordinary questions, and `leolee99/NotInject` (harmless messages containing trigger words such as "ignore"). The "regular" part of TrustAIRLab is left out because many of its prompts are obvious jailbreaks. About 9 % of the TrustAIRLab test prompts have near-duplicates in `jackhhao`, since both come from the same source, so TrustAIRLab is not fully unseen. 1,000 attacks from LLMail-Inject Phase2 are also kept for testing.

**Custom test sets:** 596 messages each in Norwegian and English, written as parallel pairs, so differences between languages come from the language and not the content. They cover ordinary questions, harmless messages that look like attacks, documents with and without hidden instructions, and direct, role-play and obfuscated attacks. They were written with an LLM (Claude) and reviewed by a human: all borderline categories in Norwegian in full, plus samples from the rest and from English, 393 messages in total. A second review of all Norwegian messages by another LLM (ChatGPT) then found 9 messages that were wrongly labelled as attacks (harmful or inappropriate requests without manipulation) and 3 flawed texts. These are corrected, with reasons, in `testsets/kilder/overstyringer.txt`. Each set now has 232 attacks and 364 harmless messages. The sets are only used for testing, never training.

## Results so far

The threshold is chosen so that at most 2 % of the harmless messages in the Norwegian calibration set are blocked. For a public service, blocking ordinary citizens is the worst error, so this is a strict setting. (Earlier the threshold was chosen on validation data from the training sources, which are much easier than real Norwegian messages, so far too many harmless messages were blocked.)

Baseline (TF-IDF + logistic regression):

| Test set | Recall | False positive rate | ROC AUC |
|---|---|---|---|
| Public, sources seen in training | 0.89 | 0.0 % | 1.00 |
| Public, unseen sources | 0.64 | 0.3 % | 0.98 |
| NotInject (harmless, with trigger words) | – | 9.7 % | – |
| Custom, English | 0.37 | 1.4 % | 0.92 |
| Custom, **Norwegian** | 0.54 | 1.6 % | **0.95** |

At this strict threshold the baseline rarely blocks ordinary messages (1.6 % in Norwegian, 5 % of the harmless messages that look like attacks), but it catches only about half of the Norwegian attacks and very few instructions hidden in documents. A looser threshold catches more attacks at the cost of more false alarms; ROC AUC, which does not depend on the threshold, shows how well the model separates the two classes overall.

`protectai/deberta-v3-base-prompt-injection-v2` on the custom test sets, at its default threshold of 0.5:

| Test set | Recall | False positive rate | ROC AUC |
|---|---|---|---|
| Custom, English | 0.73 | 4.9 % | 0.96 |
| Custom, Norwegian | 0.74 | **14.6 %** | 0.86 |

With Norwegian training data, the baseline now clearly beats ProtectAI in Norwegian (ROC AUC 0.95 against 0.86) but not in English (0.92 against 0.96). ProtectAI catches almost all obfuscated attacks, while the baseline is much better at instructions hidden in emails (91 % against 29 % on LLMail-Inject Phase2).

**ProtectAI cannot be used with a strict threshold in Norwegian.** It gives scores close to 1.0 to many harmless Norwegian messages, so keeping false positives at 2 % on the calibration set pushes its threshold to about 1.0. It then catches only 4 % of the Norwegian attacks. An English-only filter is not a safe choice for a Norwegian public service.

Next step: fine-tuning the multilingual `microsoft/mdeberta-v3-base` on the same data. `notebooks/05_mdeberta_colab.ipynb` does this on a free Colab GPU and compares it with the baseline trained on exactly the same data.

## Getting started

```bash
python -m venv .venv
.venv/Scripts/activate        # Windows; use source .venv/bin/activate elsewhere
pip install -r requirements.txt
```

Then run `notebooks/01_load_data.ipynb`, translate the Norwegian training data once (about an hour on CPU), and run the remaining notebooks in order:

```bash
python src/translate.py
```

The translation and notebook 04 need `torch`, `transformers` and `sentencepiece`.

To rebuild the custom test sets after editing the source files (review results are kept):

```bash
python testsets/build.py
```

To review the test sets one message at a time:

```bash
python testsets/review.py
```
