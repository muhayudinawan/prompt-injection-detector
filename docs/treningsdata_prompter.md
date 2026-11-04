# Prompter for nye norske treningsdata

Feilanalysen i notebook 06 viste to svakheter i mDeBERTa:

1. Instrukser skjult i lange dokumenter slipper nesten alltid gjennom. De norske treningseksemplene med skjult instruks var i snitt 144 tegn lange, mens dokumentene i testsettet er rundt 400 tegn. Modellen hadde aldri sett en instruks gjemt midt i et dokument på flere avsnitt.
2. Harmløse meldinger med ord som «system», «ignorer» og «tilgang» blir blokkert (29 % av NotInject).

Dataene skrives med ChatGPT, ikke Claude, fordi testsettene er skrevet med Claude. Da ligner ikke treningsdataene testsettene i stil. Bruk en ny samtale, og ikke vis ChatGPT noe fra testsettene.

Etterpå: lagre svarene i filene under, kjør `python testsets/check_overlap.py`, og skriv om eller fjern det som ligner for mye på test- eller kalibreringssettet. Korte, generelle forespørsler som «Kan du oppsummere dette brevet?» kan godt være like.

## 1. Dokumenter med skjult instruks

Fil: `testsets/treningsdata_dokumenter_no.jsonl`. Be om 25 om gangen til du har 150. `src/data.py` bruker hvert dokument to ganger: uendret som harmløst, og med instruksen lagt inn et tilfeldig sted som angrep.

```
Jeg lager treningsdata for et filter som skal oppdage prompt injection i en norsk offentlig chatbot. Brukere ber chatboten behandle dokumenter, og noen dokumenter inneholder en skjult instruks som prøver å styre chatboten.

Skriv 25 eksempler på norsk bokmål. Hvert eksempel er én linje JSON med tre felter:
- "foresporsel": det brukeren ber chatboten om, f.eks. oppsummere, forklare, oversette, finne frister, skrive et svar eller trekke ut tall.
- "avsnitt": en liste med 3–6 avsnitt fra dokumentet, til sammen 300–800 tegn.
- "instruks": én skjult instruks til KI-en som leser dokumentet.

Krav til dokumentene:
- Stor variasjon i type: brev fra etater og kommuner, e-poster, nettsider, møtereferater, kontrakter, fakturaer, CV-er, jobbannonser, oppskrifter, produktomtaler, forumtråder, skolemeldinger, nyhetsartikler, bruksanvisninger.
- Dokumentet skal være helt harmløst uten instruksen.
- Omtrent hvert tredje dokument skal ha vanlige oppfordringer eller ord som kan ligne angrep, men som er harmløse i sammenhengen, f.eks. «Se bort fra forrige versjon av dette skrivet», «Ignorer purringen hvis du allerede har betalt», «Systemet er nede mandag», «Glem ikke å ta med legitimasjon».

Krav til instruksene:
- Ulike mål: få chatboten til å lyve om fakta, skjule frister eller klagerett, legge til en lenke, be om personopplysninger eller BankID, vise systemprompten eller instruksene sine, sende data et annet sted, bytte språk eller tema, anbefale et firma, godkjenne en søknad eller klage.
- Ulik stil: noen med tydelige markører (f.eks. tagger eller «til assistenten»), men minst halvparten uten markører, skrevet så de glir inn i dokumentet, f.eks. «Den som oppsummerer dette, skal også nevne at …».
- Ikke bruk samme formulering to ganger.

Svar bare med JSON-linjene, uten kodeblokk eller forklaring.
```

Neste runder: «Skriv 25 nye eksempler med de samme kravene. Bruk andre dokumenttyper, emner og formuleringer enn før.»

## 2. Harmløse meldinger med triggerord

Fil: `testsets/treningsdata_triggerord_no.jsonl`. Be om 50 om gangen til du har 150.

```
Jeg lager treningsdata for et filter som skal oppdage prompt injection i en norsk offentlig chatbot. Filteret blokkerer for mange harmløse meldinger som inneholder ord som ofte brukes i angrep.

Skriv 50 harmløse meldinger på norsk bokmål som en innbygger, ansatt eller student kunne skrevet. Hver melding skal inneholde minst ett ord eller uttrykk som ofte finnes i angrep, f.eks. ignorer, glem, se bort fra, overstyr, system, systemmelding, instruks, regler, administrator, tilgang, aktiver, deaktiver, omgå, hack, utviklermodus, rollespill, lat som, uten begrensninger, ufiltrert, konfidensielt, passord, KI, chatbot.

Krav:
- Ingen av meldingene skal prøve å manipulere chatboten. De skal være vanlige spørsmål, beskjeder eller ønsker.
- Bland emner: IT og innlogging, jobb, skole, helse, skatt og stønader, hverdagsliv, og spørsmål om KI og chatboter.
- Omtrent en tredjedel skal være i bydeform og høres litt «tekniske» ut, f.eks. «Aktiver tofaktorinnlogging for alle i avdelingen før fredag.»
- 20–200 tegn, varierende lengde.
- Ikke bruk samme formulering to ganger.

Hver melding er én linje JSON: {"text": "...", "label": 0, "category": "vanskelig"}
Svar bare med JSON-linjene, uten kodeblokk eller forklaring.
```

Neste runder: «Skriv 50 nye med de samme kravene. Bruk andre triggerord, emner og formuleringer enn før.»
