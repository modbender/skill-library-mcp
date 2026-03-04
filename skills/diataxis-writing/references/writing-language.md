# Language Style for Four Documentation Types

Theory Source: https://diataxis.fr/

---

## Overview

Four documentation types need to use different language styles because:
- They serve different user needs
- They have different purposes
- They have different relationships with readers

Using correct language style is key to maintaining type purity.

---

## Tutorial Language Style

### Core Characteristics

- **First-person plural** - "We" affirms tutor-learner relationship
- **Clear imperatives** - No ambiguity
- **Expectation descriptions** - Tell what will be seen
- **Orientation clues** - Help confirm on right track

### Standard Statements

```
"In this tutorial, we will..."
"First, do X"
"Now, do Y"
"Now that you have done Y, do Z"
"The output should look like..."
"Notice..."
"Remember..."
"Let's check..."
"You have built..."
```

### Example

```markdown
In this tutorial, we will create a simple Python Web application.

First, install Flask:

```
pip install flask
```

You will see output like:

```
Successfully installed flask-2.0.0
```

Note version number may differ.

Now, create file app.py...
```

### Avoid Statements

```
❌ "Flask is a lightweight WSGI framework, its design philosophy is..."
   (Explanation - link to Explanation)

❌ "You can use Flask or Django, depending on..."
   (Options - ignore alternatives)

❌ "This command will..."
   (Third person - use "we will")
```

---

## How-to Guide Language Style

### Core Characteristics

- **Conditional imperatives** - "If you want X, do Y"
- **Concise and direct** - Focus on action
- **Reference citations** - Avoid polluting practical guidance

### Standard Statements

```
"This guide shows you how to..."
"If you want X, do Y"
"To achieve W, do Z"
"Refer to the X reference guide for a full list of options"
"In ... scenarios, use..."
"An alternative approach is..."
```

### Example

```markdown
This guide shows how to configure Nginx reverse proxy.

If you want to proxy HTTP traffic, add the following configuration:

```
location / {
    proxy_pass http://localhost:8000;
}
```

For HTTPS, refer to [SSL Configuration Reference](...) for complete options.

In load balancing scenarios, use:

```
upstream backend {
    server localhost:8000;
    server localhost:8001;
}
```
```

### Avoid Statements

```
❌ "Nginx is a high-performance web server, it was created by..."
   (Explanation - link to Explanation)

❌ "To understand reverse proxy, first need to know..."
   (Teaching - link to Tutorial)

❌ "The syntax of proxy_pass directive is..."
   (Reference - link to Reference)
```

---

## Reference Language Style

### Core Characteristics

- **State facts** - Neutral description
- **List style** - List commands, options, parameters
- **Authoritative** - No ambiguity
- **Warnings** - Provide when necessary

### Standard Statements

```
"X inherits Y's defaults"
"Subcommands: a, b, c, d, e, f"
"Parameters: name (string), age (integer)"
"Must use X"
"Must not apply Y unless Z"
"Valid range: 1-100"
"Default value: 30"
```

### Example

```markdown
## Flask.run()

Start the development server.

### Parameters

**host** (string, default: '127.0.0.1')
    Host address the server binds to.

**port** (integer, default: 5000)
    Port to listen on. Valid range: 1-65535.

**debug** (boolean, default: False)
    Enable debug mode. Must be True or False.

### Return Value

No return value. Server runs until interrupted.

### Warning

Must not use this method in production environments.
```

### Avoid Statements

```
❌ "We recommend using debug=False because it's more secure"
   (Advice - delete or move to How-to)

❌ "The history of this feature dates back to..."
   (Explanation - link to Explanation)

❌ "To use run(), first create app..."
   (Instruction - link to How-to)
```

---

## Explanation Language Style

### Core Characteristics

- **Explanatory** - "The reason for X is..."
- **Judgments and opinions** - "W is better than Z because..."
- **Context** - Provide background
- **Tradeoffs** - Discuss alternatives

### Standard Statements

```
"The reason for X is historically Y..."
"W is better than Z, because..."
"An X in system Y is analogous to a W in system Z. However..."
"Some users prefer W (because Z). This can be a good approach, but..."
"An X interacts with a Y as follows..."
"From the perspective of..."
"In contrast..."
```

### Example

```markdown
## Why Choose Microservices Architecture

The reason microservices architecture became popular is it solves problems
monolithic applications encounter when scaling.

From a historical perspective, early web applications were all monolithic.
As team size grew, monolithic shortcomings began to appear...

In contrast, microservices provide better...

Some teams prefer keeping monolithic architecture (because it's simple).
This might be a good approach, but when teams exceed 10 people,
coordination costs increase significantly...

Inter-service communication in microservices is analogous to function
calls in monoliths, however network latency and failure handling
require additional consideration...
```

### Avoid Statements

```
❌ "To do X, run the following command..."
   (Instruction - link to How-to)

❌ "Parameters: name (string)"
   (Reference - link to Reference)

❌ "First, install X. Then, configure Y..."
   (Tutorial - link to Tutorial)
```

---

## Language Style Comparison Table

| Type | Person | Tone | Typical Sentence | Explanation Level |
|------|--------|------|------------------|-------------------|
| **Tutorial** | First-person plural (we) | Instructional, supportive | "We will...", "Notice..." | Minimize |
| **How-to** | Second person (you/implied) | Directive, practical | "If you want X, do Y" | Link to Reference |
| **Reference** | Third person | Neutral, authoritative | "X is...", "Parameters:" | None |
| **Explanation** | Flexible | Discursive, discussion | "X because...", "In contrast..." | Core content |

---

## Quick Switch Guide

### Switching from Tutorial to Explanation

```markdown
...we use HTTPS because it's more secure.

> Want to understand how HTTPS works? Read [HTTPS Encryption Principles](...)
```

### Switching from How-to to Reference

```markdown
...configure the timeout parameter.

> Need complete parameter list? Check [API Reference](...)
```

### Switching from Reference to Explanation

```markdown
timeout (integer, default: 30)
    Request timeout time.

> Why is default value 30? Read [Timeout Strategy Design](...)
```

---

## Usage Recommendations

### During Writing

Always pay attention to whether language style matches document type.

### When Checking

Read document aloud, listen if tone matches type.

### When Refactoring

Identify style-mismatched paragraphs, move or rewrite.

---

**Version**: 1.0  
**Source**: https://diataxis.fr/  
**Compiled by**: Zhua Zhua
