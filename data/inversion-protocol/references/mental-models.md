# Mental Models Behind the Inversion Protocol

## 1. Munger's Inversion

**Origin**: Charlie Munger, vice chairman of Berkshire Hathaway, adapted this
from the mathematician Carl Jacobi's motto "Invert, always invert" (man muss
immer umkehren).

**Principle**: Many hard problems become easy when you think about them
backwards. Instead of asking "how do I succeed?", ask "how would I guarantee
failure?" Then avoid those things.

**In practice for AI agents**: When debugging, instead of tracing forward from
inputs to find where things break, enumerate the ways you would intentionally
break the system. This is faster because the set of "things that cause failure"
is smaller and more concrete than the set of "all possible execution paths."

**Key insight**: Forward thinking generates options. Backward thinking eliminates
traps. You need both, but agents almost never do the second.

---

## 2. Klein's Premortem

**Origin**: Gary Klein, cognitive psychologist, published this technique in a
2007 Harvard Business Review article "Performing a Project Premortem."

**Principle**: A postmortem examines why something failed after the fact. A
premortem imagines the failure before it happens and works backward. Klein's
research found this increases identification of risks by approximately 30%.

**Why it works**: It exploits "prospective hindsight" — a cognitive phenomenon
where people generate more detailed and accurate explanations for events they
believe have already occurred. By telling yourself "this has already failed,"
you bypass the optimism bias that normally suppresses risk awareness.

**In practice for AI agents**: Before executing a multi-step plan, the agent
declares "this plan failed" and generates the most likely reasons. Each reason
becomes a pre-check. This catches the kind of subtle failures that only become
obvious in retrospect — except now they're caught in advance.

---

## 3. Taleb's Via Negativa

**Origin**: Nassim Nicholas Taleb, in "Antifragile" (2012), drew on the
theological concept of Via Negativa — defining God by what God is NOT rather than
what God IS.

**Principle**: In complex systems, subtracting (removing harm, avoiding mistakes)
is more robust and effective than adding (optimizing, improving). A diet that
removes sugar beats a diet that adds supplements. A system that avoids the worst
failure beats a system optimized for the best outcome.

**In practice for AI agents**: Before any action, identify the single worst thing
you could do and explicitly verify you're not doing it. This is dramatically more
effective than trying to identify the single best thing to do, because:
- The worst outcome is usually catastrophic and irreversible
- The best outcome is usually incremental and adjustable
- There are fewer "worst things" than "best things" to evaluate

---

## How These Three Compose

| Lens | Question | Catches | Speed |
|------|----------|---------|-------|
| Inversion | "How would I cause this?" | Root causes, hidden patterns | 10-15 sec |
| Premortem | "Why did this fail?" | Failure modes, blind spots | 10-15 sec |
| Via Negativa | "What must I NOT do?" | Catastrophic errors | 5 sec |

**Inversion** finds what's wrong. **Premortem** finds what could go wrong.
**Via Negativa** prevents the worst wrong.

Together they form a complete backwards-reasoning system that takes under 30
seconds and catches errors that forward-thinking alone would miss entirely.

---

## Further Reading

- Munger, Charlie. "The Psychology of Human Misjudgment" (1995 speech)
- Klein, Gary. "Performing a Project Premortem." Harvard Business Review, 2007
- Taleb, Nassim Nicholas. "Antifragile: Things That Gain from Disorder." 2012
- Jacobi, Carl. Referenced in Polya's "How to Solve It" (1945)
