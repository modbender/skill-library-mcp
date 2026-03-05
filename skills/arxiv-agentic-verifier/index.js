const { OpenAI } = require('openai');
const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

class AgenticVerifier {
  constructor(apiKey) {
    const key = apiKey || process.env.OPENAI_API_KEY;
    if (key) {
      this.openai = new OpenAI({ apiKey: key });
    } else {
      console.warn("⚠️ No OPENAI_API_KEY provided. Using mock mode.");
      this.openai = null;
    }
    this.tempDir = path.join(__dirname, 'temp_exec');
    if (!fs.existsSync(this.tempDir)) {
      fs.mkdirSync(this.tempDir);
    }
  }

  /**
   * Generates a "discriminative" test case for the given problem and code.
   * Based on the "Agentic Verifier" concept from arXiv:4a4c4dae6a5145ebc4d62eb2d64b0f0f.
   * 
   * @param {string} problemDescription
   * @param {string} candidateCode
   * @param {string} language (python, javascript)
   * @returns {Promise<object>} { input, expectedOutput, strategy }
   */
  async generateTestCase(problemDescription, candidateCode, language = 'python') {
    if (!this.openai) {
      return {
        input: "1 2",
        expectedOutput: "3",
        strategy: "Mock strategy: verify basic functionality (No API Key)"
      };
    }

    const prompt = `
You are an Agentic Verifier for competitive coding.
Your goal is to generate a difficult, edge-case test input that might cause the candidate code to fail.
Analyze the problem and the code to find potential weaknesses (e.g., overflow, large inputs, specific constraints).

Problem:
${problemDescription}

Code:
${candidateCode}

Return ONLY a JSON object with:
{
  "input": "string representation of input",
  "expectedOutput": "string representation of correct output",
  "strategy": "Explanation of why this test case is hard"
}
`;

    try {
      const completion = await this.openai.chat.completions.create({
        messages: [{ role: "user", content: prompt }],
        model: "gpt-4-turbo-preview", // Use a smart model
        response_format: { type: "json_object" },
      });

      const result = JSON.parse(completion.choices[0].message.content);
      return result;
    } catch (error) {
      console.error("Error generating test case:", error);
      // Fallback for demo/testing without API key
      if (!process.env.OPENAI_API_KEY) {
        console.warn("Using fallback mock data due to missing API key.");
        return {
          input: "1 2",
          expectedOutput: "3",
          strategy: "Mock strategy: verify basic functionality"
        };
      }
      throw error;
    }
  }

  /**
   * Runs the code against the generated test case.
   * @param {string} code
   * @param {string} input
   * @param {string} language
   * @returns {object} { success, actualOutput, error }
   */
  runCode(code, input, language = 'python') {
    const filename = `test_run_${Date.now()}.${language === 'python' ? 'py' : 'js'}`;
    const filepath = path.join(this.tempDir, filename);
    
    fs.writeFileSync(filepath, code);

    let command;
    if (language === 'python') {
      command = `python3 ${filepath}`;
    } else {
      command = `node ${filepath}`;
    }

    try {
      // Basic execution with input piping
      // Note: This is simplified. Real competitive coding runners need sandboxing.
      const output = execSync(command, { input: input, timeout: 5000, encoding: 'utf-8' });
      return { success: true, actualOutput: output.trim() };
    } catch (error) {
      return { success: false, error: error.message, actualOutput: error.stdout ? error.stdout.toString() : '' };
    } finally {
      if (fs.existsSync(filepath)) fs.unlinkSync(filepath);
    }
  }

  /**
   * Main verification loop.
   * @param {string} problem
   * @param {string} code
   * @param {string} language
   */
  async verify(problem, code, language = 'python') {
    console.log(`Starting verification for ${language} code...`);
    
    // 1. Generate test case
    const testCase = await this.generateTestCase(problem, code, language);
    console.log(`Generated Test Case Strategy: ${testCase.strategy}`);
    console.log(`Input: ${testCase.input}`);

    // 2. Run code
    const result = this.runCode(code, testCase.input, language);

    // 3. Analyze result
    if (!result.success) {
      console.log(`❌ Code crashed or timed out: ${result.error}`);
      return { passed: false, reason: "Runtime Error", detail: result };
    }

    if (result.actualOutput === testCase.expectedOutput) {
      console.log(`✅ Passed test case. Output: ${result.actualOutput}`);
      return { passed: true, testCase };
    } else {
      console.log(`❌ Failed test case. Expected: ${testCase.expectedOutput}, Got: ${result.actualOutput}`);
      return { passed: false, reason: "Wrong Answer", detail: { expected: testCase.expectedOutput, actual: result.actualOutput } };
    }
  }
}

module.exports = AgenticVerifier;
