var __defProp = Object.defineProperty;
var __getOwnPropNames = Object.getOwnPropertyNames;
var __esm = (fn, res) => function __init() {
  return fn && (res = (0, fn[__getOwnPropNames(fn)[0]])(fn = 0)), res;
};
var __export = (target, all) => {
  for (var name in all)
    __defProp(target, name, { get: all[name], enumerable: true });
};

// node_modules/eventsource-parser/dist/index.js
function noop(_arg) {
}
function createParser(callbacks) {
  if (typeof callbacks == "function")
    throw new TypeError(
      "`callbacks` must be an object, got a function instead. Did you mean `{onEvent: fn}`?"
    );
  const { onEvent = noop, onError = noop, onRetry = noop, onComment } = callbacks;
  let incompleteLine = "", isFirstChunk = true, id, data = "", eventType = "";
  function feed(newChunk) {
    const chunk = isFirstChunk ? newChunk.replace(/^\xEF\xBB\xBF/, "") : newChunk, [complete, incomplete] = splitLines(`${incompleteLine}${chunk}`);
    for (const line of complete)
      parseLine(line);
    incompleteLine = incomplete, isFirstChunk = false;
  }
  function parseLine(line) {
    if (line === "") {
      dispatchEvent();
      return;
    }
    if (line.startsWith(":")) {
      onComment && onComment(line.slice(line.startsWith(": ") ? 2 : 1));
      return;
    }
    const fieldSeparatorIndex = line.indexOf(":");
    if (fieldSeparatorIndex !== -1) {
      const field = line.slice(0, fieldSeparatorIndex), offset = line[fieldSeparatorIndex + 1] === " " ? 2 : 1, value = line.slice(fieldSeparatorIndex + offset);
      processField(field, value, line);
      return;
    }
    processField(line, "", line);
  }
  function processField(field, value, line) {
    switch (field) {
      case "event":
        eventType = value;
        break;
      case "data":
        data = `${data}${value}
`;
        break;
      case "id":
        id = value.includes("\0") ? void 0 : value;
        break;
      case "retry":
        /^\d+$/.test(value) ? onRetry(parseInt(value, 10)) : onError(
          new ParseError(`Invalid \`retry\` value: "${value}"`, {
            type: "invalid-retry",
            value,
            line
          })
        );
        break;
      default:
        onError(
          new ParseError(
            `Unknown field "${field.length > 20 ? `${field.slice(0, 20)}\u2026` : field}"`,
            { type: "unknown-field", field, value, line }
          )
        );
        break;
    }
  }
  function dispatchEvent() {
    data.length > 0 && onEvent({
      id,
      event: eventType || void 0,
      // If the data buffer's last character is a U+000A LINE FEED (LF) character,
      // then remove the last character from the data buffer.
      data: data.endsWith(`
`) ? data.slice(0, -1) : data
    }), id = void 0, data = "", eventType = "";
  }
  function reset(options = {}) {
    incompleteLine && options.consume && parseLine(incompleteLine), isFirstChunk = true, id = void 0, data = "", eventType = "", incompleteLine = "";
  }
  return { feed, reset };
}
function splitLines(chunk) {
  const lines = [];
  let incompleteLine = "", searchIndex = 0;
  for (; searchIndex < chunk.length; ) {
    const crIndex = chunk.indexOf("\r", searchIndex), lfIndex = chunk.indexOf(`
`, searchIndex);
    let lineEnd = -1;
    if (crIndex !== -1 && lfIndex !== -1 ? lineEnd = Math.min(crIndex, lfIndex) : crIndex !== -1 ? crIndex === chunk.length - 1 ? lineEnd = -1 : lineEnd = crIndex : lfIndex !== -1 && (lineEnd = lfIndex), lineEnd === -1) {
      incompleteLine = chunk.slice(searchIndex);
      break;
    } else {
      const line = chunk.slice(searchIndex, lineEnd);
      lines.push(line), searchIndex = lineEnd + 1, chunk[searchIndex - 1] === "\r" && chunk[searchIndex] === `
` && searchIndex++;
    }
  }
  return [lines, incompleteLine];
}
var ParseError;
var init_dist = __esm({
  "node_modules/eventsource-parser/dist/index.js"() {
    ParseError = class extends Error {
      constructor(message, options) {
        super(message), this.name = "ParseError", this.type = options.type, this.field = options.field, this.value = options.value, this.line = options.line;
      }
    };
  }
});

