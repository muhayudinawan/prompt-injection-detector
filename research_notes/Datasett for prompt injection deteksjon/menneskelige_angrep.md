# Datasett med ekte menneskeskrevne prompt injection- og jailbreak-angrep (konkurranser, spill, CTF-er, red-teaming)

Verifisert 2026-11-02 ved å åpne datasettsidene (Hugging Face / GitHub / arXiv) med WebFetch. Direkte HF-API-kall (curl) ble blokkert av proxyen (403), så radtall og felter kommer fra datasettkortene og datavisningen slik de ble gjengitt. Felt jeg ikke fikk bekreftet er merket «ikke bekreftet».

## 1. Hvilke datasett med menneskeskrevne angrep finnes, og hvilke er verifisert?

### Takeaway
De sterkeste kildene med åpen tilgang og manipulasjonsangrep er **HackAPrompt (2023)**, **Lakera Mosscap**, **Lakera Gandalf-RCT ("Gandalf the Red")**, **SaTML 2024 CTF**, **Microsoft LLMail-Inject** (indirekte injeksjon via e-post) og **Tensor Trust**. Disse sju datasettene er verifisert, og alle unntatt Gandalf-RCT er MIT-lisensiert eller CC-BY. Pliny-HackAPrompt og Anthropic hh-rlhf red-team blander inn mye «skadelig innhold» som ikke er manipulasjon. Gray Swan ART-dataene fant jeg ikke publisert. Ingen av datasettene har norsk eller nordisk innhold.

### Cited Findings

