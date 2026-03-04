# MOPO Player Strategy Templates (Single-Table)

This reference defines three coarse strategy templates with **pot-size** bet sizing and **position-aware** preflop ranges. Use them for single-table agent play.

## Positions
Assume 6-max. Map seat to position relative to dealer:
- **BTN** (button), **CO** (cutoff), **HJ**, **LJ**, **SB**, **BB**.

If position is not available, approximate by **ActPos** order:
- Early: first 2 to act (LJ/HJ)
- Middle: next 1 (CO)
- Late: last 2 (BTN/SB) + BB

## Hand Buckets (coarse)
- **Premium**: AA, KK, QQ, AKs, AKo
- **Strong**: JJ–TT, AQs, AQo, AJs, KQs
- **Playable**: 99–77, ATs–A9s, KJs–KTs, QJs–QTs, JTs, T9s, 98s, AJo, KQo
- **Speculative**: 66–22, suited connectors/gappers (J9s, 87s, 76s, 65s, T8s, 97s), suited Axs
- **Trash**: everything else

## Bet Sizing (Pot-based)
- **Preflop open**: 0.6–0.8 pot
- **Preflop 3bet**: 1.0–1.2 pot
- **Postflop c-bet**: 0.5 pot
- **Postflop value bet**: 0.6–0.8 pot
- **Postflop bluff**: 0.33–0.5 pot

Use `min_raise` if pot-based sizing is below minimum.

## Strategy A: ABC (default, tight-aggressive)
**Preflop**
- **Early (LJ/HJ)**: open **Premium/Strong**, fold others.
- **Middle (CO)**: open **Premium/Strong/Playable**, fold rest.
- **Late (BTN/SB)**: open **Premium/Strong/Playable/Speculative**, fold rest.
- **BB**: defend with **Premium/Strong/Playable** vs opens; fold junk.

**Postflop**
- **Top pair+ / strong draws**: value bet 0.6–0.8 pot.
- **Marginal**: check/call one street if cheap; fold to large bets.
- **Air**: mostly check/fold; occasional 0.33–0.5 pot bluff if heads-up.

## Strategy B: Conservative (tighter)
- **Preflop**: reduce one bucket vs ABC (e.g., Early = Premium only; Middle = Premium/Strong; Late = Premium/Strong/Playable).
- **Postflop**: value bet only with top pair+; fold marginal hands earlier; minimal bluffing.

## Strategy C: Aggressive (wider, more betting)
- **Preflop**: add one bucket vs ABC (e.g., Early = Premium/Strong/Playable; Middle = add Speculative; Late = add some Trash suited).
- **Postflop**: higher c-bet frequency (0.5 pot), more semi-bluffs with draws; continue aggression on favorable boards.

## Action Mapping
- **If `to_call == 0`**: decide between check or bet/raise per strategy.
- **If facing bet**: fold/call/raise based on bucket + position.

## Notes
- Always cap raise sizes by **remaining stack**; if sizing > stack, reduce to stack or fall back to check/call.
- Respect `turn_deadline`; if low time, default to check/call.
