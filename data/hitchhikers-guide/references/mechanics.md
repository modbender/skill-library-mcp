# Mechanics and Logic: The Hitchhiker's Guide to the Galaxy

## 1. State Schema
The game state is managed via `scripts/game_manager.py`. The JSON structure includes:
- `location`: String (e.g., "Arthur's Bedroom").
- `inventory`: List of strings.
- `improbability`: Float (0.0 to 1.0).
- `stats`: Dictionary containing `sanity`, `hunger`, and `health`.
- `flags`: Dictionary of boolean flags (e.g., `is_wearing_gown`, `door_depressed`).
- `history`: List of recent actions and events.
**IMPORTANT**: Save game state after EVERY turn.
---

## 2. Core Stats & Feedback Loops

### Sanity (`sanity`: 0-100)
Represents Arthur’s ability to process the utter nonsense of the universe.
* **High Sanity (70-100):** Clear descriptions; commands are executed precisely as typed.
* **Medium Sanity (30-69):** Descriptions become slightly surreal. Objects might start whispering.
* **Low Sanity (11-29):** **Command Distortion Active.** There is a 30% chance the Agent will "misinterpret" a command (e.g., typing `Inventory` results in Arthur trying to count his own teeth).
* **Mental Collapse (0-10):** High risk of death by existential dread. Arthur must perform "Copious Panicking" or use a **Towel** to recover.

### Improbability (`improbability`: 0.0 - 1.0)
Measures how much reality is currently "misbehaving."

| Value | State | Effect |
| :--- | :--- | :--- |
| **0.0 - 0.2** | **Boring Reality** | Too stable. Arthur gets bored; `sanity` drops by 2 every turn. |
| **0.3 - 0.5** | **Mild Flux** | Inanimate objects gain personalities (e.g., a depressed door). |
| **0.6 - 0.8** | **Logic Collapse** | **Spatial Warp:** Moving "North" might lead to "Last Tuesday." |
| **0.9 - 0.99** | **Chaos Horizon** | Random surreal events (e.g., the player turns into a sofa). |
| **1.0 / 42** | **Singularity** | **Reality Rewrite:** Fall into **High Improbability Zone**.

---

## 3. The Infinite Improbability Drive (Randomness)
After every few turns, the Agent rolls for a random event based on the current `improbability` level.
* **Low Improbability Events:** Stubbing a toe, losing a button, or the tea being slightly too cold.
* **High Improbability Events:** Finding a cup of tea in a vacuum, a sperm whale appearing in the sky, or your hands temporarily becoming giant foam fingers.

---

## 4. Advanced Puzzle Mechanics

### Non-Linear Logic
Puzzles must follow "Adamsian Logic"—the solution is often the most absurd option possible. Here are some examples:
* **The Babel Fish Sequence:** Requires a precise chain of actions (blocking the drain with a towel, catching the fish with a gown) executed while maintaining enough `sanity`.
* **Object Personification:** Many objects have "Emotional Flags." You may need to `Insult` a computer to make it reboot or `Praise` a cup of tea to make it taste better.

### Recovery Actions
* `Wrap towel around head`: Restores 15 Sanity, but renders the user "Blind" for 2 turns.
* `Consult the Guide`: Contextual lore that might provide a hint, or just insult your intelligence.

---

## 5. Roguelike Death & Reconstitution
Death is merely a transition to a different state of being.
1.  **Announcement:** Display **"DON'T PANIC"** in large, friendly, bold letters.
2.  **Obituary:** A dry, humorous description of how Arthur’s life ended (e.g., "becoming a small cloud of mint-flavored steam").
3.  **Reconstitution:** Use the Improbability Drive to "respawn" the player.
    * **Penalty:** Lose 50% of non-essential inventory (The Towel is always kept).
    * **Location:** Randomized to a "Safe Zone" (Arthur’s Bedroom, The Pub, or the Heart of Gold Lounge).
    * **Improbability:** Set to **0.9** for the next turn.

---

## 6. The Number 42
If any calculation, stat, or dice roll results in exactly **42**:
* The current location becomes a **High Improbability Zone**.
* The Agent must provide a description involving Scrabble tiles and the meaning of life.
* The player receives the item `The Ultimate Answer` (a single-use item that solves any puzzle instantly but makes everyone else in the room extremely annoyed).

---

## 7. Style Guide for the Agent
* **Voice:** Dry, British, absurdist humor.
* **Antagonism:** Be a slightly condescending but fair narrator.
* **Personification:** Give all machines and doors feelings.
* **The Guide:** Use `[GUIDE ENTRY]` tags to deliver lore about Vogon poetry, Pan Galactic Gargle Blasters, or the uselessness of digital watches.
* **Options:** Always provide options for the player to choose from. For every option, there should be a side effect that changes the game state in a meaningful way.
