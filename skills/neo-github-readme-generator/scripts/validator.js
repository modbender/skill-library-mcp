/**
 * Quality checks for generated README content.
 * Validates section completeness, formatting, and style conformity.
 */

const REQUIRED_SECTIONS = [
  { heading: "Installation", level: 2 },
  { heading: "Usage", level: 2 },
  { heading: "Contributing", level: 2 },
  { heading: "License", level: 2 },
];

const RECOMMENDED_SECTIONS = [
  { heading: "API Documentation", level: 2 },
  { heading: "Project Structure", level: 2 },
  { heading: "Dependencies", level: 2 },
];

/**
 * Parse headings from markdown content.
 * Returns array of { level, text, line } objects.
 */
function parseHeadings(content) {
  const headings = [];
  const lines = content.split("\n");

  for (let i = 0; i < lines.length; i++) {
    const match = lines[i].match(/^(#{1,6})\s+(.+)$/);
    if (match) {
      headings.push({
        level: match[1].length,
        text: match[2].trim(),
        line: i + 1,
      });
    }
  }

  return headings;
}

/**
 * Check that all required sections are present.
 */
function checkRequiredSections(content) {
  const headings = parseHeadings(content);
  const errors = [];

  for (const req of REQUIRED_SECTIONS) {
    const found = headings.some(
      (h) => h.level === req.level && h.text.toLowerCase() === req.heading.toLowerCase()
    );
    if (!found) {
      errors.push(`Missing required section: ## ${req.heading}`);
    }
  }

  return errors;
}

/**
 * Check recommended sections and return warnings.
 */
function checkRecommendedSections(content) {
  const headings = parseHeadings(content);
  const warnings = [];

  for (const rec of RECOMMENDED_SECTIONS) {
    const found = headings.some(
      (h) => h.level === rec.level && h.text.toLowerCase() === rec.heading.toLowerCase()
    );
    if (!found) {
      warnings.push(`Recommended section missing: ## ${rec.heading}`);
    }
  }

  return warnings;
}

/**
 * Check that the README has a title (H1 heading).
 */
function checkTitle(content) {
  const headings = parseHeadings(content);
  if (!headings.some((h) => h.level === 1)) {
    return ["Missing title: expected a # heading at the top"];
  }
  return [];
}

/**
 * Check that code blocks are properly closed.
 */
function checkCodeBlocks(content) {
  const errors = [];
  const lines = content.split("\n");
  let inCodeBlock = false;
  let codeBlockStart = 0;

  for (let i = 0; i < lines.length; i++) {
    if (lines[i].trim().startsWith("```")) {
      if (!inCodeBlock) {
        inCodeBlock = true;
        codeBlockStart = i + 1;
      } else {
        inCodeBlock = false;
      }
    }
  }

  if (inCodeBlock) {
    errors.push(`Unclosed code block starting at line ${codeBlockStart}`);
  }

  return errors;
}

/**
 * Check minimum content length — a useful README should have substance.
 */
function checkMinimumLength(content) {
  const errors = [];
  const lines = content.split("\n").filter((l) => l.trim().length > 0);

  if (lines.length < 10) {
    errors.push(`README is too short (${lines.length} non-empty lines). Expected at least 10.`);
  }

  return errors;
}

/**
 * Check that badges/images have alt text.
 */
function checkImageAltText(content) {
  const warnings = [];
  const imgRegex = /!\[([^\]]*)\]\([^)]+\)/g;
  let match;

  while ((match = imgRegex.exec(content)) !== null) {
    if (!match[1].trim()) {
      warnings.push("Image/badge found without alt text");
    }
  }

  return warnings;
}

/**
 * Run all validation checks on the generated README.
 * Returns { valid, errors, warnings, score }.
 */
function validate(content) {
  const errors = [
    ...checkTitle(content),
    ...checkRequiredSections(content),
    ...checkCodeBlocks(content),
    ...checkMinimumLength(content),
  ];

  const warnings = [
    ...checkRecommendedSections(content),
    ...checkImageAltText(content),
  ];

  // Score: start at 100, lose 15 per error, 5 per warning
  const score = Math.max(0, 100 - errors.length * 15 - warnings.length * 5);

  return {
    valid: errors.length === 0,
    errors,
    warnings,
    score,
  };
}

module.exports = {
  parseHeadings,
  checkRequiredSections,
  checkRecommendedSections,
  checkTitle,
  checkCodeBlocks,
  checkMinimumLength,
  checkImageAltText,
  validate,
};
