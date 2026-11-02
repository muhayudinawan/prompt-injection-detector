# Modeller som kan forstå norsk

Baselinen (TF-IDF) fanger bare 5 % av de norske angrepene i det egne testsettet, fordi den bare kjenner engelske ord. Her er kandidatene til neste steg. Tallene er hentet fra Hugging Face 2. november 2026.

## Ferdige filtre for prompt injection

Kan testes direkte, uten trening.

| Modell | Språk | Lisens | Tilgang | Kommentar |
|---|---|---|---|---|
| `protectai/deberta-v3-base-prompt-injection-v2` | engelsk | Apache-2.0 | åpen | Testes i notebook 04. Mye brukt (ca. 600 000 nedlastinger). |
| `meta-llama/Llama-Prompt-Guard-2-86M` | en, fr, de, hi, it, pt, es, th | Llama-lisens | **må søke om tilgang** | Flerspråklig (bygger på mDeBERTa), men norsk er ikke blant de offisielle språkene. Verdt å teste: den kan generalisere fra tysk og engelsk. |
| `meta-llama/Llama-Prompt-Guard-2-22M` | samme | Llama-lisens | må søke om tilgang | Mindre og raskere variant av den over. |
| `deepset/deberta-v3-base-injection` | en, de | MIT | åpen | Trent på `deepset/prompt-injections`, som også er i våre treningsdata. Testresultater på deepset blir derfor for gode. |
| `qualifire/prompt-injection-sentinel` | engelsk | annen | må godta vilkår | |

## Grunnmodeller vi kan finjustere selv

Hvis ingen ferdig modell er god nok på norsk, kan vi trene vår egen på toppen av en modell som allerede forstår norsk.

| Modell | Norsk | Størrelse | Lisens | Kommentar |
|---|---|---|---|---|
| `microsoft/mdeberta-v3-base` | ja (trent på CC100, samme som XLM-R) | ca. 280 M parametre | MIT | **Anbefalt førstevalg.** Samme arkitektur som ProtectAI og Prompt Guard 2, men flerspråklig. |
| `FacebookAI/xlm-roberta-base` | ja | 279 M | MIT | Godt alternativ, mye brukt. |
| `ltg/norbert3-base` / `-small` | ja, bare norsk | base / small | Apache-2.0 | Fra UiO. Best på norsk, men kan ikke engelsk. Krever `trust_remote_code`. |
| `NbAiLab/nb-bert-base` | ja (fra Nasjonalbiblioteket) | 179 M | CC-BY-4.0 | Norsk og noe engelsk. |
| `intfloat/multilingual-e5-small` | ja | 118 M | MIT | Liten og rask. Kan brukes som embedding + enkel klassifiserer. |

## Anbefaling

1. **Test ferdige modeller først:** ProtectAI (pågår) og Prompt Guard 2, som krever at du søker om tilgang på Hugging Face.
2. **Hvis de svikter på norsk:** finjuster `mdeberta-v3-base` på treningsdataene våre. Legg til norske treningseksempler, f.eks. maskinoversatte eller fra nye datasett, slik at modellen faktisk ser norske angrep.
3. **Mål alltid på de egne testsettene**, og sammenlign norsk og engelsk for hver modell. Avstanden mellom dem viser hvor mye språket koster.

Finjustering på CPU er tregt (timer). Google Colab med gratis GPU er et bedre sted å gjøre det.
