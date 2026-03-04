# Glucksrad — Decision Wheel

Use this skill when a user is stuck choosing between multiple options and wants a fun, random way to decide. Generate a URL that opens an interactive 3D spinning wheel.

## When to use

- The user can't decide between a few options (e.g. "where should we eat?", "which movie should we watch?")
- The user explicitly asks you to pick one at random or spin a wheel
- There are 2–20 concrete options to choose from

Do NOT use this when the user needs a reasoned recommendation — only when randomness is welcome.

## URL format

```
https://makedecisionforme.netlify.app/?items=Option1:Weight,Option2:Weight,Option3:Weight
```

### Rules

- **Base URL**: `https://makedecisionforme.netlify.app/`
- **Query parameter**: `items` — comma-separated list of entries
- **Entry format**: `Name:Weight`
  - `Name` — the option label. URL-encode special characters (spaces → `%20`, `&` → `%26`, etc.)
  - `Weight` — optional integer (defaults to `1`). Higher weight = larger slice on the wheel. Use weights when the user indicates a preference or when options aren't equally likely.
- Items are separated by commas (`,`). Do not add spaces between items.

### Examples

Equal chances:
```
?items=Pizza,Sushi,Tacos,Burgers
```

Weighted (Pizza is 3x more likely than Sushi):
```
?items=Pizza:3,Sushi:1,Tacos:2
```

Names with spaces:
```
?items=Thai%20Food,Fish%20and%20Chips,Mac%20%26%20Cheese
```

## How to respond

1. Collect the options from the user's message.
2. Build the URL with the `items` query parameter.
3. Present the link to the user so they can click it and spin the wheel.
