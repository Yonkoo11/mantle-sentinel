// Re-capture the registry frame, waiting until the on-chain rows actually render.
const puppeteer = require("puppeteer-core");
const path = require("path");
const CHROME = "/Users/yonko/.cache/puppeteer/chrome/mac_arm-146.0.7680.153/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
const OUT = path.join(__dirname, "frames");
const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const b = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--hide-scrollbars"] });
  const p = await b.newPage();
  await p.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });
  await p.goto("https://yonkoo11.github.io/mantle-sentinel/registry.html", { waitUntil: "networkidle2", timeout: 60000 });
  try {
    await p.waitForFunction(() => { const t = document.getElementById("reg-table"); return t && !t.hidden && t.querySelectorAll("tbody tr").length > 0; }, { timeout: 90000 });
    console.log("table populated");
  } catch (e) { console.log("table did not populate in time:", e.message); }
  await sleep(1200);
  await p.evaluate(() => window.scrollTo(0, 0));
  await sleep(300);
  await p.screenshot({ path: path.join(OUT, "04-registry.png") });
  // dev snippet region
  await p.evaluate(() => { const el = document.querySelector(".dev"); if (el) el.scrollIntoView({ block: "start" }); });
  await sleep(600);
  await p.screenshot({ path: path.join(OUT, "05-dev.png") });
  await b.close();
  console.log("done");
})();
