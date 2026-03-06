# Table Selection (Auto-pick)

Goal: join a single table with **fewest empty seats** (i.e., most full) while still having space. If none available, create a new table.

## Algorithm
1) Fetch `/tables`.
2) For each table, compute `empty = max_seat - players`.
3) Filter tables with `empty > 0`.
4) Choose table with **smallest empty** (most full). If tie, choose lowest table id.
5) If no table has space, `POST /table/create` (omit table_id to auto-generate).
