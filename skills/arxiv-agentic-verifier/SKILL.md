# ArXiv Agentic Verifier

**Source Paper:** [Scaling Agentic Verifier for Competitive Coding](https://arxiv.org/abs/2602.09012) (ID: 4a4c4dae6a5145ebc4d62eb2d64b0f0f)
**Type:** Code Verification / Test Generation

## Description
This skill implements an "Agentic Verifier" that actively reasons about code correctness by generating targeted, "discriminative" test cases. Instead of random sampling, it analyzes the problem constraints and code logic to find edge cases or logic flaws.

## Features
-   **Analyze Code:** Understands Python/JS code logic.
-   **Generate Tests:** Creates specific inputs to break the code.
-   **Execute & Verify:** Runs the code against generated tests (sandbox recommended for production).

## Usage

```javascript
const AgenticVerifier = require('./index');
const verifier = new AgenticVerifier(process.env.OPENAI_API_KEY);

const problem = "Given two integers A and B, output their sum.";
const code = "print(int(input().split()[0]) + int(input().split()[1]))";

verifier.verify(problem, code, 'python')
  .then(result => console.log(result))
  .catch(err => console.error(err));
```

## Configuration
-   **OPENAI_API_KEY:** Required for LLM reasoning.

## Security Warning
This skill executes code provided to it. Use in a restricted environment or sandbox.
