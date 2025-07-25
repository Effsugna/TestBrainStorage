const puppeteer = require("puppeteer");
const fs = require("fs");
const readline = require("readline");

const rl = readline.createInterface({
  input: process.stdin,
  output: process.stdout,
});

function askQuestion(query) {
  return new Promise((resolve) => rl.question(query, resolve));
}

(async () => {
  const username = await askQuestion("Instagram username: ");
  const password = await askQuestion("Instagram password: ");

  console.log("Launching headless browser...");
  const browser = await puppeteer.launch({ headless: "new" });
  const page = await browser.newPage();

  await page.goto("https://www.instagram.com/accounts/login/", {
    waitUntil: "networkidle2",
  });

  await page.type("input[name='username']", username, { delay: 50 });
  await page.type("input[name='password']", password, { delay: 50 });

  await Promise.all([
    page.click("button[type='submit']"),
    page.waitForNavigation({ waitUntil: "networkidle2" }),
  ]);

  // 2FA
  try {
    await page.waitForSelector("input[name='verificationCode']", {
      timeout: 15000,
    });
    const code = await askQuestion("Enter the 2FA code you received: ");
    await page.type("input[name='verificationCode']", code, { delay: 50 });

    await page.waitForFunction(() => {
      const btns = [...document.querySelectorAll("button")];
      return btns.find(b => b.innerText.toLowerCase().includes("confirm"));
    }, { timeout: 10000 });

    const [confirmBtn] = await page.$x("//button[contains(text(), 'Confirm')]");
    if (confirmBtn) {
      await Promise.all([
        confirmBtn.click(),
        page.waitForNavigation({ waitUntil: "networkidle2" }),
      ]);
    } else {
      throw new Error("2FA confirm button not found.");
    }
  } catch (e) {
    console.log("No 2FA screen detected or handled manually.");
  }

  console.log("✅ Logged in.");

  // Start interactive terminal nav
  while (true) {
    const cmd = await askQuestion(`📍 Current Page: ${page.url()}\nWhat would you like to do next? (e.g. "goto saved", "extract", "exit") → `);

    if (cmd === "goto saved") {
      await page.goto(`https://www.instagram.com/${username}/saved/`, {
        waitUntil: "networkidle2",
      });
      console.log("📂 Navigated to Saved Posts.");
    }

    else if (cmd === "extract") {
      // Scroll to load posts
      let previousHeight = 0;
      try {
        while (true) {
          previousHeight = await page.evaluate("document.body.scrollHeight");
          await page.evaluate("window.scrollTo(0, document.body.scrollHeight)");
          await page.waitForTimeout(2000);
          const newHeight = await page.evaluate("document.body.scrollHeight");
          if (newHeight === previousHeight) break;
        }
      } catch {
        console.log("⚠️ Scrolling ended or failed.");
      }

      // Extract links
      const links = await page.evaluate(() => {
        return Array.from(document.querySelectorAll("a"))
          .map(a => a.href)
          .filter(href => href.includes("/p/"));
      });

      console.log(`\n🔗 Saved Post Links (${links.length} found):\n`);
      links.forEach(link => console.log(link));
    }

    else if (cmd === "exit") {
      break;
    }

    else {
      console.log("❓ Unknown command.");
    }
  }

  const cookies = await page.cookies();
  fs.writeFileSync("cookies.json", JSON.stringify(cookies, null, 2));
  console.log("\n🍪 Session cookies saved as cookies.json");

  await browser.close();
  rl.close();
})();
