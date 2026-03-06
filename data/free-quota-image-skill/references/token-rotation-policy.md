# Token Rotation Policy

## Goals

* Allow multiple tokens per provider.
* Rotate automatically when quota errors occur.
* Persist exhausted-token state by provider and day.

## Token input normalization

`providers.<id>.tokens` accepts:

* CSV string (`"tok_a,tok_b"`)
* list of strings (`["tok_a", "tok_b"]`)

The pool trims whitespace and removes duplicates while preserving order.

## Daily reset rules

* `huggingface`, `a4f`: reset by UTC date.
* `gitee`, `modelscope`: reset by Beijing date (UTC+8).
* `openai_compatible`: reset by UTC date.

Persisted schema in `state.token_status_file`:

```JSON
{
  "huggingface": {
    "date": "2026-03-02",
    "exhausted": {
      "hf_xxx": true
    }
  }
}
```

## Quota and auth classification

Quota is detected when status/message matches one of:

* HTTP `429`
* `quota`
* `credit`
* `insufficient_quota`
* `You have exceeded your free GPU quota`
* `arrearage`

Auth is detected by:

* HTTP `401`/`403`
* `unauthorized`
* `forbidden`
* `invalid token`
* `authentication`

## Rotation behavior

1. Load available (not exhausted) tokens for provider.
2. Try each token in order.
3. On quota error, mark token exhausted and continue.
4. On auth error, continue to next token.
5. If all token attempts fail, move to next provider in routing order.

Batch mode (`--count > 1`) behavior:

* In `auto` routing, each image rotates the provider start position.
* Within a provider, token attempt order also rotates per image.
* This spreads requests across providers/tokens to reduce burst pressure on a single key.

Hugging Face special case:

* If no active token and `allow_public_quota: true`, one `public` attempt is allowed.

