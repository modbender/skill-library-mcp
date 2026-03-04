/**
 * DS-160 Auto-fill Script
 *
 * This script uses Chrome DevTools Protocol (CDP) to automate filling DS-160 visa forms.
 * It reads element mappings from YAML and user data from CSV.
 *
 * Note: Users may provide data in Chinese. This script includes a built-in translation
 * dictionary for common fields. For fields not in the dictionary, the script will
 * request LLM assistance for translation.
 */

const fs = require('fs');
const path = require('path');
const yaml = require('js-yaml');

// Configuration
const CONFIG = {
  workspaceDir: process.env.OPENCLAW_WORKSPACE || '/home/jasonzhao/.openclaw/workspace',
  dataDir: path.join(process.env.OPENCLAW_WORKSPACE || '/home/jasonzhao/.openclaw/workspace', 'ds160'),
  yamlFile: path.join(__dirname, '../references/ds160-elements.yaml'),
  csvFile: path.join(process.env.OPENCLAW_WORKSPACE || '/home/jasonzhao/.openclaw/workspace', 'ds160/ds160-user-info.csv'),
  sessionFile: path.join(process.env.OPENCLAW_WORKSPACE || '/home/jasonzhao/.openclaw/workspace', 'ds160/ds160-session.json')
};

// Global session data
let sessionData = {
  applicationId: null,
  securityQuestion: null,
  securityAnswer: null,
  currentPageIndex: 0,
  completedPages: [],
  startDate: null
};

/**
 * Chinese to English translation dictionary for common DS-160 fields
 */
const TRANSLATION_DICT = {
  // Gender
  '男': 'MALE',
  '女': 'FEMALE',
  '男性': 'MALE',
  '女性': 'FEMALE',

  // Marital Status
  '已婚': 'MARRIED',
  '未婚': 'SINGLE',
  '离异': 'DIVORCED',
  '丧偶': 'WIDOWED',
  '合法分居': 'LEGALLY SEPARATED',
  '事实婚姻': 'COMMON LAW MARRIAGE',
  '民事结合': 'CIVIL UNION/DOMESTIC PARTNERSHIP',

  // Yes/No
  '是': 'Yes',
  '否': 'No',
  '有': 'Yes',
  '没有': 'No',
  '是，有': 'Yes',
  '否，没有': 'No',

  // Common Countries
  '中国': 'CHINA',
  '美国': 'USA',
  '英国': 'UNITED KINGDOM',
  '日本': 'JAPAN',
  '韩国': 'KOREA, SOUTH',

  // Common Visa Types
  '旅游': 'B1/B2',
  '商务': 'B1/B2',
  '商务/旅游': 'B1/B2',
  '学生': 'F1',
  '访问学者': 'J1',
  '工作': 'H1B',

  // Payment
  '自己': 'SELF',
  '自费': 'SELF',
  '公司': 'OTHER COMPANY',
  '其他人': 'OTHER PERSON',

  // U.S. Point of Contact - Relationship
  '朋友': 'Friend',
  '亲戚': 'Relative',
  '同事': 'Colleague',
  '配偶': 'Spouse',
  '同学': 'Classmate',
  '其他': 'Other',

  // Other Names, Telecode, etc.
  '不适用': 'Does Not Apply',
  '不，不适用': 'Does Not Apply'
};

/**
 * Check if a string contains Chinese characters
 */
function hasChinese(str) {
  return /[\u4e00-\u9fa5]/.test(str);
}

/**
 * Translate Chinese value to English using dictionary or request LLM assistance
 */
function translateValue(value, elementName, elementInfo) {
  if (!value || !hasChinese(value)) {
    return { translated: false, value };
  }

  const trimmedValue = value.trim();

  // Check dictionary first
  if (TRANSLATION_DICT[trimmedValue]) {
    console.log(`✓ Translated "${trimmedValue}" → "${TRANSLATION_DICT[trimmedValue]}" (dict)`);
    return { translated: true, value: TRANSLATION_DICT[trimmedValue] };
  }

  // Not in dictionary - request LLM assistance
  return {
    translated: false,
    value: trimmedValue,
    needsTranslation: true,
    translationContext: {
      elementName,
      elementInfo: {
        label: elementInfo.label,
        label_cn: elementInfo.label_cn,
        type: elementInfo.type,
        options: elementInfo.options
      }
    }
  };
}

/**
 * Load session data from file
 */
