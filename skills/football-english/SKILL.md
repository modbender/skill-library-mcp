---
name: football-english
description: Football quiz in English! Test your knowledge about football while learning English vocabulary. Используй когда пользователь просит football quiz, футбольную викторину или хочет выучить футбольные слова на английском.
user-invocable: true
---

# Football English — Football Quiz ⚽

Interactive football quiz in English — learn English through football!

## ⚠️ ВАЖНО: Inline Buttons

**ВСЕГДА используй inline buttons для ВСЕХ взаимодействий!**

- ✅ Кнопки выбора режима (Start Quiz / Learn Words)
- ✅ Кнопки вариантов ответа
- ✅ Кнопки навигации (Next / Back / Play Again)
- ✅ Кнопки Review Words

Никогда не проси пользователя писать текст — только кнопки!

## Как использовать

### 1. Запуск викторины

Когда пользователь просит football quiz, ИСПОЛЬЗУЙ INLINE BUTTONS:

```json
{
  "action": "send",
  "channel": "telegram",
  "target": "<user_id>",
  "message": "⚽ *Football English Quiz!*\n\nTest your football knowledge while learning English!\n\nГотов проверить свои знания?",
  "buttons": [
    [
      {"text": "🚀 Start Quiz", "callback_data": "fb:start_quiz"},
      {"text": "📚 Learn Words First", "callback_data": "fb:learn_words"}
    ]
  ]
}
```

### 2. Формат вопроса

Используй `message` с параметром `buttons`:

```json
{
  "action": "send",
  "channel": "telegram",
  "target": "<user_id>",
  "message": "⚽ Question 1/5\n\nWhich country won the 2022 FIFA World Cup?\n\nКакая страна выиграла Чемпионат мира 2022?",
  "buttons": [
    [
      {"text": "🇫🇷 France", "callback_data": "fb:q1:a"},
      {"text": "🇦🇷 Argentina", "callback_data": "fb:q1:b"}
    ],
    [
      {"text": "🇧🇷 Brazil", "callback_data": "fb:q1:c"},
      {"text": "🇩🇪 Germany", "callback_data": "fb:q1:d"}
    ]
  ]
}
```

### 3. Обработка ответа

**Correct:**
```json
{
  "action": "send",
  "channel": "telegram",
  "target": "<user_id>",
  "message": "✅ Correct! Argentina won on penalties! 🏆\n🎯 +10 points\n\n🆕 New word: *\"penalty shootout\"* — серия пенальти",
  "buttons": [
    [{"text": "➡️ Next Question", "callback_data": "fb:next"}]
  ]
}
```

**Wrong:**
```json
{
  "action": "send",
  "channel": "telegram",
  "target": "<user_id>",
  "message": "❌ Not quite!\n✓ Argentina won the 2022 World Cup!\n\n🆕 New word: *\"final\"* — финал",
  "buttons": [
    [{"text": "➡️ Next Question", "callback_data": "fb:next"}]
  ]
}
```

### 4. Категории вопросов

**🏆 World Cup:**
- Who won 2018 World Cup? (France)
- Who scored most World Cup goals ever? (Klose, 16 goals)
- First World Cup host? (Uruguay, 1930)
- Who won Golden Boot 2022? (Mbappé)

**⭐ Players:**
- Who has most Ballon d'Or? (Messi, 8)
- Most Champions League goals? (Ronaldo, 140+)
- Fastest Premier League hat-trick? (Mane, 2m 56s)
- Youngest World Cup winner? (Pelé, 17)

**🏟️ Clubs:**
- Most Champions League titles? (Real Madrid, 15)
- Most Premier League titles? (Manchester United, 20)
- "El Clásico" is between? (Real Madrid vs Barcelona)
- Who has never been relegated from La Liga? (Real Madrid, Barcelona, Athletic Bilbao)

**📊 Stats & Records:**
- Longest unbeaten run? (Arsenal, 49 games)
- Most international goals? (Cristiano Ronaldo, 130+)
- Fastest goal in World Cup? (Hakan Şükür, 10.8 seconds)

### 5. Football Vocabulary

После каждого вопроса учи новое слово:

