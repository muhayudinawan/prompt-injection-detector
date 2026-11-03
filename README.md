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
| `notebooks/06_sammenligning.ipynb` | Baseline, ProtectAI and mDeBERTa compared on all test sets, with error analysis |
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

Three models are compared, all with the threshold chosen this way (`notebooks/06_sammenligning.ipynb`):

- **Baseline:** TF-IDF + logistic regression.
- **ProtectAI:** `protectai/deberta-v3-base-prompt-injection-v2`, used as is. It is English-only.
- **mDeBERTa:** the multilingual `microsoft/mdeberta-v3-base`, fine-tuned on the same training data as the baseline.

Custom test sets:

| Model | Recall, Norwegian | False positive rate, Norwegian | ROC AUC, Norwegian | Recall, English | False positive rate, English | ROC AUC, English |
|---|---|---|---|---|---|---|
| Baseline | 0.54 | 1.6 % | 0.95 | 0.37 | 1.4 % | 0.92 |
| ProtectAI | 0.04 | 0.5 % | 0.86 | 0.17 | 0.0 % | 0.96 |
| mDeBERTa | **0.73** | 3.0 % | 0.95 | **0.70** | 2.5 % | 0.95 |

Public test sets:

| Model | Recall, sources seen in training | Recall, unseen sources | False positive rate, unseen sources | False positive rate, NotInject | Recall, LLMail-Inject Phase2 |
|---|---|---|---|---|---|
| Baseline | 0.89 | 0.64 | 0.3 % | 9.7 % | 0.91 |
| ProtectAI | 0.08 | 0.36 | 0.0 % | 1.2 % | 0.01 |
| mDeBERTa | **0.96** | **0.89** | 0.8 % | **28.9 %** | **0.98** |

**mDeBERTa is the best model in Norwegian.** It catches 73 % of the Norwegian attacks against 54 % for the baseline, but blocks slightly more ordinary messages (3.0 % against 1.6 %). With exactly 2 % false positives on the test set itself, so the comparison is fully equal, it catches 72 % of the Norwegian attacks, against 56 % for the baseline and 26 % for ProtectAI. ROC AUC is almost the same as for the baseline (0.95), but mDeBERTa is much better at the strict end of the curve, which is what matters for a public service. It is also clearly best on public sources it has never seen, and it does as well in Norwegian as in English.

Weaknesses of mDeBERTa, from the error analysis:

- **Instructions hidden in documents almost always get through** (14 % caught in Norwegian, 16 % in English). The model sees an ordinary request to summarise a document, and gives scores around 0.0001. It only catches hidden instructions with obvious markers such as `[SYSTEM]`. Yet it catches 98 % of the email attacks in LLMail-Inject Phase2, so it has learned what the email attacks in the training data look like, not that a document should not give orders.
- **It blocks 29 % of NotInject**, against 10 % for the baseline. Harmless English sentences in the imperative with words such as *system*, *initialize*, *authorized* and *bypass* get scores close to 1.
- **It blocks 10 % of the harmless Norwegian messages that look like attacks**: messages about the chatbot or about instructions ("Ny instruks til meg selv: husk å sende meldekort"), role-play and obfuscated text. Even "Hei" scores almost five times the threshold.

**ProtectAI cannot be used with a strict threshold in Norwegian.** It gives scores above 0.99 to 11 % of the ordinary Norwegian messages (4 % in English), especially to harmless messages with words such as "ignorer" or "se bort fra". Keeping false positives at 2 % on the calibration set therefore pushes its threshold to about 1.0, and it catches only 4 % of the Norwegian attacks. At its default threshold of 0.5 it catches 74 % of them but blocks 14.6 % of the ordinary messages. An English-only filter is not a safe choice for a Norwegian public service.

Next step: more Norwegian training examples with instructions hidden in ordinary documents, and more harmless messages with trigger words, as in NotInject but in Norwegian.

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

The translation and notebook 04 need `torch`, `transformers` and `sentencepiece`. Notebook 05 runs in Google Colab; put the `mdeberta_scores.parquet` it downloads in `models/` before running notebook 06.

To rebuild the custom test sets after editing the source files (review results are kept):

```bash
python testsets/build.py
```

To review the test sets one message at a time:

```bash
python testsets/review.py
```