function loadSession() {
  try {
    if (fs.existsSync(CONFIG.sessionFile)) {
      const data = fs.readFileSync(CONFIG.sessionFile, 'utf8');
      sessionData = JSON.parse(data);
      console.log('✓ Loaded session data:', JSON.stringify(sessionData, null, 2));
      return sessionData;
    }
  } catch (error) {
    console.log('No existing session found, starting fresh');
  }
  return null;
}

/**
 * Save session data to file
 */
function saveSession() {
  try {
    if (!fs.existsSync(CONFIG.dataDir)) {
      fs.mkdirSync(CONFIG.dataDir, { recursive: true });
    }
    fs.writeFileSync(CONFIG.sessionFile, JSON.stringify(sessionData, null, 2));
    console.log('✓ Session data saved');
  } catch (error) {
    console.error('✗ Failed to save session:', error.message);
  }
}

/**
 * Parse YAML element mapping file
 */
function parseYaml(yamlPath) {
  try {
    const fileContents = fs.readFileSync(yamlPath, 'utf8');
    const data = yaml.load(fileContents);
    console.log(`✓ Loaded ${data.pages.length} pages from YAML`);
    return data;
  } catch (error) {
    throw new Error(`Failed to parse YAML: ${error.message}`);
  }
}

/**
 * Parse CSV user data file
 */
function parseCSV(csvPath) {
  try {
    const fileContents = fs.readFileSync(csvPath, 'utf8');
    const lines = fileContents.trim().split('\n');
    const headers = lines[0].split(',').map(h => h.trim());

    const data = {};
    for (let i = 1; i < lines.length; i++) {
      const values = parseCSVLine(lines[i]);
      const page = values[0];
      const fieldName = values[1];
      const userValue = values[6] || ''; // User填写 column (index 6)

      if (fieldName && !data[fieldName]) {
        data[fieldName] = {
          page,
          value: userValue.trim(),
          description: values[2] || '',
          descriptionCn: values[3] || '',
          required: values[4] === '是',
          example: values[5] || ''
        };
      }
    }

    console.log(`✓ Loaded ${Object.keys(data).length} fields from CSV`);
    return data;
  } catch (error) {
    throw new Error(`Failed to parse CSV: ${error.message}`);
  }
}

/**
 * Parse a CSV line handling quoted values
 */
function parseCSVLine(line) {
  const result = [];
  let current = '';
  let inQuotes = false;

  for (let i = 0; i < line.length; i++) {
    const char = line[i];

    if (char === '"') {
      inQuotes = !inQuotes;
    } else if (char === ',' && !inQuotes) {
      result.push(current);
      current = '';
    } else {
      current += char;
    }
  }
  result.push(current);

  return result;
}

/**
 * Find current page from URL
 */
function findCurrentPage(pages, currentUrl) {
  for (const page of pages) {
    if (currentUrl.includes(page.url) || currentUrl.includes(page.page_id)) {
      return page;
    }
  }
  return null;
}

/**
 * Locate element using CDP
 */
async function locateElement(page, elementInfo) {
  const elementId = elementInfo.id;
  const elementType = elementInfo.type;
  const elementName = elementInfo.name;

  // Try multiple locator strategies
  const locators = [
    // Strategy 1: By ID
    `document.getElementById('${elementId}')`,
    // Strategy 2: By name
    `document.querySelector('[name="${elementName}"]')`,
    // Strategy 3: By selector
    `document.querySelector('#${elementId}')`
  ];

  for (const locator of locators) {
    try {
      const result = await page.evaluate(`!!(${locator})`);
      if (result) {
        console.log(`✓ Found element ${elementName} using: ${locator}`);
        return { found: true, locator, elementId };
      }
    } catch (error) {
      // Continue to next strategy
    }
  }

  console.log(`✗ Element ${elementName} (${elementId}) not found`);
  return { found: false, elementId, elementType, elementName, elementInfo };
}

/**
 * Fill form element
 */