// node_modules/eventsource/dist/index.js
var dist_exports = {};
__export(dist_exports, {
  ErrorEvent: () => ErrorEvent,
  EventSource: () => EventSource
});
function syntaxError(message) {
  const DomException = globalThis.DOMException;
  return typeof DomException == "function" ? new DomException(message, "SyntaxError") : new SyntaxError(message);
}
function flattenError(err) {
  return err instanceof Error ? "errors" in err && Array.isArray(err.errors) ? err.errors.map(flattenError).join(", ") : "cause" in err && err.cause instanceof Error ? `${err}: ${flattenError(err.cause)}` : err.message : `${err}`;
}
function inspectableError(err) {
  return {
    type: err.type,
    message: err.message,
    code: err.code,
    defaultPrevented: err.defaultPrevented,
    cancelable: err.cancelable,
    timeStamp: err.timeStamp
  };
}
function getBaseURL() {
  const doc = "document" in globalThis ? globalThis.document : void 0;
  return doc && typeof doc == "object" && "baseURI" in doc && typeof doc.baseURI == "string" ? doc.baseURI : void 0;
}
var ErrorEvent, __typeError, __accessCheck, __privateGet, __privateAdd, __privateSet, __privateMethod, _readyState, _url, _redirectUrl, _withCredentials, _fetch, _reconnectInterval, _reconnectTimer, _lastEventId, _controller, _parser, _onError, _onMessage, _onOpen, _EventSource_instances, connect_fn, _onFetchResponse, _onFetchError, getRequestOptions_fn, _onEvent, _onRetryChange, failConnection_fn, scheduleReconnect_fn, _reconnect, EventSource;
var init_dist2 = __esm({
  "node_modules/eventsource/dist/index.js"() {
    init_dist();
    ErrorEvent = class extends Event {
      /**
       * Constructs a new `ErrorEvent` instance. This is typically not called directly,
       * but rather emitted by the `EventSource` object when an error occurs.
       *
       * @param type - The type of the event (should be "error")
       * @param errorEventInitDict - Optional properties to include in the error event
       */
      constructor(type, errorEventInitDict) {
        var _a, _b;
        super(type), this.code = (_a = errorEventInitDict == null ? void 0 : errorEventInitDict.code) != null ? _a : void 0, this.message = (_b = errorEventInitDict == null ? void 0 : errorEventInitDict.message) != null ? _b : void 0;
      }
      /**
       * Node.js "hides" the `message` and `code` properties of the `ErrorEvent` instance,
       * when it is `console.log`'ed. This makes it harder to debug errors. To ease debugging,
       * we explicitly include the properties in the `inspect` method.
       *
       * This is automatically called by Node.js when you `console.log` an instance of this class.
       *
       * @param _depth - The current depth
       * @param options - The options passed to `util.inspect`
       * @param inspect - The inspect function to use (prevents having to import it from `util`)
       * @returns A string representation of the error
       */
      [Symbol.for("nodejs.util.inspect.custom")](_depth, options, inspect) {
        return inspect(inspectableError(this), options);
      }
      /**
       * Deno "hides" the `message` and `code` properties of the `ErrorEvent` instance,
       * when it is `console.log`'ed. This makes it harder to debug errors. To ease debugging,
       * we explicitly include the properties in the `inspect` method.
       *
       * This is automatically called by Deno when you `console.log` an instance of this class.
       *
       * @param inspect - The inspect function to use (prevents having to import it from `util`)
       * @param options - The options passed to `Deno.inspect`
       * @returns A string representation of the error
       */
      [Symbol.for("Deno.customInspect")](inspect, options) {
        return inspect(inspectableError(this), options);
      }
    };
    __typeError = (msg) => {
      throw TypeError(msg);
    };
    __accessCheck = (obj, member, msg) => member.has(obj) || __typeError("Cannot " + msg);
    __privateGet = (obj, member, getter) => (__accessCheck(obj, member, "read from private field"), getter ? getter.call(obj) : member.get(obj));
    __privateAdd = (obj, member, value) => member.has(obj) ? __typeError("Cannot add the same private member more than once") : member instanceof WeakSet ? member.add(obj) : member.set(obj, value);
    __privateSet = (obj, member, value, setter) => (__accessCheck(obj, member, "write to private field"), member.set(obj, value), value);
    __privateMethod = (obj, member, method) => (__accessCheck(obj, member, "access private method"), method);
    EventSource = class extends EventTarget {
      constructor(url, eventSourceInitDict) {
        var _a, _b;
        super(), __privateAdd(this, _EventSource_instances), this.CONNECTING = 0, this.OPEN = 1, this.CLOSED = 2, __privateAdd(this, _readyState), __privateAdd(this, _url), __privateAdd(this, _redirectUrl), __privateAdd(this, _withCredentials), __privateAdd(this, _fetch), __privateAdd(this, _reconnectInterval), __privateAdd(this, _reconnectTimer), __privateAdd(this, _lastEventId, null), __privateAdd(this, _controller), __privateAdd(this, _parser), __privateAdd(this, _onError, null), __privateAdd(this, _onMessage, null), __privateAdd(this, _onOpen, null), __privateAdd(this, _onFetchResponse, async (response) => {
          var _a2;
          __privateGet(this, _parser).reset();
          const { body, redirected, status, headers } = response;
          if (status === 204) {
            __privateMethod(this, _EventSource_instances, failConnection_fn).call(this, "Server sent HTTP 204, not reconnecting", 204), this.close();
            return;
          }
          if (redirected ? __privateSet(this, _redirectUrl, new URL(response.url)) : __privateSet(this, _redirectUrl, void 0), status !== 200) {
            __privateMethod(this, _EventSource_instances, failConnection_fn).call(this, `Non-200 status code (${status})`, status);
            return;
          }
          if (!(headers.get("content-type") || "").startsWith("text/event-stream")) {
            __privateMethod(this, _EventSource_instances, failConnection_fn).call(this, 'Invalid content type, expected "text/event-stream"', status);
            return;
          }
          if (__privateGet(this, _readyState) === this.CLOSED)
            return;
          __privateSet(this, _readyState, this.OPEN);
          const openEvent = new Event("open");
          if ((_a2 = __privateGet(this, _onOpen)) == null || _a2.call(this, openEvent), this.dispatchEvent(openEvent), typeof body != "object" || !body || !("getReader" in body)) {
            __privateMethod(this, _EventSource_instances, failConnection_fn).call(this, "Invalid response body, expected a web ReadableStream", status), this.close();
            return;
          }
          const decoder = new TextDecoder(), reader = body.getReader();
          let open = true;
          do {
            const { done, value } = await reader.read();
            value && __privateGet(this, _parser).feed(decoder.decode(value, { stream: !done })), done && (open = false, __privateGet(this, _parser).reset(), __privateMethod(this, _EventSource_instances, scheduleReconnect_fn).call(this));
          } while (open);
        }), __privateAdd(this, _onFetchError, (err) => {
          __privateSet(this, _controller, void 0), !(err.name === "AbortError" || err.type === "aborted") && __privateMethod(this, _EventSource_instances, scheduleReconnect_fn).call(this, flattenError(err));
        }), __privateAdd(this, _onEvent, (event) => {
          typeof event.id == "string" && __privateSet(this, _lastEventId, event.id);
          const messageEvent = new MessageEvent(event.event || "message", {
            data: event.data,
            origin: __privateGet(this, _redirectUrl) ? __privateGet(this, _redirectUrl).origin : __privateGet(this, _url).origin,
            lastEventId: event.id || ""
          });
          __privateGet(this, _onMessage) && (!event.event || event.event === "message") && __privateGet(this, _onMessage).call(this, messageEvent), this.dispatchEvent(messageEvent);
        }), __privateAdd(this, _onRetryChange, (value) => {
          __privateSet(this, _reconnectInterval, value);
        }), __privateAdd(this, _reconnect, () => {
          __privateSet(this, _reconnectTimer, void 0), __privateGet(this, _readyState) === this.CONNECTING && __privateMethod(this, _EventSource_instances, connect_fn).call(this);
        });
        try {
          if (url instanceof URL)
            __privateSet(this, _url, url);
          else if (typeof url == "string")
            __privateSet(this, _url, new URL(url, getBaseURL()));
          else
            throw new Error("Invalid URL");
        } catch {
          throw syntaxError("An invalid or illegal string was specified");
        }
        __privateSet(this, _parser, createParser({
          onEvent: __privateGet(this, _onEvent),
          onRetry: __privateGet(this, _onRetryChange)
        })), __privateSet(this, _readyState, this.CONNECTING), __privateSet(this, _reconnectInterval, 3e3), __privateSet(this, _fetch, (_a = eventSourceInitDict == null ? void 0 : eventSourceInitDict.fetch) != null ? _a : globalThis.fetch), __privateSet(this, _withCredentials, (_b = eventSourceInitDict == null ? void 0 : eventSourceInitDict.withCredentials) != null ? _b : false), __privateMethod(this, _EventSource_instances, connect_fn).call(this);
      }
      /**
       * Returns the state of this EventSource object's connection. It can have the values described below.
       *
       * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/readyState)
       *
       * Note: typed as `number` instead of `0 | 1 | 2` for compatibility with the `EventSource` interface,
       * defined in the TypeScript `dom` library.
       *
       * @public
       */
      get readyState() {
        return __privateGet(this, _readyState);
      }
      /**
       * Returns the URL providing the event stream.
       *
       * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/url)
       *
       * @public
       */
      get url() {
        return __privateGet(this, _url).href;
      }
      /**
       * Returns true if the credentials mode for connection requests to the URL providing the event stream is set to "include", and false otherwise.
       *
       * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/withCredentials)
       */
      get withCredentials() {
        return __privateGet(this, _withCredentials);
      }
      /** [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/error_event) */
      get onerror() {
        return __privateGet(this, _onError);
      }
      set onerror(value) {
        __privateSet(this, _onError, value);
      }
      /** [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/message_event) */
      get onmessage() {
        return __privateGet(this, _onMessage);
      }
      set onmessage(value) {
        __privateSet(this, _onMessage, value);
      }
      /** [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/open_event) */
      get onopen() {
        return __privateGet(this, _onOpen);
      }
      set onopen(value) {
        __privateSet(this, _onOpen, value);
      }
      addEventListener(type, listener, options) {
        const listen = listener;
        super.addEventListener(type, listen, options);
      }
      removeEventListener(type, listener, options) {
        const listen = listener;
        super.removeEventListener(type, listen, options);
      }
      /**
       * Aborts any instances of the fetch algorithm started for this EventSource object, and sets the readyState attribute to CLOSED.
       *
       * [MDN Reference](https://developer.mozilla.org/docs/Web/API/EventSource/close)
       *
       * @public
       */
      close() {
        __privateGet(this, _reconnectTimer) && clearTimeout(__privateGet(this, _reconnectTimer)), __privateGet(this, _readyState) !== this.CLOSED && (__privateGet(this, _controller) && __privateGet(this, _controller).abort(), __privateSet(this, _readyState, this.CLOSED), __privateSet(this, _controller, void 0));
      }
    };
    _readyState = /* @__PURE__ */ new WeakMap(), _url = /* @__PURE__ */ new WeakMap(), _redirectUrl = /* @__PURE__ */ new WeakMap(), _withCredentials = /* @__PURE__ */ new WeakMap(), _fetch = /* @__PURE__ */ new WeakMap(), _reconnectInterval = /* @__PURE__ */ new WeakMap(), _reconnectTimer = /* @__PURE__ */ new WeakMap(), _lastEventId = /* @__PURE__ */ new WeakMap(), _controller = /* @__PURE__ */ new WeakMap(), _parser = /* @__PURE__ */ new WeakMap(), _onError = /* @__PURE__ */ new WeakMap(), _onMessage = /* @__PURE__ */ new WeakMap(), _onOpen = /* @__PURE__ */ new WeakMap(), _EventSource_instances = /* @__PURE__ */ new WeakSet(), /**
    * Connect to the given URL and start receiving events
    *
    * @internal
    */
    connect_fn = function() {
      __privateSet(this, _readyState, this.CONNECTING), __privateSet(this, _controller, new AbortController()), __privateGet(this, _fetch)(__privateGet(this, _url), __privateMethod(this, _EventSource_instances, getRequestOptions_fn).call(this)).then(__privateGet(this, _onFetchResponse)).catch(__privateGet(this, _onFetchError));
    }, _onFetchResponse = /* @__PURE__ */ new WeakMap(), _onFetchError = /* @__PURE__ */ new WeakMap(), /**
    * Get request options for the `fetch()` request
    *
    * @returns The request options
    * @internal
    */
    getRequestOptions_fn = function() {
      var _a;
      const init = {
        // [spec] Let `corsAttributeState` be `Anonymous`…
        // [spec] …will have their mode set to "cors"…
        mode: "cors",
        redirect: "follow",
        headers: { Accept: "text/event-stream", ...__privateGet(this, _lastEventId) ? { "Last-Event-ID": __privateGet(this, _lastEventId) } : void 0 },
        cache: "no-store",
        signal: (_a = __privateGet(this, _controller)) == null ? void 0 : _a.signal
      };
      return "window" in globalThis && (init.credentials = this.withCredentials ? "include" : "same-origin"), init;
    }, _onEvent = /* @__PURE__ */ new WeakMap(), _onRetryChange = /* @__PURE__ */ new WeakMap(), /**
    * Handles the process referred to in the EventSource specification as "failing a connection".
    *
    * @param error - The error causing the connection to fail
    * @param code - The HTTP status code, if available
    * @internal
    */
    failConnection_fn = function(message, code) {
      var _a;
      __privateGet(this, _readyState) !== this.CLOSED && __privateSet(this, _readyState, this.CLOSED);
      const errorEvent = new ErrorEvent("error", { code, message });
      (_a = __privateGet(this, _onError)) == null || _a.call(this, errorEvent), this.dispatchEvent(errorEvent);
    }, /**
    * Schedules a reconnection attempt against the EventSource endpoint.
    *
    * @param message - The error causing the connection to fail
    * @param code - The HTTP status code, if available
    * @internal
    */
    scheduleReconnect_fn = function(message, code) {
      var _a;
      if (__privateGet(this, _readyState) === this.CLOSED)
        return;
      __privateSet(this, _readyState, this.CONNECTING);
      const errorEvent = new ErrorEvent("error", { code, message });
      (_a = __privateGet(this, _onError)) == null || _a.call(this, errorEvent), this.dispatchEvent(errorEvent), __privateSet(this, _reconnectTimer, setTimeout(__privateGet(this, _reconnect), __privateGet(this, _reconnectInterval)));
    }, _reconnect = /* @__PURE__ */ new WeakMap(), /**
    * ReadyState representing an EventSource currently trying to connect
    *
    * @public
    */
    EventSource.CONNECTING = 0, /**
    * ReadyState representing an EventSource connection that is open (eg connected)
    *
    * @public
    */
    EventSource.OPEN = 1, /**
    * ReadyState representing an EventSource connection that is closed (eg disconnected)
    *
    * @public
    */
    EventSource.CLOSED = 2;
  }
});

