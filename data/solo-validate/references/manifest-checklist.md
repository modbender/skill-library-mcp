# Manifest Alignment Checklist

Extracted from `0-principles/manifest.md`. Check each principle against the idea.

## Principles

| # | Principle | Core Rule | Red Flag If... |
|---|-----------|-----------|----------------|
| 1 | **Privacy-first** | Data local, on-device, no cloud for core function | Cloud-dependent, data goes to 3rd party |
| 2 | **Offline-first** | Works without internet for core features | Requires constant connection |
| 3 | **One pain -> one feature -> launch** | Single problem, single solution, ship in days | "Platform", multiple features, complex onboarding |
| 4 | **AI as foundation** | AI is the core architecture, not a bolt-on | Remove AI and product still works |
| 5 | **Speed over perfection** | MVP in days, not months | MVP needs >2 weeks |
| 6 | **Antifragile architecture** | Modular, replaceable, no single point of failure | Single vendor lock-in, monolith |
| 7 | **Money without overheating** | Revenue before automation, honest pricing | Burns cash hoping for scale |
| 8 | **Against exploitation** | Serves people, doesn't extract from them | Dark patterns, addiction mechanics, manipulation |
| 9 | **Subscription fatigue** | One-time purchase if no ongoing cost | Monthly fee for something that doesn't cost monthly |

## Red Flags (Instant Kill)

From manifest's "Red Flags I Cut Immediately":

- [ ] "Just another feature like everyone else has"
- [ ] One client >30% of revenue
- [ ] Vanity metrics with no connection to money or retention
- [ ] Turns "one function" into "a platform"
- [ ] Releases that can't be rolled back in a day
- [ ] Products that exploit, discriminate, or manipulate

## Scoring

- **0 violations** = perfect alignment
- **1-2 violations** = proceed with caution, document conflicts
- **3+ violations** = strong KILL signal

## The Oath (key lines)

> "I cut everything except value."
> "We should be creators, not robots."
> "Tools that help people reflect, create, and own their narrative."

If the idea doesn't serve creators or doesn't help people reflect/create/own — it conflicts with the core mission.
