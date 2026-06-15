// Capture 1920x1080 frames for the Sentinel demo video. Uses the installed Chrome.
// Drives the real live paste-audit (the money shot) against the deployed backend.
const puppeteer = require("puppeteer-core");
const path = require("path");

const CHROME = "/Users/yonko/.cache/puppeteer/chrome/mac_arm-146.0.7680.153/chrome-mac-arm64/Google Chrome for Testing.app/Contents/MacOS/Google Chrome for Testing";
const SITE = "https://yonkoo11.github.io/mantle-sentinel";
const OUT = path.join(__dirname, "frames");
const TX = "0x5965c8c763e7496931fd0aefb7ba5122ed241a8b88cdd663011813d3fc345ead"; // agent-186 reputation bind

const VULN = `// SPDX-License-Identifier: MIT
pragma solidity ^0.8.20;
contract Bank {
    mapping(address => uint) public bal;
    address owner;
    function deposit() external payable { bal[msg.sender] += msg.value; }
    function withdraw(uint a) external {
        require(bal[msg.sender] >= a);
        (bool ok,) = msg.sender.call{value: a}("");
        require(ok);
        bal[msg.sender] -= a;
    }
    function drain(address to) external { require(tx.origin == owner); payable(to).transfer(address(this).balance); }
}`;

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));

(async () => {
  const browser = await puppeteer.launch({ executablePath: CHROME, headless: true, args: ["--hide-scrollbars"] });
  const page = await browser.newPage();
  await page.setViewport({ width: 1920, height: 1080, deviceScaleFactor: 1 });

  async function shot(name) { await page.screenshot({ path: path.join(OUT, name) }); console.log("frame:", name); }

  // --- 01 + 02: the live audit money shot ---
  try {
    await page.goto(SITE + "/index.html", { waitUntil: "networkidle2", timeout: 60000 });
    await sleep(6000); // sample on-chain verdict loads
    await page.click("#paste-toggle");
    await sleep(400);
    await page.type("#source", VULN, { delay: 4 });
    await page.click("#check");
    // wait for the findings list to appear (backend round-trip)
    await page.waitForFunction(() => { const f = document.getElementById("findings"); return f && !f.hidden && f.children.length > 0; }, { timeout: 90000 });
    await sleep(800);
    await page.evaluate(() => window.scrollTo(0, 0));
    await sleep(300);
    await shot("01-grade.png");
    // scroll the credential's findings into view for clip 2
    await page.evaluate(() => { const el = document.getElementById("findings"); if (el) el.scrollIntoView({ block: "center" }); });
    await sleep(500);
    await shot("02-findings.png");
  } catch (e) { console.log("audit frames FAILED:", e.message); }

  // --- 04 + 05: registry table + dev snippet ---
  try {
    await page.goto(SITE + "/registry.html", { waitUntil: "networkidle2", timeout: 60000 });
    await sleep(12000); // chunked on-chain reads
    await page.evaluate(() => window.scrollTo(0, 0));
    await sleep(300);
    await shot("04-registry.png");
    await page.evaluate(() => { const el = document.querySelector(".dev"); if (el) el.scrollIntoView({ block: "start" }); });
    await sleep(500);
    await shot("05-dev.png");
  } catch (e) { console.log("registry frames FAILED:", e.message); }

  // --- 06: home hero (CTA close) ---
  try {
    await page.goto(SITE + "/index.html", { waitUntil: "networkidle2", timeout: 60000 });
    await sleep(6000);
    await page.evaluate(() => window.scrollTo(0, 0));
    await shot("06-hero.png");
  } catch (e) { console.log("hero frame FAILED:", e.message); }

  // --- 03: on-chain attestation tx on Mantlescan ---
  try {
    await page.goto("https://sepolia.mantlescan.xyz/tx/" + TX, { waitUntil: "domcontentloaded", timeout: 45000 });
    await sleep(5000);
    await shot("03-tx.png");
  } catch (e) { console.log("tx frame FAILED:", e.message); }

  await browser.close();
  console.log("done");
})();