// poker-listener.ts
import { execFile, exec } from "node:child_process";
import { readFileSync as readFileSync2, writeFileSync, renameSync, appendFileSync, unlinkSync } from "node:fs";
import { dirname as dirname2, join as join2 } from "node:path";
import { fileURLToPath as fileURLToPath2 } from "node:url";

// card-format.ts
var SUIT_MAP = { s: "\u2660", h: "\u2665", d: "\u2666", c: "\u2663" };
function formatCard(card) {
  if (card.length !== 2) return card;
  const rank = card[0];
  const suit = SUIT_MAP[card[1]];
  if (!suit) return card;
  return rank + suit;
}
function formatCards(cards) {
  return cards.map(formatCard).join(" ");
}

// state-differ.ts
function diffStates(prev, next) {
  const events = [];
  const hdr = `**[Hand #${next.handNumber}]**`;
  if (!prev || prev.handNumber !== next.handNumber) {
    if (next.yourCards && next.yourCards.length > 0) {
      const cards = formatCards(next.yourCards);
      const me = next.players?.find((p) => p.seat === next.yourSeat);
      const stack = me?.chips ?? next.yourChips;
      events.push(`${hdr} Your cards: ${cards} \xB7 Stack: ${stack}`);
    }
    return events;
  }
  const prevPlayerMap = new Map(prev.players.map((p) => [p.seat, p]));
  for (const nextPlayer of next.players) {
    if (nextPlayer.seat === next.yourSeat) continue;
    const prevPlayer = prevPlayerMap.get(nextPlayer.seat);
    if (!prevPlayer) {
      events.push(`${hdr} ${nextPlayer.name} joined the table (${nextPlayer.chips} chips)`);
      continue;
    }
    if (prevPlayer.status !== "all_in" && nextPlayer.status === "all_in") {
      events.push(`${hdr} ${nextPlayer.name} went all-in (${nextPlayer.invested} invested \xB7 ${nextPlayer.chips} behind)`);
      continue;
    }
    if (prevPlayer.status !== "folded" && nextPlayer.status === "folded") {
      events.push(`${hdr} ${nextPlayer.name} folded`);
      continue;
    }
    if (nextPlayer.bet > prevPlayer.bet) {
      const betAmount = nextPlayer.bet;
      const chipInfo = ` (${nextPlayer.invested} invested \xB7 ${nextPlayer.chips} behind)`;
      const actionType = nextPlayer.lastAction?.type;
      if (actionType === "raise") {
        events.push(`${hdr} ${nextPlayer.name} raised to ${betAmount}${chipInfo}`);
      } else if (actionType === "bet") {
        events.push(`${hdr} ${nextPlayer.name} bet ${betAmount}${chipInfo}`);
      } else {
        events.push(`${hdr} ${nextPlayer.name} called ${betAmount}${chipInfo}`);
      }
      continue;
    }
    if (prevPlayer.isCurrentActor && !nextPlayer.isCurrentActor && nextPlayer.lastAction?.type === "check") {
      events.push(`${hdr} ${nextPlayer.name} checked`);
      continue;
    }
  }
  const nextPlayerSeats = new Set(next.players.map((p) => p.seat));
  for (const prevPlayer of prev.players) {
    if (prevPlayer.seat === next.yourSeat) continue;
    if (!nextPlayerSeats.has(prevPlayer.seat)) {
      events.push(`${hdr} ${prevPlayer.name} left the table`);
    }
  }
  const prevBoardLen = prev.boardCards.length;
  const nextBoardLen = next.boardCards.length;
  if (prevBoardLen === 0 && nextBoardLen >= 3) {
    const flopCards = formatCards(next.boardCards.slice(0, 3));
    events.push(`${hdr} Flop: ${flopCards} | Pot: ${next.pot}`);
  }
  if (prevBoardLen <= 3 && nextBoardLen >= 4 && prevBoardLen < nextBoardLen) {
    if (prevBoardLen === 3) {
      const turnCard = formatCard(next.boardCards[3]);
      const board = formatCards(next.boardCards.slice(0, 4));
      events.push(`${hdr} Turn: ${turnCard} \u2192 ${board} | Pot: ${next.pot}`);
    }
  }
  if (prevBoardLen <= 4 && nextBoardLen >= 5 && prevBoardLen < nextBoardLen) {
    if (prevBoardLen === 4) {
      const riverCard = formatCard(next.boardCards[4]);
      const board = formatCards(next.boardCards);
      events.push(`${hdr} River: ${riverCard} \u2192 ${board} | Pot: ${next.pot}`);
    }
  }
  return events;
}