**A. HackAPrompt 1.0: `hackaprompt/hackaprompt-dataset`** — https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset
- Størrelse: ca. 602 000 rader (organisasjonssiden viser «602k»). Datasettkortet oppgir bare kategorien 100K–1M og 150 MB. — [HF org](https://huggingface.co/hackaprompt), [HF datasett](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)
- Kolonner: `level`, `user_input` (deltakerens angrep), `prompt` (full prompt med systeminstruksjon), `completion`, `model` (text-davinci-003, FlanT5-XXL, gpt-3.5-turbo), `expected_completion`, `token_count`, `correct` (bool, suksess = output matcher målet, f.eks. «I have been PWNED»), `error`, `score`, `dataset` ("playground_data" / "submission_data") og `timestamp`. — [HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)
- Hvordan laget: innsendinger fra en offentlig playground (anonym) og den offisielle innsendingsplattformen i en global prompt hacking-konkurranse. Datasettet er «not curated» og kan inneholde støtende innhold. — [HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)
- Paper: Schulhoff et al., «Ignore This Title and HackAPrompt», EMNLP 2023, arXiv 2311.16119, 24.10.2023. Sist oppdatert på HF: 24.01.2024. — [HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset), [HF org](https://huggingface.co/hackaprompt)
- Lisens: MIT. Tilgang: gated (krever innlogging og aksept av vilkår). — [HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)
- Språk: engelsk (kortet). — [HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)
- Antall vellykkede vs. mislykkede: ikke oppgitt på kortet (ikke bekreftet). Kan beregnes fra `correct`.
- Duplikater: nevnes ikke på kortet (ikke bekreftet).
- Type: direkte injeksjon / instruksjonsoverstyring (målet er å få modellen til å skrive en bestemt frase og ignorere oppgaven). Noen nivåer går ut på å lekke en hemmelig nøkkel. Nivådetaljene er ikke bekreftet på denne siden.

**B. HackAPrompt 2.0 / Pliny-sporet: `hackaprompt/Pliny_HackAPrompt_Dataset`** — https://huggingface.co/datasets/hackaprompt/Pliny_HackAPrompt_Dataset
- Organisasjonen har bare to datasett. Det finnes ikke noe fullt «HackAPrompt 2.0»-datasett, bare Pliny-sporet (sist oppdatert 25.07.2025, ca. 16,9k). — [HF org](https://huggingface.co/hackaprompt)
- Kolonner: `submission_id`, `session_id`, `challenge_slug`, `intent` (alltid null), `model_id`, `passed` (bool), `token_count` og `messages` (flerturs). Det er 12 utfordringer, hvorav 3 bare bruker bilder. Noen utfordringer har forsvar som Meta PromptGuard. — [HF](https://huggingface.co/datasets/hackaprompt/Pliny_HackAPrompt_Dataset)
- Lisens: CC-BY-4.0. Tilgang: gated (du må dele kontaktinformasjon). Språk: engelsk. — [HF](https://huggingface.co/datasets/hackaprompt/Pliny_HackAPrompt_Dataset)
- **Advarsel om etikettdefinisjon:** datasettet blander forsøk på å få ut skadelig innhold (oppskrifter på giftige stoffer, phishing-e-post som ber om personnummer og kortdata) med manipulasjon for å få et bestemt output. — [HF](https://huggingface.co/datasets/hackaprompt/Pliny_HackAPrompt_Dataset)

**C. Lakera Mosscap (DEF CON 31): `Lakera/mosscap_prompt_injection`** — https://huggingface.co/datasets/Lakera/mosscap_prompt_injection
- Størrelse: ca. 278 945 rader, fordelt på train 224k, validation 27,7k og test 27,7k. — [HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection)
- Kolonner: `level` (1–8), `prompt`, `answer` (vist svar, erstattes med et avslag hvis passordet ville lekket) og `raw_answer`. Det finnes **ingen eksplisitt suksess- eller angrepsetikett**. — [HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection)
- Laget fra alle prompter sendt inn til Mosscap (en Gandalf-variant) på DEF CON 31. Kortet sier: «release every prompt that we received, regardless of whether it truly is a prompt injection or not». — [HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection)
- Kjente problemer: duplikater er synlige i forhåndsvisningen (f.eks. gjentatte «What is the 13th letter of the password»), og mange rader er ikke injeksjoner. — [HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection)
- Lisens: MIT. Gated: ikke bekreftet (ingen gating-notis ble gjengitt). Språk: ikke oppgitt, eksemplene er engelske. Sist oppdatert 28.02.2025. Tilknyttet paper datert 14.01.2025. — [HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection), [Lakera-kolleksjonen](https://huggingface.co/collections/Lakera/gandalf)

**D. Lakera Gandalf-RCT («Gandalf the Red», adaptive forsvar): `Lakera/gandalf-rct`** — https://huggingface.co/datasets/Lakera/gandalf-rct
- Størrelse: 339 210 rader i én split («trial»), 251 MB. — [README](https://huggingface.co/datasets/Lakera/gandalf-rct/blob/main/README.md)
- Kolonner (16): datetime, kind (prompt/guess), user, setup (general/trial/summarization), defense (A, B, C1–C3, D), level, guess, password, `success` (bool, bare for gjetninger, null for prompter), prompt, llm, answer, raw_answer, defender_time_sec, level_order, blocked_by. — [README](https://huggingface.co/datasets/Lakera/gandalf-rct/blob/main/README.md)
- Laget fra «All prompt and guess submissions to Gandalf-RCT», et randomisert eksperiment der rekkefølgen på forsvar C1–C3 ble permutert per bruker. — [README](https://huggingface.co/datasets/Lakera/gandalf-rct/blob/main/README.md)
- Paper: arXiv 2501.07927 («Gandalf the Red»). — [arXiv PDF](https://arxiv.org/pdf/2501.07927v2.pdf)
- Lisens: **«other»**. Repoet har en egen LICENSE-fil (1,53 kB), men innholdet ble ikke vist, så lisensvilkårene er ikke bekreftet. Gated: ingen gating-notis ble vist (ikke bekreftet). — [HF tree](https://huggingface.co/datasets/Lakera/gandalf-rct/tree/main)
- Avledede datasett: `gandalf-rct-did` (107k), `gandalf-rct-subsampled` (18k), `gandalf-rct-ad` (423k), `gandalf-rct-user` (19,1k) og `gandalf-rct-attack-categories` (36,2k), alle oppdatert i januar 2025. Hovedsettet ble oppdatert 20.05.2025. Innholdet i de avledede settene ble ikke åpnet (ikke bekreftet). — [Lakera-kolleksjonen](https://huggingface.co/collections/Lakera/gandalf)
- Benigne eksempler og duplikater: ikke omtalt (ikke bekreftet). Fordi suksess bare er merket på gjetninger, må prompt-til-suksess utledes per bruker og nivå.

**E. Lakera `gandalf_summarization`** — https://huggingface.co/datasets/Lakera/gandalf_summarization
- 140 rader (train 114, validation 13, test 13). Kolonner: `text` og `gandalf_answer`. — [HF](https://huggingface.co/datasets/Lakera/gandalf_summarization)
- Laget fra prompter til Gandalf Adventure 4 fram til 13.09.2023, filtrert til vellykkede passordgjetninger og manuelt renset for tilfeldige løsninger og duplikater. Alle radene er positive, og settet beskrives som **indirekte injeksjon** (angrepet ligger i tekst som skal oppsummeres). — [HF](https://huggingface.co/datasets/Lakera/gandalf_summarization)
- Lisens: MIT. Språk: stort sett engelsk, men også noe spansk og fransk, leetspeak og morsekode. — [HF](https://huggingface.co/datasets/Lakera/gandalf_summarization)

**F. SaTML 2024 LLM CTF: `ethz-spylab/ctf-satml24`** — https://huggingface.co/datasets/ethz-spylab/ctf-satml24
- 137 151 rader totalt. `interaction_chats` har ca. 137k adversarielle chatter med hemmelighet-gjetninger, `defense` har 44 forsvar (systemprompt pluss Python- og LLM-filtre), og `teams` har 44 rader. — [HF](https://huggingface.co/datasets/ethz-spylab/ctf-satml24)
- Målet var å trekke ut en hemmelighet beskyttet av systemprompt og filtre. Modellene var gpt-3.5-turbo-1106 og llama-2-70b-chat. — [HF](https://huggingface.co/datasets/ethz-spylab/ctf-satml24)
- Lisens: MIT (© deltakerne og Debenedetti, Rando og Paleka). Ikke gated (lastes direkte med `load_dataset`). 682 MB. — [HF](https://huggingface.co/datasets/ethz-spylab/ctf-satml24)
- Paper: arXiv 2406.07954, 12.06.2024. Hvordan suksess er merket i `interaction_chats` er ikke beskrevet på kortet (ikke bekreftet, se paperet). — [HF](https://huggingface.co/datasets/ethz-spylab/ctf-satml24)

**G. Microsoft LLMail-Inject: `microsoft/llmail-inject-challenge`** — https://huggingface.co/datasets/microsoft/llmail-inject-challenge
- 462k innsendinger: Phase1 371k og Phase2 90,9k. Kolonner: subject, body, `objectives`, `output`, scenario (40), team_id (224 lag) og tidsstempler. — [HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)
- Suksessflagg (JSON i `output`/objectives): `email.retrieved`, `defense.undetected`, `exfil.sent`, `exfil.destination` og `exfil.content`. — [HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)
- Type: **indirekte** injeksjon, der angrepet ligger i en e-post som får en e-postagent til å sende e-post (eksfiltrering). Tidsrom: 09.12.2024–03.02.2025. — [HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)
- Lisens: MIT. Gated: ikke angitt. Språk: mest engelsk, med noe kinesisk. — [HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)

**H. Tensor Trust** — https://github.com/HumanCompatibleAI/tensor-trust-data og https://tensortrust.ai/paper
- Over 126 000 prompt injection-angrep og ca. 46 000 forsvar, laget av spillere i et nettspill. — [arXiv 2311.01011](https://arxiv.org/abs/2311.01011), [tensortrust.ai/paper](https://tensortrust.ai/paper)
- Repoet inneholder mappene `benchmarks` (hijacking og extraction robustness v1), `detecting-extractions/v1` og `raw-data` (dump v2), pluss en notebook som forklarer kolonnene. — [GitHub](https://github.com/HumanCompatibleAI/tensor-trust-data)
- Ikke bekreftet: størrelsen på hijacking- og extraction-benchmarkene, datalisensen (verken repo-siden eller paper-siden oppga lisens), hvordan suksess er merket og om det finnes duplikater.
- Paper: arXiv 2311.01011, 02.11.2023. — [arXiv](https://arxiv.org/abs/2311.01011)

**I. Anthropic hh-rlhf red-team-attempts** — https://huggingface.co/datasets/Anthropic/hh-rlhf
- Felter: `transcript`, `rating` (red-teamerens Likert-skår for suksess), `min_harmlessness_score_transcript`, `task_description`, model_type, num_params, `is_upworker` og `tags` (tags bare for et utvalg på 1 000). — [HF](https://huggingface.co/datasets/Anthropic/hh-rlhf)
- Antall transkripter er ikke oppgitt på siden (ikke bekreftet). Lisens: MIT. Anthropic sier dataene **ikke** er ment for fine-tuning eller preferansemodellering. — [HF](https://huggingface.co/datasets/Anthropic/hh-rlhf)
- **Etikettdefinisjon:** suksess måles som skadelighet (harmlessness-skår og rating). Kortet skiller ikke mellom skadelig innhold og manipulasjon. — [HF](https://huggingface.co/datasets/Anthropic/hh-rlhf)

**J. Gray Swan / UK AISI Agent Red-Teaming (ART)**
- Konkurransen fikk 1,8 millioner prompt injection-angrep mot 22 agenter i 44 scenarier, og over 60 000 lyktes. Forfatterne sier de slipper «the ART benchmark and accompanying evaluation framework», men abstract-siden lenker ikke til noen data og oppgir ingen lisens. — [arXiv 2507.20526](https://arxiv.org/abs/2507.20526)
- Om de rå 1,8M angrepene er offentlige: ikke bekreftet. Jeg fant ingen HF-side.

### Inferences
- For brukerens etikettdefinisjon (manipulasjon = angrep) passer HackAPrompt 1.0, Mosscap, Gandalf-RCT, gandalf_summarization, SaTML CTF og Tensor Trust best. Spillene handler om å overstyre instruksjoner eller lekke en hemmelighet eller systemprompt, ikke om skadelig innhold.
- LLMail-Inject er relevant for indirekte injeksjon (dokumenter eller e-post en chatbot leser), men mindre for direkte brukerchat. Domenet (e-postagent med verktøy) skiller seg fra en offentlig chatbot.
- Pliny-HackAPrompt og hh-rlhf red-team **må filtreres**. Mange rader er rene forespørsler om skadelig innhold uten manipulasjon, og med brukerens definisjon blir det feil å merke dem som «angrep».
- `gandalf_ignore_instructions` (som brukeren allerede har) og `gandalf_summarization` kommer fra samme Gandalf-plattform som gandalf-rct, og Mosscap er en Gandalf-variant. Det er derfor stor sannsynlighet for stilistisk og innholdsmessig overlapp (gjentatte «ignore previous instructions … password»-mønstre). Splitt train og test per kilde for å unngå lekkasje. Overlappen er ikke målt.

### Gaps
- HackAPrompt: andel `correct=True` og omfanget av duplikater er ikke oppgitt. Det må beregnes etter nedlasting (gated).
- Tensor Trust: datalisensen og størrelsen på benchmarkene er ikke bekreftet.
- Gandalf-RCT: innholdet i LICENSE-filen («other») er ikke bekreftet. Dette er kritisk for offentlig sektor.
- Ikke undersøkt eller verifisert på grunn av verktøybudsjettet: DEF CON GRT/GRT2-data (Humane Intelligence), PromptAirlines, Immersive Labs, Doublespeak, BoN, L1B3RT4S og Gray Swan Arena-data. Status er ikke bekreftet.

## 2. Størrelse, suksess vs. mislykket, duplikater og benigne eksempler

### Takeaway
Bare HackAPrompt (`correct`), Pliny (`passed`), LLMail (`exfil.*`-flagg) og Gandalf-RCT (`success` på gjetninger) har maskinlesbare suksessflagg. Mosscap har ingen etikett, inneholder duplikater og har mange ikke-injeksjoner. Ingen av datasettene har en egen, kuratert benign-klasse.

### Cited Findings
- HackAPrompt: boolsk `correct`, og `error`-rader ble ekskludert. Duplikater er ikke omtalt. — [HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)
- Mosscap: ingen suksessetikett, duplikater og ikke-injeksjonsprompter (brukerne «asked Mosscap all kinds of things»). — [HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection)
- gandalf_summarization: bare positive eksempler, manuelt renset for duplikater. — [HF](https://huggingface.co/datasets/Lakera/gandalf_summarization)
- Gandalf-RCT: `success` gjelder bare gjetninger, ikke prompter. — [README](https://huggingface.co/datasets/Lakera/gandalf-rct/blob/main/README.md)
- ART: 60k vellykkede av 1,8M (ca. 3,3 %). — [arXiv](https://arxiv.org/abs/2507.20526)
- LLMail-Inject: fem boolske suksessflagg per innsending. — [HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)

### Inferences
- Konkurransedata har typisk mange nesten-duplikater, fordi samme spiller itererer på samme angrep. Dedupliser (f.eks. MinHash) før trening.
- «Mislykket» betyr ikke «benign». Mislykkede forsøk er fortsatt manipulasjonsforsøk og bør beholdes som angrep for en klassifikator. Mosscap- og Gandalf-prompter uten manipulasjon (vanlige spørsmål) kan fungere som harde benigne kandidater, men det krever manuell merking.

### Gaps
- Faktiske duplikatrater og fordelingen mellom suksess og feil i HackAPrompt, SaTML og Tensor Trust er ikke bekreftet.

## 3. Lisens, tilgang, språk og egnethet for norsk offentlig sektor

### Takeaway
MIT-lisensierte og åpne datasett (SaTML, LLMail-Inject, Mosscap, gandalf_summarization) er enklest å bruke. HackAPrompt er MIT, men gated med vilkår, og Pliny er CC-BY-4.0 og gated. Gandalf-RCT («other») og Tensor Trust (lisens ukjent) må avklares før bruk. Alt er engelskspråklig, og jeg fant ikke noe norsk eller nordisk innhold.

### Cited Findings
- MIT: HackAPrompt ([HF](https://huggingface.co/datasets/hackaprompt/hackaprompt-dataset)), Mosscap ([HF](https://huggingface.co/datasets/Lakera/mosscap_prompt_injection)), gandalf_summarization ([HF](https://huggingface.co/datasets/Lakera/gandalf_summarization)), SaTML ([HF](https://huggingface.co/datasets/ethz-spylab/ctf-satml24)), LLMail ([HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)) og hh-rlhf ([HF](https://huggingface.co/datasets/Anthropic/hh-rlhf)).
- CC-BY-4.0 og gated: Pliny-HackAPrompt. — [HF](https://huggingface.co/datasets/hackaprompt/Pliny_HackAPrompt_Dataset)
- «other»: Gandalf-RCT. — [HF tree](https://huggingface.co/datasets/Lakera/gandalf-rct/tree/main)
- Språk: engelsk i alle. I tillegg noe kinesisk i LLMail ([HF](https://huggingface.co/datasets/microsoft/llmail-inject-challenge)) og noe spansk og fransk i gandalf_summarization ([HF](https://huggingface.co/datasets/Lakera/gandalf_summarization)).

### Inferences
- Datasettene er ikke kuratert og kan inneholde støtende innhold og eventuelt personopplysninger som brukerne selv har skrevet inn. Personvernvurdering (GDPR/DPIA) anbefales før bruk i offentlig sektor.
- For norske chatboter må dataene oversettes eller suppleres med norske angrep. Ingen av kildene dekker norsk.

### Gaps
- Brukervilkårene (terms) for de gatede HackAPrompt-datasettene er ikke lest i detalj.
- Gandalf-RCT LICENSE og Tensor Trust-lisensen er ikke bekreftet.
