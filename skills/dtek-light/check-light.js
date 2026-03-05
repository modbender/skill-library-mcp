const { chromium } = require("playwright");
const os = require("os");
const path = require("path");

// Detect Chromium path based on platform
function getChromiumPath() {
  const cacheDir = path.join(os.homedir(), "Library", "Caches", "ms-playwright");
  const fs = require("fs");

  // Find any chromium directory (not headless_shell)
  try {
    const dirs = fs.readdirSync(cacheDir).filter((d) => d.startsWith("chromium-") && !d.includes("headless"));
    if (dirs.length > 0) {
      const chromiumDir = path.join(cacheDir, dirs[dirs.length - 1]);
      const macPath = path.join(chromiumDir, "chrome-mac", "Chromium.app", "Contents", "MacOS", "Chromium");
      if (fs.existsSync(macPath)) return macPath;
      const macArmPath = path.join(chromiumDir, "chrome-mac-arm64", "Chromium.app", "Contents", "MacOS", "Chromium");
      if (fs.existsSync(macArmPath)) return macArmPath;
    }
  } catch {}

  return undefined; // Let Playwright find it
}

(async () => {
  const executablePath = getChromiumPath();
  const launchOptions = { headless: true };
  if (executablePath) launchOptions.executablePath = executablePath;

  const browser = await chromium.launch(launchOptions);
  const context = await browser.newContext({
    locale: "uk-UA",
    viewport: { width: 1280, height: 900 },
    userAgent:
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/131.0.0.0 Safari/537.36",
  });
  const page = await context.newPage();

  try {
    await page.goto("https://www.dtek-oem.com.ua/ua/shutdowns", {
      waitUntil: "networkidle",
      timeout: 30000,
    });
    await page.waitForTimeout(3000);

    // Close modal with Escape
    await page.keyboard.press("Escape");
    await page.waitForTimeout(1000);

    // === CITY: type "Одес" and select "м. Одеса" ===
    const cityInput = page.locator("#discon_form #city");
    await cityInput.click();
    await cityInput.pressSequentially("Одес", { delay: 150 });
    await page.waitForTimeout(2000);

    // Click the first autocomplete item for city
    const cityItem = page.locator("#cityautocomplete-list > div").first();
    await cityItem.waitFor({ state: "visible", timeout: 5000 });
    await cityItem.click();
    await page.waitForTimeout(2000);

    // === STREET: type "Чикаленка" and select from list ===
    const streetInput = page.locator("#discon_form #street");
    await streetInput.waitFor({ state: "attached", timeout: 5000 });

    // Wait for street input to become enabled
    await page.waitForFunction(
      () => !document.querySelector("#discon_form #street").disabled,
      { timeout: 10000 }
    );
    await page.waitForTimeout(500);

    await streetInput.click();
    await streetInput.pressSequentially("Чикаленка", { delay: 100 });
    await page.waitForTimeout(3000);

    // Click the first autocomplete item for street
    const streetItem = page.locator("#streetautocomplete-list > div").first();
    await streetItem.waitFor({ state: "visible", timeout: 5000 });
    await streetItem.click();
    await page.waitForTimeout(2000);

    // === HOUSE: type "43" and select from list ===
    const houseInput = page.locator("#discon_form #house_num");
    await houseInput.waitFor({ state: "attached", timeout: 5000 });

    // Wait for house input to become enabled
    await page.waitForFunction(
      () => !document.querySelector("#discon_form #house_num").disabled,
      { timeout: 10000 }
    );
    await page.waitForTimeout(500);

    await houseInput.click();
    await houseInput.pressSequentially("43", { delay: 150 });
    await page.waitForTimeout(3000);

    // Click the autocomplete item for house number
    const houseItem = page.locator("#house_numautocomplete-list > div").first();
    await houseItem.waitFor({ state: "visible", timeout: 5000 });
    await houseItem.click();

    // Wait for results to load
    await page.waitForTimeout(5000);

    // Read the result from page
    const pageText = await page.locator("body").innerText();

    const result = {};

    if (pageText.includes("відсутня електроенергія")) {
      result.status = "no_light";

      const startMatch = pageText.match(/Час початку\s*[–\-]\s*(\d{1,2}:\d{2}\s+\d{2}\.\d{2}\.\d{4})/);
      if (startMatch) result.start_time = startMatch[1].trim();

      const restoreMatch = pageText.match(
        /Орієнтовний час відновлення електроенергії\s*[–\-]\s*(?:до\s+)?(\d{1,2}:\d{2}\s+\d{2}\.\d{2}\.\d{4})/
      );
      if (restoreMatch) result.restore_time = restoreMatch[1].trim();

      const reasonMatch = pageText.match(/Причина:\s*(.+?)(?:\n|Час)/s);
      if (reasonMatch) result.reason = reasonMatch[1].trim();

      const updateMatch = pageText.match(
        /Дата оновлення інформації\s*[–\-]\s*(\d{1,2}:\d{2}\s+\d{2}\.\d{2}\.\d{4})/
      );
      if (updateMatch) result.update_time = updateMatch[1].trim();
    } else if (
      pageText.includes("імовірно виникла аварійна ситуація") ||
      pageText.includes("гарантує його наявність")
    ) {
      result.status = "light_on";
    } else {
      result.status = "unknown";
      // Extract text around the result area for debugging
      const showCurOutage = await page.locator("#showCurOutage").innerText().catch(() => "");
      const disconFact = await page.locator("#discon-fact").innerText().catch(() => "");
      result.showCurOutage = showCurOutage;
      result.disconFact = disconFact;
      result.page_snippet = pageText.substring(0, 2000);
    }

    console.log(JSON.stringify(result));
  } catch (err) {
    console.log(JSON.stringify({ status: "error", error: err.message }));
  } finally {
    await browser.close();
  }
})();