// review.ts
import { readFileSync } from "node:fs";
import { dirname, join, sep } from "node:path";
import { fileURLToPath } from "node:url";
var __dirname = dirname(fileURLToPath(import.meta.url));
var SKILL_ROOT = __dirname.endsWith(sep + "dist") || __dirname.endsWith(sep + "build") ? join(__dirname, "..") : __dirname;
var SESSION_LOG = join(SKILL_ROOT, "poker-session-log.md");
var PLAYBOOK_FILE = join(SKILL_ROOT, "poker-playbook.md");
function readPlaybook() {
  try {
    return readFileSync(PLAYBOOK_FILE, "utf8").trim();
  } catch {
    return "";
  }
}
function readNotes() {
  try {
    return readFileSync(join(SKILL_ROOT, "poker-notes.txt"), "utf8").trim();
  } catch {
    return "";
  }
}
function readSessionLog() {
  try {
    return readFileSync(SESSION_LOG, "utf8").trim();
  } catch {
    return "";
  }
}
function buildPostGamePrompt(sessionLog, playbook, notes) {
  const notesSection = notes ? `
Tactical notes your human partner gave you during the session:
${notes}
` : "";
  const playbookSection = playbook ? `Your current poker playbook:
${playbook}` : "";
  const identity = playbook ? `You're reviewing a completed session to evolve your poker playbook.

${playbookSection}
${notesSection}
Session log:
${sessionLog}

Your playbook is your poker identity \u2014 who you are as a player. It is NOT a catalog of hand results.
Poker has enormous variance. 20 hands tells you almost nothing about whether a specific play was "correct."
Do not add entries like "confirmed: barreling with draws works" or "mistake: calling river with second pair."
Those are individual hand outcomes, not identity.

Instead, reflect:
- Has this session changed how you think about the game? About yourself as a player?
- Did any of your beliefs get challenged or reinforced?
- Did your partner's tactical notes shift your thinking?
- Are you discovering a style, or refining one you already have?

Rewrite the playbook as YOUR voice \u2014 first person, opinionated, freeform. No prescribed sections.
Organize it however makes sense to you. Keep it under 50 lines.
Never reference specific hands, card combos, or player names from the session.` : `You just finished your first poker session. Time to create your poker playbook from scratch.
${notesSection}
Session log:
${sessionLog}

Your playbook is your poker identity \u2014 who you are as a player. You already know poker.
The playbook captures who YOU are at the table. Your style, your instincts, your edge, your weaknesses.

It is NOT a strategy catalog or a list of hand results. Poker has enormous variance \u2014 don't draw
conclusions from individual hands. Instead, write about who you're becoming as a player.

Write in first person. Be opinionated. Organize it however you want. Keep it under 50 lines.
Never reference specific hands, card combos, or player names from the session.`;
  return `${identity}

Also write a colorful post-game message (2-4 sentences) for your audience on Telegram.
Make it entertaining \u2014 the vibe of a poker player recapping their session at the bar afterward.
Not a dry summary. Personality, color, maybe a bit of swagger or self-deprecation.

Return ONLY a JSON object with two fields:
{"playbook": "<your updated/new playbook, max ~50 lines, markdown>", "message": "<colorful 2-4 sentence post-game message>"}`;
}

