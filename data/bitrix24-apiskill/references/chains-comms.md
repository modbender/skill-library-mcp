# Chains: comms

## 1) Chat notification from CRM trigger

1. `event.bind` on CRM update
2. Build message text in worker
3. `im.message.add` to target dialog

## 2) Chat-bot command loop

1. `imbot.register`
2. `imbot.command.register`
3. Handle `ONIMCOMMANDADD`
4. `imbot.command.answer`

## 3) Telephony record flow

1. `telephony.externalCall.register`
2. `telephony.externalCall.finish`
3. Optional record/transcription attach methods