async function fillElement(page, elementData, userData, currentUrl) {
  const { found, locator, elementId, elementType, elementName, elementInfo } = elementData;

  if (!found) {
    // Element not found - need LLM assistance
    return {
      success: false,
      needsLLM: true,
      message: `Element ${elementName} (${elementId}) not found on page`,
      elementId,
      elementType,
      elementInfo,
      currentUrl
    };
  }

  // Get user value
  const fieldValue = userData[elementName]?.value;

  if (!fieldValue && elementInfo.required) {
    // Data missing - need user input
    return {
      success: false,
      needsUserInput: true,
      message: `Missing data for required field: ${elementName} (${elementInfo.label_cn || elementInfo.label})`,
      elementId,
      elementType,
      elementName,
      elementInfo
    };
  }

  // Check if translation is needed
  const translationResult = translateValue(fieldValue, elementName, elementInfo);

  if (translationResult.needsTranslation) {
    // Need LLM assistance for translation
    return {
      success: false,
      needsTranslation: true,
      message: `Translation needed for field ${elementName}: "${translationResult.value}"`,
      elementId,
      elementType,
      elementName,
      elementInfo,
      originalValue: translationResult.value,
      translationContext: translationResult.translationContext
    };
  }

  const valueToFill = translationResult.value;

  try {
    let fillScript = '';

    switch (elementType) {
      case 'text':
      case 'textarea':
        fillScript = `
          const el = ${locator};
          if (el) {
            el.value = '${valueToFill}';
            el.dispatchEvent(new Event('input', { bubbles: true }));
            el.dispatchEvent(new Event('change', { bubbles: true }));
            true;
          } else {
            false;
          }
        `;
        break;

      case 'select':
        // Find option by text or value
        fillScript = `
          const el = ${locator};
          if (el) {
            const options = Array.from(el.options);
            let option = options.find(o => o.text === '${valueToFill}' || o.value === '${valueToFill}');
            if (!option) {
              option = options.find(o => o.text.includes('${valueToFill}') || o.value.includes('${valueToFill}'));
            }
            if (option) {
              el.value = option.value;
              el.dispatchEvent(new Event('change', { bubbles: true }));
              true;
            } else {
              false;
            }
          } else {
            false;
          }
        `;
        break;

      case 'checkbox':
        fillScript = `
          const el = ${locator};
          if (el) {
            const shouldBeChecked = '${valueToFill}'.toLowerCase() === 'true' || '${valueToFill}'.toLowerCase() === 'yes';
            if (el.checked !== shouldBeChecked) {
              el.click();
            }
            true;
          } else {
            false;
          }
        `;
        break;

      case 'radio':
        fillScript = `
          const el = ${locator};
          if (el) {
            const radios = document.querySelectorAll('[name="${elementName}"]');
            const radio = Array.from(radios).find(r => r.id === '${elementId}');
            if (radio) {
              radio.click();
              true;
            } else {
              false;
            }
          } else {
            false;
          }
        `;
        break;

      default:
        return {
          success: false,
          needsLLM: true,
          message: `Unsupported element type: ${elementType}`,
          elementId,
          elementType
        };
    }

    const result = await page.evaluate(fillScript);

    if (result) {
      const displayValue = translationResult.translated
        ? `${translationResult.value} (translated from: "${fieldValue}")`
        : valueToFill;
      console.log(`✓ Filled ${elementName}: ${displayValue}`);
      return { success: true, elementName, value: valueToFill, originalValue: fieldValue };
    } else {
      return {
        success: false,
        needsLLM: true,
        message: `Failed to fill ${elementName}`,
        elementId,
        elementType
      };
    }

  } catch (error) {
    return {
      success: false,
      needsLLM: true,
      message: `Error filling ${elementName}: ${error.message}`,
      elementId,
      elementType
    };
  }
}

/**
 * Handle captcha using LLM
 */
async function handleCaptcha(page, currentUrl) {
  console.log('🤖 Captcha detected - calling LLM for assistance');

  // This function should be called from the main skill
  // The skill will use the image tool to analyze the captcha
  return {
    needsCaptcha: true,
    message: 'Captcha detected. Please analyze the captcha image and provide the code.',
    currentUrl
  };
}

/**
 * Extract Application ID from page
 */
async function extractApplicationId(page) {
  try {
    // Try to find Application ID in various locations
    const selectors = [
      '//td[contains(text(), "Application ID")]/following-sibling::td',
      '//div[contains(text(), "Application ID")]',
      '//span[contains(text(), "Application ID")]'
    ];

    for (const selector of selectors) {
      try {
        const result = await page.evaluate(`
          (function() {
            const xpath = '${selector}';
            const result = document.evaluate(
              xpath,
              document,
              null,
              XPathResult.FIRST_ORDERED_NODE_TYPE,
              null
            );
            const node = result.singleNodeValue;
            return node ? node.textContent.trim() : null;
          })()
        `);

        if (result && result.match(/[A-Z0-9]{10}/)) {
          const match = result.match(/[A-Z0-9]{10}/);
          if (match) {
            console.log(`✓ Found Application ID: ${match[0]}`);
            return match[0];
          }
        }
      } catch (error) {
        // Continue to next selector
      }
    }

    return null;
  } catch (error) {
    console.log('Could not extract Application ID');
    return null;
  }
}