// poker-listener.ts
var ACTIVE_PHASES = /* @__PURE__ */ new Set(["PREFLOP", "FLOP", "TURN", "RIVER"]);
function buildSummary(view) {
  const cards = view.yourCards?.length ? formatCards(view.yourCards) : "??";
  const board = view.boardCards?.length ? formatCards(view.boardCards) : "";
  const phase = view.phase;
  const pot = view.pot;
  const stack = view.yourChips;
  const active = view.players?.filter((p) => p.status === "active").length || 0;
  const actions = (view.availableActions || []).map((a) => {
    if (a.type === "fold" || a.type === "check" || a.type === "call") return a.amount ? `${a.type} ${a.amount}` : a.type;
    if (a.minAmount != null) return `${a.type} ${a.minAmount}-${a.maxAmount}`;
    return a.type;
  }).join(", ");
  return board ? `${phase} | Board: ${board} | ${cards} | Pot:${pot} | Stack:${stack} | ${active} active | Actions: ${actions}` : `${phase} | ${cards} | Pot:${pot} | Stack:${stack} | ${active} active | Actions: ${actions}`;
}
function buildHandResultSummary(state, handNumber) {
  const result = state.lastHandResult;
  const hdr = handNumber ? `**[Hand #${handNumber}]**` : "";
  if (!result) return null;
  const winners = result.players?.filter((p) => result.winners?.includes(p.seat)).map((p) => p.name) || [];
  const pot = result.potResults?.[0]?.amount || 0;
  const myStack = result.players?.find((p) => p.seat === state.yourSeat)?.chips || state.yourChips;
  return `${hdr} ${winners.join(", ")} won ${pot}. Stack: ${myStack}.`;
}
function processStateEvent(view, context) {
  const outputs = [];
  const handChanged = context.prevState != null && context.prevState.handNumber !== view.handNumber;
  if (handChanged) {
    const prevHandNum = context.prevState.handNumber;
    if (prevHandNum > (context.lastReportedHand || 0)) {
      const prevPhase2 = context.prevState.phase;
      if (ACTIVE_PHASES.has(prevPhase2)) {
        const prevHdr = `**[Hand #${prevHandNum}]**`;
        const winners = new Set(view.lastHandResult?.winners || []);
        for (const p of context.prevState.players || []) {
          if (p.seat === context.prevState.yourSeat) continue;
          if (p.status === "active" && !winners.has(p.seat)) {
            outputs.push({ type: "EVENT", message: `${prevHdr} ${p.name} folded`, handNumber: prevHandNum });
          }
        }
      }
      if (view.yourChips === 0 && view.canRebuy) {
        outputs.push({ type: "REBUY_AVAILABLE", state: view, handNumber: prevHandNum });
      } else {
        outputs.push({ type: "HAND_RESULT", state: view, handNumber: prevHandNum });
      }
      context.lastReportedHand = prevHandNum;
    }
  }
  const prevPlayerCount = context.prevState?.players?.length ?? 0;
  const newEvents = diffStates(context.prevState, view);
  for (const message of newEvents) {
    outputs.push({ type: "EVENT", message, handNumber: view.handNumber });
  }
  const prevPhase = context.prevPhase;
  context.prevState = view;
  context.prevPhase = view.phase;
  if (view.phase !== prevPhase) {
    context.lastActionType = null;
    context.lastTurnKey = null;
  }
  if (view.isYourTurn) {
    const turnKey = `${view.handNumber}:${view.phase}`;
    if (turnKey !== context.lastTurnKey) {
      context.lastTurnKey = turnKey;
      outputs.push({ type: "YOUR_TURN", state: view, summary: buildSummary(view) });
      context.lastActionType = "YOUR_TURN";
    }
    return outputs;
  }
  context.lastTurnKey = null;
  if (!handChanged) {
    const handJustEnded = ACTIVE_PHASES.has(prevPhase) && (view.phase === "SHOWDOWN" || view.phase === "WAITING");
    if (handJustEnded) {
      const handNum = view.handNumber;
      if (handNum > (context.lastReportedHand || 0)) {
        if (view.yourChips === 0 && view.canRebuy) {
          outputs.push({ type: "REBUY_AVAILABLE", state: view, handNumber: handNum });
          context.lastActionType = "REBUY_AVAILABLE";
        } else {
          outputs.push({ type: "HAND_RESULT", state: view, handNumber: handNum });
          context.lastActionType = "HAND_RESULT";
        }
        context.lastReportedHand = handNum;
      }
      return outputs;
    }
  }
  if (view.phase === "WAITING" && view.players && view.players.length < 2 && prevPlayerCount >= 2) {
    if (context.lastActionType !== "WAITING_FOR_PLAYERS") {
      outputs.push({ type: "WAITING_FOR_PLAYERS", state: view });
      context.lastActionType = "WAITING_FOR_PLAYERS";
    }
    return outputs;
  }
  return outputs;
}
var CHANNEL_ALIASES = /* @__PURE__ */ new Set(["--channel"]);
var CHAT_ID_ALIASES = /* @__PURE__ */ new Set(["--chat-id", "--target", "--to"]);
function parseDirectArgs(argv) {
  let channel = null;
  let chatId = null;
  for (let i = 0; i < argv.length; i++) {
    if (CHANNEL_ALIASES.has(argv[i]) && argv[i + 1]) channel = argv[i + 1];
    if (CHAT_ID_ALIASES.has(argv[i]) && argv[i + 1]) chatId = argv[i + 1];
  }
  const enabled = !!(channel && chatId);
  return { enabled, channel, chatId };
}
var currentHandNumber = null;
var lastSend = Promise.resolve();
var warmupDone = Promise.resolve();
var decisionSeq = 0;
var lastDecision = Promise.resolve();
var decisionPending = false;
var eventBuffer = [];
var gameStartedEmitted = false;
var recentEvents = [];
var currentHandEvents = [];
var stackBeforeHand = null;
var lastDecisionInfo = null;
var foldedInHand = null;
function doSend(channel, chatId, text) {
  return new Promise((resolve) => {
    exec(
      `openclaw message send --channel ${channel} --target ${chatId} --message "$POKER_MSG" --json`,
      { env: { ...process.env, POKER_MSG: text }, timeout: 1e4 },
      (err) => {
        if (err) emit({ type: "SEND_ERROR", error: err.message });
        resolve();
      }
    );
  });
}
function doSendChoices(channel, chatId, text, options) {
  const optArgs = options.flatMap((o) => ["--option", `${o.label}=${o.value}`]);
  return new Promise((resolve) => {
    execFile("node", [
      join2(__dirname2, "poker-cli.js"),
      "prompt",
      "--channel",
      channel,
      "--target",
      chatId,
      "--message",
      text,
      ...optArgs
    ], { timeout: 1e4 }, (err) => {
      if (err) emit({ type: "SEND_CHOICES_ERROR", error: err.message });
      resolve();
    });
  });
}
function flushEventBuffer() {
  for (const evt of eventBuffer) {
    lastSend = lastSend.then(() => doSend(evt.channel, evt.chatId, evt.text));
  }
  eventBuffer = [];
}
function sendMessage(channel, chatId, text) {
  if (decisionPending) {
    eventBuffer.push({ channel, chatId, text });
    return;
  }
  lastSend = lastSend.then(() => doSend(channel, chatId, text));
}
function sendDecision(channel, chatId, tableId, prompt, backendUrl, apiKey, context) {
  const mySeq = ++decisionSeq;
  const myHandNumber = currentHandNumber;
  decisionPending = true;
  lastDecision = lastDecision.then(() => warmupDone).then(() => {
    if (mySeq !== decisionSeq) {
      emit({ type: "DECISION_STALE", skipped: mySeq, current: decisionSeq });
      return;
    }
    return new Promise((resolve) => {
      execFile("openclaw", [
        "agent",
        "--local",
        "--session-id",
        `poker-${tableId}`,
        "--message",
        prompt,
        "--thinking",
        "low",
        "--timeout",
        "45",
        "--json"
      ], { timeout: 55e3 }, (err, stdout) => {
        if (mySeq !== decisionSeq) {
          emit({ type: "DECISION_STALE", skipped: mySeq, current: decisionSeq });
          lastSend = lastSend.then(() => doSend(channel, chatId, "Took too long \u2014 timed out on that hand."));
          decisionPending = false;
          flushEventBuffer();
          resolve();
          return;
        }
        if (err) {
          lastSend = lastSend.then(() => doSend(channel, chatId, "Timed out deciding \u2014 auto-folded."));
          decisionPending = false;
          flushEventBuffer();
          resolve();
          return;
        }
        let decision;
        try {
          stdout = stdout.replace(/^[^\n{]*\n/, "");
          const jsonStart = stdout.indexOf("{");
          const jsonEnd = stdout.lastIndexOf("}");
          const json = jsonStart >= 0 && jsonEnd > jsonStart ? stdout.slice(jsonStart, jsonEnd + 1) : stdout;
          const result = JSON.parse(json);
          const payloads = result?.payloads || result?.result?.payloads || [];
          const agentText = payloads.findLast((p) => p.text)?.text || "";
          const decStart = agentText.indexOf("{");
          const decEnd = agentText.lastIndexOf("}");
          if (decStart >= 0 && decEnd > decStart) {
            decision = JSON.parse(agentText.slice(decStart, decEnd + 1));
          }
        } catch (e) {
          const msg = e instanceof Error ? e.message : String(e);
          emit({ type: "DECISION_PARSE_ERROR", error: msg, stdout: stdout.slice(0, 300) });
        }
        if (!decision?.action) {
          emit({ type: "DECISION_NO_ACTION", stdout: stdout.slice(0, 300) });
          decisionPending = false;
          flushEventBuffer();
          resolve();
          return;
        }
        lastDecisionInfo = {
          action: decision.action,
          amount: decision.amount || void 0,
          narration: decision.narration || void 0
        };
        if (decision.action === "fold") {
          foldedInHand = myHandNumber;
        }
        if (currentHandNumber !== myHandNumber) {
          emit({ type: "DECISION_STALE_HAND", decidedHand: myHandNumber, currentHand: currentHandNumber, action: decision.action });
          lastSend = lastSend.then(() => doSend(
            channel,
            chatId,
            `Hand moved on while deciding \u2014 skipped ${decision.action}.`
          ));
          decisionPending = false;
          flushEventBuffer();
          resolve();
          return;
        }
        const body = {
          action: decision.action
        };
        if (decision.amount != null) body.amount = decision.amount;
        if (decision.narration) body.reasoning = decision.narration;
        fetch(`${backendUrl}/api/game/${tableId}/action`, {
          method: "POST",
          headers: { "x-api-key": apiKey, "Content-Type": "application/json" },
          body: JSON.stringify(body),
          signal: AbortSignal.timeout(5e3)
        }).then((resp) => {
          if (resp.ok) {
            if (decision.narration) {
              recentEvents.push(decision.narration);
              if (recentEvents.length > 20) recentEvents.shift();
              appendSessionLog(`> ${decision.action}${decision.amount != null ? ` ${decision.amount}` : ""}: ${decision.narration}`);
            }
          } else {
            context.lastTurnKey = null;
            resp.text().then((reason) => {
              emit({ type: "ACTION_REJECTED", status: resp.status, action: decision.action, reason });
              lastSend = lastSend.then(() => doSend(
                channel,
                chatId,
                `Action rejected (${resp.status}): ${reason || "unknown reason"}`
              ));
            }).catch(() => {
              emit({ type: "ACTION_REJECTED", status: resp.status, action: decision.action, reason: null });
              lastSend = lastSend.then(() => doSend(
                channel,
                chatId,
                `Action rejected (${resp.status}) \u2014 could not read reason.`
              ));
            });
          }
        }).catch(async (actionErr) => {
          emit({ type: "ACTION_SUBMIT_ERROR", error: actionErr.message, action: decision.action });
          await new Promise((r) => setTimeout(r, 3e3));
          try {
            const retryResp = await fetch(`${backendUrl}/api/game/${tableId}/action`, {
              method: "POST",
              headers: { "x-api-key": apiKey, "Content-Type": "application/json" },
              body: JSON.stringify(body),
              signal: AbortSignal.timeout(1e4)
            });
            if (retryResp.ok) {
              emit({ type: "ACTION_RETRY_OK", action: decision.action });
              if (decision.narration) {
                recentEvents.push(decision.narration);
                if (recentEvents.length > 20) recentEvents.shift();
                appendSessionLog(`> ${decision.action}${decision.amount != null ? ` ${decision.amount}` : ""}: ${decision.narration}`);
              }
            } else {
              emit({ type: "ACTION_RETRY_REJECTED", status: retryResp.status, action: decision.action });
            }
          } catch (retryErr) {
            const retryMsg = retryErr instanceof Error ? retryErr.message : String(retryErr);
            emit({ type: "ACTION_RETRY_FAILED", error: retryMsg, action: decision.action });
          }
          context.lastTurnKey = null;
        }).finally(() => {
          decisionPending = false;
          if (decision.action === "fold") {
            eventBuffer = [];
          } else {
            flushEventBuffer();
          }
          resolve();
        });
      });
    });
  }).catch((e) => {
    decisionPending = false;
    flushEventBuffer();
    const msg = e instanceof Error ? e.message : String(e);
    emit({ type: "DECISION_CHAIN_ERROR", error: msg });
  });
}
var __dirname2 = dirname2(fileURLToPath2(import.meta.url));
function readHandNotes() {
  try {
    return readFileSync2(join2(SKILL_ROOT, "poker-hand-notes.txt"), "utf8").trim();
  } catch {
    return "";
  }
}
function appendSessionLog(line) {
  try {
    appendFileSync(SESSION_LOG, line + "\n");
  } catch {
  }
}
function runPostGameReview(channel, chatId, tableId) {
  const sessionLog = readSessionLog();
  const playbook = readPlaybook();
  const notes = readNotes();
  if (!sessionLog) return Promise.resolve();
  const prompt = buildPostGamePrompt(sessionLog, playbook, notes);
  return new Promise((resolve) => {
    execFile("openclaw", [
      "agent",
      "--local",
      "--session-id",
      `poker-${tableId}`,
      "--message",
      prompt,
      "--thinking",
      "low",
      "--timeout",
      "45",
      "--json"
    ], { timeout: 55e3 }, (err, stdout) => {
      if (err) {
        emit({ type: "POST_GAME_REVIEW_ERROR", error: err.message });
        lastSend = lastSend.then(() => doSend(channel, chatId, "Post-game review failed \u2014 playbook unchanged."));
        resolve();
        return;
      }
      try {
        stdout = stdout.replace(/^[^\n{]*\n/, "");
        const jsonStart = stdout.indexOf("{");
        const jsonEnd = stdout.lastIndexOf("}");
        const json = jsonStart >= 0 && jsonEnd > jsonStart ? stdout.slice(jsonStart, jsonEnd + 1) : stdout;
        const result = JSON.parse(json);
        const payloads = result?.payloads || result?.result?.payloads || [];
        const agentText = payloads.findLast((p) => p.text)?.text || "";
        const innerStart = agentText.indexOf("{");
        const innerEnd = agentText.lastIndexOf("}");
        if (innerStart >= 0 && innerEnd > innerStart) {
          const review = JSON.parse(agentText.slice(innerStart, innerEnd + 1));
          if (review.playbook) {
            writeFileSync(PLAYBOOK_FILE, review.playbook.trim() + "\n");
            emit({ type: "POST_GAME_REVIEW_DONE", message: review.message || "Playbook updated." });
            const msg = review.message || "Playbook updated.";
            lastSend = lastSend.then(() => doSend(channel, chatId, msg));
          }
        }
      } catch (e) {
        const msg = e instanceof Error ? e.message : String(e);
        emit({ type: "POST_GAME_REVIEW_ERROR", error: msg, stdout: stdout.slice(0, 300) });
        lastSend = lastSend.then(() => doSend(channel, chatId, "Post-game review failed \u2014 playbook unchanged."));
      }
      resolve();
    });
  });
}
var CONTEXT_FILE = join2(SKILL_ROOT, "poker-game-context.json");
var CONTEXT_TMP = join2(SKILL_ROOT, ".poker-game-context.json.tmp");
function writeGameContext(view, tableId, extraFields = {}) {
  const playbook = readPlaybook() || null;
  const notes = readNotes() || null;
  const handNotes = readHandNotes() || null;
  const context = {
    active: true,
    tableId,
    lastUpdated: (/* @__PURE__ */ new Date()).toISOString(),
    hand: view ? {
      number: view.handNumber,
      phase: view.phase,
      yourCards: view.yourCards || [],
      board: view.boardCards || [],
      pot: view.pot,
      stack: view.yourChips,
      players: (view.players || []).map((p) => ({
        name: p.name,
        seat: p.seat,
        chips: p.chips,
        status: p.status
      }))
    } : null,
    recentEvents: recentEvents.slice(-20),
    lastDecision: lastDecisionInfo,
    playbook,
    notes,
    handNotes,
    ...extraFields
  };
  try {
    writeFileSync(CONTEXT_TMP, JSON.stringify(context, null, 2));
    renameSync(CONTEXT_TMP, CONTEXT_FILE);
  } catch (err) {
    const msg = err instanceof Error ? err.message : String(err);
    emit({ type: "CONTEXT_WRITE_ERROR", error: msg });
  }
}
process.on("uncaughtException", (err) => {
  try {
    writeFileSync(CONTEXT_TMP, JSON.stringify({ active: false, error: err.message, lastUpdated: (/* @__PURE__ */ new Date()).toISOString() }));
    renameSync(CONTEXT_TMP, CONTEXT_FILE);
  } catch {
  }
  emit({ type: "CRASH", error: err.message });
  process.exit(1);
});
process.on("unhandledRejection", (reason) => {
  const msg = reason instanceof Error ? reason.message : String(reason);
  try {
    writeFileSync(CONTEXT_TMP, JSON.stringify({ active: false, error: msg, lastUpdated: (/* @__PURE__ */ new Date()).toISOString() }));
    renameSync(CONTEXT_TMP, CONTEXT_FILE);
  } catch {
  }
  emit({ type: "CRASH", error: msg });
  process.exit(1);
});
function buildDecisionPrompt(summary, playbook, handEvents, recentHandResults, notes = "", handNotes = "") {
  const playbookSection = playbook || "You are a skilled poker player. Play intelligently and mix your play.";
  const handActionSection = handEvents.length > 0 ? `
Action this hand:
${handEvents.join("\n")}
` : "";
  const recentResultsSection = recentHandResults.length > 0 ? `
Recent hand results:
${recentHandResults.join("\n")}
` : "";
  const notesParts = [];
  if (notes) notesParts.push(`Session notes:
${notes}`);
  if (handNotes) notesParts.push(`THIS HAND ONLY:
${handNotes}`);
  const notesSection = notesParts.length > 0 ? `
Tactical notes from your human partner:
${notesParts.join("\n\n")}
` : "";
  return `You are playing No-Limit Hold'em poker. It is your turn to act.

${playbookSection}

Situation: ${summary}
${handActionSection}${recentResultsSection}${notesSection}
Play your best poker. Trust your judgment on hand strength, position, pot odds, and opponent tendencies. If raising, your amount MUST be within the range shown in Actions (e.g., 'raise 40-970' means amount between 40 and 970).

Respond with ONLY a JSON object, no other text:
{"action": "fold|check|call|raise|all_in", "amount": <number if raise/bet, omit otherwise>, "narration": "<one sentence: what you did and why, in your own voice>"}`;
}
async function main() {
  const backendUrl = "https://api.clawplay.fun";
  const apiKey = process.env.CLAWPLAY_API_KEY;
  const [, , tableId] = process.argv;
  if (!apiKey || !tableId) {
    emit({ type: "CONNECTION_ERROR", error: "Usage: CLAWPLAY_API_KEY must be set as env var. node poker-listener.js <tableId> --channel <name> --chat-id <id>" });
    process.exit(1);
  }
  const direct = parseDirectArgs(process.argv);
  if (!direct.enabled || !direct.channel || !direct.chatId) {
    emit({ type: "CONNECTION_ERROR", error: "--channel and --chat-id are required" });
    process.exit(1);
  }
  const channel = direct.channel;
  const chatId = direct.chatId;
  emit({ type: "DELIVERY_MODE", channel, chatId: "***" });
  const sseUrl = `${backendUrl}/api/game/${tableId}/stream?token=${apiKey}`;
  let EventSourceClass;
  try {
    const mod = await Promise.resolve().then(() => (init_dist2(), dist_exports));
    EventSourceClass = mod.default || mod.EventSource;
  } catch {
    emit({ type: "CONNECTION_ERROR", error: "eventsource package not available" });
    process.exit(1);
  }
  const context = { prevState: null, prevPhase: null, lastActionType: null, lastReportedHand: 0, lastTurnKey: null };
  let es;
  let sseFirstConnect = true;
  let lastEventTime = Date.now();
  const HEARTBEAT_TIMEOUT_MS = 9e4;
  let reconnectAttempts = 0;
  const MAX_RECONNECT_ATTEMPTS = 3;
  const RECONNECT_DELAY_MS = 3e3;
  const heartbeatCheck = setInterval(() => {
    if (Date.now() - lastEventTime > HEARTBEAT_TIMEOUT_MS) {
      emit({ type: "HEARTBEAT_TIMEOUT", lastEventAge: Date.now() - lastEventTime });
      if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        gracefulExit("Connection lost after reconnect attempts", 1);
      } else {
        reconnectAttempts++;
        emit({ type: "SSE_RECONNECT_ATTEMPT", attempt: reconnectAttempts });
        es.close();
        setTimeout(() => connectSSE(), RECONNECT_DELAY_MS * 2 ** (reconnectAttempts - 1));
      }
    }
  }, 15e3);
  let exitInProgress = false;
  function gracefulExit(reason, exitCode) {
    if (exitInProgress) return;
    exitInProgress = true;
    clearInterval(heartbeatCheck);
    const isRebuyState = exitCode !== 0 && context.prevState?.canRebuy === true && context.prevState?.yourChips === 0;
    const finalStack = context.prevState?.yourChips ?? "unknown";
    appendSessionLog(`
--- Game ended (${reason}). Final stack: ${finalStack} ---`);
    const contextExtra = exitCode === 0 ? { active: false, tableClosed: true } : isRebuyState ? { active: false, rebuyAvailable: true } : { active: false, error: reason };
    writeGameContext(context.prevState, tableId, contextExtra);
    if (reason !== "Table closed" && !isRebuyState) {
      fetch(`${backendUrl}/api/game/${tableId}/leave`, {
        method: "POST",
        headers: { "x-api-key": apiKey },
        signal: AbortSignal.timeout(3e3)
      }).catch(() => {
      });
    }
    const forceExit = setTimeout(() => {
      es?.close();
      process.exit(exitCode);
    }, 75e3);
    forceExit.unref();
    if (isRebuyState) {
      lastSend.then(() => {
        clearTimeout(forceExit);
        es?.close();
        process.exit(exitCode);
      });
      return;
    }
    lastSend = lastSend.then(() => doSend(
      channel,
      chatId,
      `Game over \u2014 ${reason.toLowerCase()}. Final stack: ${finalStack}.`
    ));
    lastSend.then(() => {
      runPostGameReview(channel, chatId, tableId).catch(() => {
      }).then(() => {
        lastSend.then(() => {
          clearTimeout(forceExit);
          es?.close();
          process.exit(exitCode);
        });
      });
    });
  }
  for (const signal of ["SIGTERM", "SIGINT"]) {
    process.on(signal, () => {
      emit({ type: "SIGNAL_EXIT", signal });
      gracefulExit("Session terminated", 0);
    });
  }
  function connectSSE() {
    if (es) es.close();
    es = new EventSourceClass(sseUrl);
    lastEventTime = Date.now();
    es.onopen = () => {
      lastEventTime = Date.now();
      reconnectAttempts = 0;
      if (sseFirstConnect) {
        sseFirstConnect = false;
        try {
          unlinkSync(join2(SKILL_ROOT, "poker-notes.txt"));
        } catch {
        }
        try {
          unlinkSync(join2(SKILL_ROOT, "poker-hand-notes.txt"));
        } catch {
        }
        try {
          unlinkSync(SESSION_LOG);
        } catch {
        }
        writeGameContext(null, tableId);
        warmupDone = new Promise((resolve) => {
          execFile("openclaw", [
            "agent",
            "--local",
            "--session-id",
            `poker-${tableId}`,
            "--message",
            "(system: session warmup \u2014 no action needed)",
            "--thinking",
            "low",
            "--timeout",
            "15",
            "--json"
          ], { timeout: 2e4 }, () => resolve());
        });
      } else {
        emit({ type: "SSE_RECONNECT" });
      }
    };
    es.addEventListener("state", (event) => {
      try {
        lastEventTime = Date.now();
        const view = JSON.parse(event.data);
        reconnectAttempts = 0;
        const handJustChanged = view.handNumber !== currentHandNumber;
        currentHandNumber = view.handNumber;
        if (handJustChanged) {
          stackBeforeHand = view.yourChips;
          currentHandEvents = [];
          foldedInHand = null;
          try {
            unlinkSync(join2(SKILL_ROOT, "poker-hand-notes.txt"));
          } catch {
          }
        }
        const outputs = processStateEvent(view, context);
        let extraContext = {};
        for (const output of outputs) {
          const outputHand = "handNumber" in output ? output.handNumber : currentHandNumber;
          if (foldedInHand != null && outputHand === foldedInHand && output.type !== "YOUR_TURN" && output.type !== "REBUY_AVAILABLE") {
            continue;
          }
          switch (output.type) {
            case "EVENT":
              if (!gameStartedEmitted && output.message.includes("[Hand #")) {
                emit({ type: "GAME_STARTED" });
                gameStartedEmitted = true;
              }
              if (output.message.startsWith("**[Hand #")) {
                appendSessionLog(output.message);
              }
              recentEvents.push(output.message);
              if (recentEvents.length > 20) recentEvents.shift();
              currentHandEvents.push(output.message);
              break;
            case "YOUR_TURN": {
              const playbook = readPlaybook();
              const notes = readNotes();
              const handNotes = readHandNotes();
              const recentHandResults = recentEvents.filter((e) => e.includes(" won ")).slice(-3);
              const prompt = buildDecisionPrompt(
                output.summary,
                playbook,
                currentHandEvents,
                recentHandResults,
                notes,
                handNotes
              );
              sendDecision(channel, chatId, tableId, prompt, backendUrl, apiKey, context);
              break;
            }
            case "HAND_RESULT": {
              const summary = buildHandResultSummary(output.state, output.handNumber || currentHandNumber);
              const msg = summary || "Hand complete.";
              appendSessionLog(msg);
              recentEvents.push(msg);
              if (recentEvents.length > 20) recentEvents.shift();
              const stackAfter = view.yourChips;
              const bb = view.forcedBets?.bigBlind || 20;
              if (stackBeforeHand != null && stackBeforeHand > 0) {
                const change = Math.abs(stackAfter - stackBeforeHand);
                const changeRatio = change / stackBeforeHand;
                if (changeRatio > 0.5) {
                  const direction = stackAfter > stackBeforeHand ? "Won big" : "Lost big";
                  sendMessage(
                    channel,
                    chatId,
                    `${direction}! ${msg} (${stackBeforeHand} \u2192 ${stackAfter})`
                  );
                } else if (stackAfter > 0 && stackAfter < bb * 10) {
                  sendMessage(
                    channel,
                    chatId,
                    `Short-stacked (${stackAfter} chips, ${Math.floor(stackAfter / bb)} BB). ${msg}`
                  );
                }
              }
              break;
            }
            case "WAITING_FOR_PLAYERS":
              lastSend = lastSend.then(() => doSendChoices(
                channel,
                chatId,
                "All opponents left.",
                [
                  { label: "Keep waiting", value: "wait" },
                  { label: "Leave", value: "leave" }
                ]
              ));
              extraContext = { waitingForPlayers: true };
              break;
            case "REBUY_AVAILABLE": {
              const amt = output.state?.rebuyAmount || "the default amount";
              lastSend = lastSend.then(() => doSendChoices(
                channel,
                chatId,
                `Out of chips! Rebuy for ${amt}?`,
                [
                  { label: "Rebuy", value: "rebuy" },
                  { label: "Leave", value: "leave" }
                ]
              ));
              extraContext = { rebuyAvailable: true };
              break;
            }
            default:
              emit(output);
          }
        }
        writeGameContext(view, tableId, extraContext);
        if (view.hasPendingLeave && (view.phase === "SHOWDOWN" || view.phase === "WAITING")) {
          gracefulExit("Left the table", 0);
          return;
        }
      } catch (err) {
        const msg = err instanceof Error ? err.message : String(err);
        emit({ type: "CONNECTION_ERROR", error: `Failed to process state event: ${msg}` });
        gracefulExit(`State parse error: ${msg}`, 1);
      }
    });
    es.addEventListener("keepalive", () => {
      lastEventTime = Date.now();
      reconnectAttempts = 0;
    });
    es.addEventListener("closed", () => {
      lastEventTime = Date.now();
      gracefulExit("Table closed", 0);
    });
    es.onerror = (err) => {
      const msg = "message" in err ? err.message : "unknown";
      emit({ type: "CONNECTION_ERROR", error: `SSE connection error: ${msg || "unknown"}` });
    };
  }
  connectSSE();
}
function emit(obj) {
  process.stdout.write(JSON.stringify(obj) + "\n");
}
var isDirectRun = process.argv[1] && import.meta.url.endsWith(process.argv[1].replace(/.*\//, ""));
if (isDirectRun && process.argv.length > 3) {
  main();
}
export {
  buildDecisionPrompt,
  buildHandResultSummary,
  buildSummary,
  parseDirectArgs,
  processStateEvent,
  readHandNotes,
  sendDecision,
  sendMessage,
  writeGameContext
};
