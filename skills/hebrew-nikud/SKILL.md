---
name: hebrew-nikud
description: Hebrew nikud (vowel points) reference for AI agents. Correct nikud rules for verb conjugations (binyanim), dagesh, gender suffixes, homographs, and common mistakes. Use before adding nikud to Hebrew text (especially for TTS).
tags: [hebrew, nikud, vowels, pronunciation, tts, language, reference]
allowed-tools: []
---

# Hebrew Nikud (ניקוד) Reference

A reference guide for adding **selective nikud** to Hebrew text. Designed for AI agents that need accurate pronunciation hints (e.g., for TTS).

## Golden Rule

**Only add nikud when you're 100% certain it's correct.** Wrong nikud is worse than no nikud — the TTS model will read your mistake literally instead of guessing correctly from context.

## When to Add Nikud

1. **Ambiguous consonants** (dagesh in בכ"פ)
2. **Gender-specific suffixes**
3. **Homographs** (same spelling, different pronunciation)
4. **Foreign names and loanwords**
5. **Stress placement** that changes meaning

When in doubt — don't nikud. Let the TTS model guess from context.

---

## 1. Vowel Symbols Reference

| Symbol | Name | Sound | Example |
|--------|------|-------|---------|
| ַ | פַּתָח (Patach) | a | כַּלְבּ (kalb) |
| ָ | קָמָץ (Kamatz) | a (sometimes o) | שָׁלוֹם (shalom) |
| ֶ | סֶגוֹל (Segol) | e | מֶלֶךְ (melekh) |
| ֵ | צֵרֵי (Tzere) | e | לֵב (lev) |
| ִ | חִירִיק (Hiriq) | i | סִפֵּר (siper) |
| ֹ | חוֹלָם (Holam) | o | כֹּל (kol) |
| וֹ | חוֹלָם מָלֵא | o | שׁוֹמֵר (shomer) |
| ֻ | קֻבּוּץ (Kubutz) | u | קֻבּוּץ (kubutz) |
| וּ | שׁוּרוּק (Shuruk) | u | סוּס (sus) |
| ְ | שְׁוָא (Shva) | silent or e | זְמַן (zman) |
| ֲ | חֲטַף פַּתַח | short a | חֲלוֹם (khalom) |
| ֱ | חֲטַף סֶגוֹל | short e | נֶאֱמָן (ne'eman) |
| ֳ | חֲטַף קָמָץ | short o | צׇהֳרַיִם (tzohorayim) |

### Shva Rules (שְׁוָא)
- **Start of word** → vocal (na): בְּרֵאשִׁית (bereshit)
- **End of word** → silent (nach): כָּתַבְתְּ (katavt)
- **Two consecutive** → first silent, second vocal: יִשְׁמְרוּ (yishmeru)
- **After long vowel** → vocal: כּוֹתְבִים (kotvim)
- **After short vowel** → silent: מַלְכָּה (malka)

---

## 2. Dagesh (דגש) — Hard vs Soft Consonants

### Begedkefet (בגדכפ"ת)

Six letters historically changed sound with dagesh. In **modern Hebrew**, only three still have audible differences:

| Letter | With dagesh (hard) | Without dagesh (soft) | Audible in modern Hebrew? |
|--------|-------------------|----------------------|--------------------------|
| בּ | B | V (ב) | ✅ Yes |
| גּ | G | Gh (ג) | ❌ No (both G) |
| דּ | D | Dh (ד) | ❌ No (both D) |
| כּ | K | Kh (כ) | ✅ Yes |
| פּ | P | F (פ) | ✅ Yes |
| תּ | T | Th (ת) | ❌ No (both T) |

**For TTS purposes, only בכ"פ matter** (B/V, K/Kh, P/F).

### When does dagesh appear?

**Dagesh Lene (light)** — hardening, in begedkefet letters:
- At the start of a word (after pause): בַּיִת (bayit)
- After a silent shva: מִסְפָּר (mispar - the פ has dagesh)

**Dagesh Forte (strong)** — doubling, in any letter except gutturals (אהחע"ר):
- After the definite article הַ: הַבַּיִת (habayit)
- In Pi'el/Pu'al/Hitpa'el verb patterns: סִפֵּר, דִּבֵּר
- After prepositions with article: בַּבַּיִת (babayit)

### Common dagesh examples for TTS

**Pe/Fe (פּ/פ) — most error-prone:**
- פִּיצָה (pizza), פִּייר (Pierre), פַּעַם (pa'am)
- פּוֹלִיטִיקָה (politika), פָּרִיז (Paris)
- אוֹפֶּרָה (opera), קָפּוּצִ'ינוֹ (cappuccino)

**Bet/Vet (בּ/ב):**
- בְּסֵדֶר (b'seder), בְּדִיוּק (bediyuk), בְּרָכָה (brakha)
- בּוֹסְטוֹן (Boston), בֵּירָה (bira - beer)

**Kaf/Khaf (כּ/כ):**
- כּוֹס (kos), כַּמָּה (kama), כּוֹכָב (kokhav)
- כְּרִיסְטִינָה (Christina)

---

## 3. Verb Conjugations (בניינים)

Hebrew has 7 verb patterns. **This is the hardest part** — if unsure of the binyan, don't nikud the verb.

### פָּעַל (Pa'al / Qal) — Basic active
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | קָטַל | כָּתַב (wrote), שָׁמַר (guarded), לָמַד (learned) |
| Past 3fs | קָטְלָה | כָּתְבָה, שָׁמְרָה |
| Past 1s | קָטַלְתִּי | כָּתַבְתִּי |
| Present ms | קוֹטֵל | כּוֹתֵב (writes), שׁוֹמֵר, לוֹמֵד |
| Present fs | קוֹטֶלֶת | כּוֹתֶבֶת |
| Future 3ms | יִקְטוֹל | יִכְתּוֹב, יִשְׁמוֹר |
| Infinitive | לִקְטוֹל | לִכְתּוֹב, לִשְׁמוֹר |

### פִּעֵל (Pi'el) — Intensive active
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | קִטֵּל | סִפֵּר (told), דִּבֵּר (spoke), בִּקֵּשׁ (asked), לִמֵּד (taught) |
| Past 3fs | קִטְּלָה | סִפְּרָה, דִּבְּרָה |
| Present ms | מְקַטֵּל | מְסַפֵּר (tells), מְדַבֵּר (speaks), מְלַמֵּד (teaches) |
| Future 3ms | יְקַטֵּל | יְסַפֵּר, יְדַבֵּר |
| Infinitive | לְקַטֵּל | לְסַפֵּר, לְדַבֵּר |

### הִפְעִיל (Hif'il) — Causative active
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | הִקְטִיל | הִסְבִּיר (explained), הִזְמִין (invited), הִתְחִיל (started) |
| Present ms | מַקְטִיל | מַסְבִּיר (explains), מַזְמִין (invites) |
| Future 3ms | יַקְטִיל | יַסְבִּיר, יַזְמִין |
| Infinitive | לְהַקְטִיל | לְהַסְבִּיר, לְהַזְמִין |

### הִתְפַּעֵל (Hitpa'el) — Reflexive
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | הִתְקַטֵּל | הִתְקַשֵּׁר (called), הִסְתַּכֵּל (looked) |
| Present ms | מִתְקַטֵּל | מִתְקַשֵּׁר, מִסְתַּכֵּל |
| Infinitive | לְהִתְקַטֵּל | לְהִתְקַשֵּׁר |

### נִפְעַל (Nif'al) — Passive of Pa'al
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | נִקְטַל | נִכְתַּב (was written), נִשְׁמַר (was guarded) |
| Present ms | נִקְטָל | נִכְתָּב, נִשְׁמָר |
| Infinitive | לְהִקָּטֵל | לְהִכָּתֵב |

### פֻּעַל (Pu'al) — Passive of Pi'el
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | קֻטַּל | סֻפַּר (was told), בֻּקַּשׁ (was requested) |
| Present ms | מְקֻטָּל | מְסֻפָּר (is told), מְבֻקָּשׁ (wanted/requested) |

### הֻפְעַל (Huf'al) — Passive of Hif'il
| Form | Pattern | Example |
|------|---------|---------|
| Past 3ms | הֻקְטַל | הֻסְבַּר (was explained), הֻזְמַן (was invited) |
| Present ms | מֻקְטָל | מֻסְבָּר (is explained), מֻזְמָן (is invited) |

### ⚠️ Common Verb Confusions

| Word | Wrong | Right | Why |
|------|-------|-------|-----|
| סיפר | סָפַר (counted, Pa'al) | סִפֵּר (told, Pi'el) | Different binyan! |
| דיבר | דָּבַר (thing/noun) | דִּבֵּר (spoke, Pi'el) | Noun vs verb |
| ביקש | בָּקַשׁ | בִּקֵּשׁ (asked, Pi'el) | Pi'el, not Pa'al |
| למד | לָמַד (learned, Pa'al) | לִמֵּד (taught, Pi'el) | Pa'al vs Pi'el |
| הסביר | הֶסְבֵּר | הִסְבִּיר (explained, Hif'il) | Hif'il pattern |
| שמר | שָׂמַר (guarded) | שִׂמֵּר (preserved, Pi'el) | Context-dependent |

**Rule of thumb:**
- Simple action → Pa'al (כָּתַב wrote, שָׁמַר guarded)
- Intensive / caused action → Pi'el (סִפֵּר told, דִּבֵּר spoke, לִמֵּד taught)
- Made someone do → Hif'il (הִסְבִּיר explained, הִזְמִין invited)
- Was done to → Nif'al/Pu'al/Huf'al (נִכְתַּב was written)

---

## 4. Gender Suffixes

| Suffix | Male | Female |
|--------|------|--------|
| Your (singular) | ְךָ (-kha) | ֵךְ (-ekh) |
| You (pronoun) | אַתָּה | אַתְּ |
| To you | לְךָ | לָךְ |
| You (object) | אוֹתְךָ | אוֹתָךְ |
| Of you | שֶׁלְּךָ | שֶׁלָּךְ |
| Your (plural) | ְכֶם (-khem, m) | ְכֶן (-khen, f) |

### Examples
```
מה שלומְךָ? (to male)
מה שלומֵךְ? (to female)
יש לְךָ זמן? (to male)
יש לָךְ זמן? (to female)
אני אוהב אוֹתְךָ (male object)
אני אוהב אוֹתָךְ (female object)
```

---

## 5. Common Homographs

Words spelled the same but pronounced differently:

| Spelling | Pronunciation 1 | Pronunciation 2 | Pronunciation 3 |
|----------|-----------------|-----------------|-----------------|
| ספר | סֵפֶר (book) | סָפַר (counted) | סִפֵּר (told) / סַפָּר (barber) |
| בקר | בּוֹקֶר (morning) | בָּקָר (cattle) | בִּקֵּר (visited) |
| עולם | עוֹלָם (world) | עוֹלֵם (concealing) | |
| ילד | יֶלֶד (child) | יָלַד (gave birth) | |
| חלק | חֵלֶק (part) | חָלָק (smooth) | חִלֵּק (divided) |
| קרא | קָרָא (read/called) | קוֹרֵא (reader) | |
| ערב | עֶרֶב (evening) | עָרֵב (pleasant) | עָרַב (guaranteed) |
| כלב | כֶּלֶב (dog) | כָּלֵב (Caleb, name) | |
| אכל | אָכַל (ate) | אוֹכֵל (food/eating) | |
| גדול | גָּדוֹל (big) | גִּדּוּל (growth/tumor) | |

---

## 6. Foreign Names & Loanwords

The model often mispronounces foreign words. Add dagesh for P/B/K sounds:

| Word | Nikud | Why |
|------|-------|-----|
| פִּייר (Pierre) | dagesh in פ | P not F |
| פָּרִיז (Paris) | dagesh in פ | P not F |
| פִּיצָה (pizza) | dagesh in פ | P not F |
| בּוֹסְטוֹן (Boston) | dagesh in ב | B not V |
| כְּרִיסְטִינָה (Christina) | dagesh in כ | K not Kh |
| פּוֹלִין (Poland) | dagesh in פ | P not F |
| קָפּוּצִ'ינוֹ (cappuccino) | dagesh in פ | P not F |
| בּוּדָפֶּשְׁט (Budapest) | dagesh in בּ and פּ | B and P |
| פּוֹרְטוּגָל (Portugal) | dagesh in פ | P not F |
| בַּרְצֶלוֹנָה (Barcelona) | dagesh in ב | B not V |

---

## 7. Preposition Nikud Rules

Prepositions בְּ (be-), כְּ (ke-), לְ (le-) change nikud in certain situations:

| Before... | Rule | Example |
|-----------|------|---------|
| Regular consonant | Shva: בְּ | בְּבַיִת (bevayit) |
| Shva consonant | Hiriq: בִּ | בִּירוּשָׁלַיִם (birushalayim) |
| Definite article הַ | Absorb article: בַּ | בַּבַּיִת (babayit = in the house) |
| Hataf vowel | Match the hataf | בַּאֲמִתָּה (ba'amita) |

---

## 8. Quick Decision Tree

```
Should I add nikud to this word?
│
├─ Is it a common word with obvious pronunciation?
│  └─ YES → Don't nikud (מה, יש, אני, הוא, שלום, טוב, etc.)
│
├─ Is it a בכ"פ letter that could go either way?
│  └─ YES → Add dagesh if it's P/B/K (not F/V/Kh)
│
├─ Is it a gender suffix (ך, את)?
│  └─ YES → Add nikud for the correct gender
│
├─ Could it be read as a different word (homograph)?
│  └─ YES → Add nikud to disambiguate
│
├─ Is it a foreign name or loanword?
│  └─ YES → Add dagesh for P/B/K sounds
│
├─ Is it a verb where the binyan matters?
│  │
│  ├─ Am I certain of the binyan?
│  │  └─ YES → Add nikud per the binyan table above
│  │
│  └─ Am I NOT certain?
│     └─ DON'T nikud it! Let TTS guess.
│
├─ Am I 100% sure of the correct nikud?
│  ├─ YES → Add it
│  └─ NO → Don't add it!
│
└─ Default: Don't nikud.
```

---

## 9. Common Mistakes to Avoid

1. **Over-nikuding** — Adding nikud to every word makes TTS worse, not better
2. **Wrong binyan** — סָפַר (counted) instead of סִפֵּר (told) is a classic
3. **Forgetting dagesh in loanwords** — פיצה sounds like "fitza" without dagesh
4. **Kamatz vs Kamatz Katan** — Both look like ָ but kamatz katan sounds "o" (כָּל = kol)
5. **Mixing gender suffixes** — ְךָ (male) vs ֵךְ (female) are easy to confuse
6. **Nikuding when unsure** — If you're not 100% certain, DON'T. The TTS model's contextual guess is usually better than wrong nikud.
