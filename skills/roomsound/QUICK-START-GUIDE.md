# RoomSound Quick Start Guide

Use this guide for user-facing requests. The agent handles technical setup and execution.

## 1) Let the Agent Initialize RoomSound

Tell the agent:
- "Initialize RoomSound on this system."
- Approve permission prompts if the agent asks to install packages.

## 2) Set Speaker Aliases

Tell the agent:
- "List my speakers and help me name them."
- "Set living room to the Bose speaker."
- "Set kitchen to the JBL speaker."

## 3) Daily Use

Use natural requests like:
- "Play ambient music on living room speaker."
- "Switch to kitchen speaker."
- "Play this YouTube link on bedroom speaker."
- "What speakers are available right now?"

Default playback behavior:
- The agent builds a context-aware queue (time of day, recent activity, known preferences).
- The agent looks up YouTube options with track duration shown in results.
- The queue target is at least 90 minutes total playback, unless you ask for a specific list or different length.

## 4) If Something Fails

Tell the agent what happened, for example:
- "No sound is coming out."
- "Bluetooth speaker won’t connect."
- "Search results are not showing properly."

The agent should run the technical fixes automatically.