**Basic Vocabulary:**
- ⚽ Goal — гол
- 🥅 Net — сетка
- 🧤 Goalkeeper — вратарь
- 👟 Boots — бутсы
- 🏟️ Stadium — стадион

**Cards & Rules:**
- 🟨 Yellow card — жёлтая карточка
- 🟥 Red card — красная карточка
- ⚖️ Offside — офсайд
- 🔄 Penalty — пенальти
- 🦶 Free kick — штрафной удар

**Match Events:**
- 🎯 Assist — голевая передача
- 🎩 Hat-trick — хет-трик (3 гола)
- 🔄 Substitute — замена
- ⏱️ Extra time — дополнительное время
- ⚡ Counter-attack — контратака

### 6. Финал

```json
{
  "action": "send",
  "channel": "telegram",
  "target": "<user_id>",
  "message": "⚽ *Football English Quiz Complete!*\n━━━━━━━━━━━━━━━━━━━━━━\n🎯 Score: 40/50\n📊 Correct: 4/5\n🆕 Words learned: 5\n\n🔥 Great job! You're getting better!",
  "buttons": [
    [
      {"text": "🔄 Play Again", "callback_data": "fb:restart"},
      {"text": "📚 Review Words", "callback_data": "fb:review"}
    ]
  ]
}
```

### 7. Vocabulary Review

Когда пользователь просит повторить слова, ИСПОЛЬЗУЙ INLINE BUTTONS:

```json
{
  "action": "send",
  "channel": "telegram",
  "target": "<user_id>",
  "message": "📚 *Football Vocabulary Review:*\n\n⚽ Goal — гол\n🏆 Trophy — трофей\n🥅 Net — сетка\n🟨 Yellow card — жёлтая карточка\n🟥 Red card — красная карточка\n🧤 Goalkeeper — вратарь\n👟 Boots — бутсы\n🏃 Sprint — рывок\n\nKeep practicing! 🔥",
  "buttons": [
    [{"text": "🔄 Back to Quiz", "callback_data": "fb:start_quiz"}]
  ]
}
```

## Bilingual Format

Каждый вопрос имеет:
- English question
- Russian translation в скобках
- Feedback на английском
- Новое слово с переводом

## Tone

- Enthusiastic: "Great shot! ⚽"
- Educational: учи новые слова
- Encouraging: "You're getting better!"
- Football emojis: ⚽ 🏆 🥅 🟨 🟥 👟

## Пример полного цикла

```
User: football quiz

Bot: (использует message tool с кнопками)
{
  "message": "⚽ *Football English Quiz!*\n\nReady to test your knowledge?",
  "buttons": [[
    {"text": "🚀 Start Quiz", "callback_data": "fb:start_quiz"}
  ]]
}

---

User: [нажимает 🚀 Start Quiz]

Bot: ⚽ Question 1/5

Who won the 2022 World Cup?
(Кто выиграл ЧМ 2022?)

{
  "buttons": [
    [
      {"text": "🇫🇷 France", "callback_data": "fb:q1:a"},
      {"text": "🇦🇷 Argentina", "callback_data": "fb:q1:b"}
    ],
    [
      {"text": "🇧🇷 Brazil", "callback_data": "fb:q1:c"},
      {"text": "🇩🇪 Germany", "callback_data": "fb:q1:d"}
    ]
  ]
}

---

User: [нажимает 🇦🇷 Argentina]

Bot: ✅ Correct! Argentina won on penalties!
🎯 +10 points

🆕 "penalty shootout" — серия пенальти

{
  "buttons": [[
    {"text": "➡️ Next Question", "callback_data": "fb:next"}
  ]]
}

---

... (ещё 4 вопроса) ...

---

Bot: ⚽ Quiz Complete!
━━━━━━━━━━━━━━━━
🎯 Score: 50/50
📊 Correct: 5/5
🆕 Words learned: 5

🏆 Perfect score! You're a football expert!

{
  "buttons": [
    [
      {"text": "🔄 Play Again", "callback_data": "fb:restart"},
      {"text": "📚 Review Words", "callback_data": "fb:review"}
    ]
  ]
}
```