/**
 * Generate random security question and answer
 */
function generateSecurityQA() {
  const questions = [
    {
      value: '1',
      text: 'What is the given name of your mother\'s mother?',
      answer: 'LiMei'
    },
    {
      value: '2',
      text: 'What is the given name of your father\'s father?',
      answer: 'WangGang'
    },
    {
      value: '3',
      text: 'What is your maternal grandmother\'s maiden name?',
      answer: 'Chen'
    },
    {
      value: '4',
      text: 'What name did your family used to call you when you were a child?',
      answer: 'XiaoMing'
    },
    {
      value: '5',
      text: 'In what city did you meet your spouse/significant other?',
      answer: 'Beijing'
    }
  ];

  const selected = questions[Math.floor(Math.random() * questions.length)];
  return {
    question: selected.text,
    questionValue: selected.value,
    answer: selected.answer
  };
}

/**
 * Save CSV file to workspace
 */
function saveCSVFile(csvContent) {
  try {
    if (!fs.existsSync(CONFIG.dataDir)) {
      fs.mkdirSync(CONFIG.dataDir, { recursive: true });
    }
    fs.writeFileSync(CONFIG.csvFile, csvContent);
    console.log(`✓ CSV saved to ${CONFIG.csvFile}`);
    return CONFIG.csvFile;
  } catch (error) {
    throw new Error(`Failed to save CSV: ${error.message}`);
  }
}

/**
 * Main fill function
 */
async function fillPage(page, currentUrl, userData, yamlData) {
  console.log(`\n📄 Processing page: ${currentUrl}`);

  // Find current page in YAML
  const currentPage = findCurrentPage(yamlData.pages, currentUrl);

  if (!currentPage) {
    console.log(`⚠️  Page not found in mapping: ${currentUrl}`);
    return {
      success: false,
      message: `Page not found in mapping`,
      currentUrl
    };
  }

  console.log(`✓ Found page mapping: ${currentPage.page_name}`);

  // Check for captcha
  if (currentPage.page_id === 'home') {
    const captchaResult = await handleCaptcha(page, currentUrl);
    if (captchaResult.needsCaptcha) {
      return captchaResult;
    }
  }

  const results = [];
  let needsSave = false;

  // Process each element
  for (const element of currentPage.elements) {
    // Skip buttons (will be handled at the end)
    if (element.type === 'button') {
      continue;
    }

    // Skip captcha text field (will be handled by LLM)
    if (element.name === 'captcha') {
      continue;
    }

    // Locate element
    const elementData = await locateElement(page, element);

    // Fill element
    const fillResult = await fillElement(page, elementData, userData, currentUrl);
    results.push(fillResult);

    // Check if we need to pause
    if (fillResult.needsUserInput) {
      console.log(`\n⚠️  PAUSE NEEDED: ${fillResult.message}`);
      needsSave = true;
      break;
    }

    if (fillResult.needsLLM) {
      console.log(`\n⤵️  LLM ASSISTANCE NEEDED: ${fillResult.message}`);
      return {
        needsLLM: true,
        message: fillResult.message,
        elementInfo: fillResult,
        results,
        needsSave
      };
    }
  }

  // Check if we need to save current progress
  if (needsSave) {
    return {
      needsUserInput: true,
      message: results.find(r => r.needsUserInput)?.message,
      results,
      needsSave: true,
      currentPage: currentPage.page_name
    };
  }

  return {
    success: true,
    currentPage: currentPage.page_name,
    completedElements: results.filter(r => r.success).length,
    totalElements: results.length
  };
}

/**
 * Get progress report
 */
function getProgressReport(yamlData) {
  const totalPages = yamlData.pages.length;
  const completedPages = sessionData.completedPages.length;

  return {
    applicationId: sessionData.applicationId,
    securityQuestion: sessionData.securityQuestion,
    securityAnswer: sessionData.securityAnswer,
    progress: `${completedPages}/${totalPages} pages completed`,
    completedPages: sessionData.completedPages,
    startDate: sessionData.startDate
  };
}

// Export functions for use in OpenClaw skill
module.exports = {
  parseYaml,
  parseCSV,
  fillPage,
  loadSession,
  saveSession,
  extractApplicationId,
  generateSecurityQA,
  saveCSVFile,
  getProgressReport,
  CONFIG
};
