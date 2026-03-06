# Alexa Skill Development

## Skill Architecture

```
User speaks → Alexa cloud (NLU) → Your skill (intent + slots) → Lambda/Endpoint → Response → Alexa speaks
```

**Skill types:**
- **Custom skills:** Full control, build intents from scratch
- **Smart home skills:** Device control with pre-built intents
- **Flash briefing:** News/content feeds
- **Video/Music skills:** Media playback (complex certification)

---

## Interaction Model

### Intent Design

```json
{
  "intents": [
    {
      "name": "OrderPizzaIntent",
      "slots": [
        { "name": "size", "type": "AMAZON.SizeType" },
        { "name": "topping", "type": "PizzaToppingType" }
      ],
      "samples": [
        "order a {size} pizza with {topping}",
        "I want {topping} pizza",
        "get me a pizza"
      ]
    }
  ]
}
```

**Slot types:**
- Built-in: AMAZON.NUMBER, AMAZON.DATE, AMAZON.City, AMAZON.SearchQuery
- Custom: Define your own values + synonyms

**Sample utterances:**
- Minimum 10-20 per intent for good recognition
- Include variations: formal/casual, with/without slots
- Test with real users — they say things you don't expect

### Required Intents (Certification)

| Intent | Purpose | Example Response |
|--------|---------|------------------|
| AMAZON.HelpIntent | Explain skill | "You can ask me to order pizza, check your order status, or..." |
| AMAZON.StopIntent | Exit cleanly | "Goodbye!" |
| AMAZON.CancelIntent | Exit cleanly | Same as Stop |
| AMAZON.FallbackIntent | Unrecognized input | "I didn't catch that. Try saying 'order a pizza'." |
| LaunchRequest | Skill opened without command | Welcome message + what they can do |

---

## Lambda Function (Node.js)

```javascript
const Alexa = require('ask-sdk-core');

const LaunchHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'LaunchRequest';
  },
  handle(handlerInput) {
    return handlerInput.responseBuilder
      .speak('Welcome to Pizza Order. What would you like?')
      .reprompt('You can say "order a large pepperoni pizza".')
      .getResponse();
  }
};

const OrderPizzaHandler = {
  canHandle(handlerInput) {
    return Alexa.getRequestType(handlerInput.requestEnvelope) === 'IntentRequest'
      && Alexa.getIntentName(handlerInput.requestEnvelope) === 'OrderPizzaIntent';
  },
  handle(handlerInput) {
    const slots = handlerInput.requestEnvelope.request.intent.slots;
    const size = slots.size?.value || 'medium';
    const topping = slots.topping?.value || 'cheese';
    
    return handlerInput.responseBuilder
      .speak(`Ordering a ${size} ${topping} pizza. Is that correct?`)
      .reprompt('Say yes to confirm or no to cancel.')
      .getResponse();
  }
};

exports.handler = Alexa.SkillBuilders.custom()
  .addRequestHandlers(LaunchHandler, OrderPizzaHandler)
  .lambda();
```

**Handler chain:** First handler where `canHandle` returns true wins.

---

## Session & State Management

**Session attributes (within session):**
```javascript
const sessionAttributes = handlerInput.attributesManager.getSessionAttributes();
sessionAttributes.orderSize = 'large';
handlerInput.attributesManager.setSessionAttributes(sessionAttributes);
```

**Persistent attributes (DynamoDB):**
```javascript
const persistentAttributes = await handlerInput.attributesManager.getPersistentAttributes();
persistentAttributes.orderHistory = [...];
handlerInput.attributesManager.setPersistentAttributes(persistentAttributes);
await handlerInput.attributesManager.savePersistentAttributes();
```

---

## Testing

**Alexa Developer Console:**
1. Go to Test tab
2. Enable "Development" testing
3. Type or speak utterances
4. Check JSON Input/Output for debugging

**Physical device testing (critical):**
- Enable skill on your account
- Test with actual voice (mumbling, accents, background noise)
- Test on different Echo devices (Show vs Dot)

**Common test cases:**
- [ ] Launch without command (LaunchRequest)
- [ ] Direct command ("Alexa, ask [skill] to [action]")
- [ ] All slots filled vs partial vs empty
- [ ] Help, Stop, Cancel work
- [ ] Session timeout (8 seconds silence)
- [ ] Error handling (Lambda timeout, API failure)

---

## Certification Checklist

Before submitting:

- [ ] All required intents implemented
- [ ] Help intent describes all features
- [ ] No placeholder or test content
- [ ] Privacy policy URL (if collecting data)
- [ ] Testing instructions for reviewer
- [ ] Skill icon 108x108 and 512x512 PNG
- [ ] Example phrases (3) that actually work
- [ ] No trademark issues in skill name

**Common rejection reasons:**
- Example phrases don't work exactly as written
- Help intent is generic ("I can help you")
- Skill name conflicts with existing skill or trademark
- Missing privacy policy for data collection
- Broken functionality in edge cases

---

## Account Linking (OAuth)

For skills that need user accounts:

1. Configure OAuth provider in skill settings
2. User links account in Alexa app
3. Access token available in `handlerInput.requestEnvelope.context.System.user.accessToken`

**Flow:**
1. User enables skill → redirected to your OAuth login
2. User logs in → you redirect back to Amazon with auth code
3. Amazon exchanges code for tokens → stores for user
4. Your Lambda receives access token with each request

---

## Publishing

**Distribution options:**
- Public: Available to all Alexa users
- Beta: Up to 500 testers via email
- Private (Organizations): Enterprise deployment

**Post-launch:**
- Monitor CloudWatch for errors
- Check skill analytics in developer console
- Respond to voice feedback (users can leave reviews)
- Update regularly — stale skills get deprioritized
