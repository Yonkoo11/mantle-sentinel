// Sentinel — reads live verdicts from the registry on Mantle Sepolia. No backend, no wallet.

const RPC = "https://rpc.sepolia.mantle.xyz";
const REGISTRY = "0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae";
const EXPLORER_ADDR = "https://sepolia.mantlescan.xyz/address/";
const SAMPLE = "0x469C46486d44eE02BB5A8d4FE341e55d13f5dF25";

const ABI = [
  "function count(address) view returns (uint256)",
  "function latest(address) view returns (tuple(address auditor,bool pass,uint16 vulnCount,uint8 highestSeverity,uint256 erc8004AgentId,bytes32 reportHash,string ipfsCID,uint64 timestamp))",
];
const SEV = ["none", "informational", "low", "medium", "high", "critical"];
// highest-severity -> letter grade + 0..100 score + tone
const GRADE = [
  { g: "A", s: 98, tone: "ok" }, { g: "A", s: 92, tone: "ok" }, { g: "B", s: 82, tone: "ok" },
  { g: "C", s: 68, tone: "med" }, { g: "D", s: 46, tone: "bad" }, { g: "F", s: 22, tone: "bad" },
];

// Curated evidence for the sample (our VulnerableVault) — the real flagged finding + code.
const SAMPLE_DETAIL = {
  sev: [{ label: "HIGH", n: 1, cls: "high" }, { label: "INFO", n: 2, cls: "info" }],
  excerptLabel: "reentrancy-eth · withdraw() · VulnerableVault.sol:13–18",
  code: [
    { n: 13, flag: false, parts: [["function ", "kw"], ["withdraw", "fn"], ["(uint256 amount) external {", ""]] },
    { n: 14, flag: false, parts: [["  require(balances[msg.sender] >= amount, ", ""], ["\"insufficient\"", "st"], [");", ""]] },
    { n: 15, flag: true, parts: [["  (bool ok,) = msg.sender.call{value: amount}(", ""], ["\"\"", "st"], [");", ""], ["  // external call first", "cm"]] },
    { n: 16, flag: false, parts: [["  require(ok, ", ""], ["\"send failed\"", "st"], [");", ""]] },
    { n: 17, flag: true, parts: [["  balances[msg.sender] -= amount;", ""], ["  // state written AFTER the call", "cm"]] },
    { n: 18, flag: false, parts: [["}", ""]] },
  ],
};

const $ = (id) => document.getElementById(id);
const provider = new ethers.JsonRpcProvider(RPC);
const registry = new ethers.Contract(REGISTRY, ABI, provider);

function setStatus(msg, kind = "") { const el = $("status"); el.textContent = msg; el.className = "status " + kind; }
function short(a) { return a.slice(0, 6) + "…" + a.slice(-4); }
function fmtTime(ts) { return new Date(Number(ts) * 1000).toISOString().slice(0, 16).replace("T", " ") + " UTC"; }

function renderSevStrip(items) {
  const el = $("sevstrip"); el.replaceChildren();
  for (const it of items) {
    const s = document.createElement("span");
    s.className = "sev " + it.cls;
    const b = document.createElement("b"); b.textContent = it.n;
    s.append(it.label + " ", b);
    el.appendChild(s);
  }
}

function renderCode(lines) {
  const pre = $("code"); pre.replaceChildren();
  for (const line of lines) {
    const div = document.createElement("span");
    div.className = "ln" + (line.flag ? " flag" : "");
    const num = document.createElement("span");
    num.className = "num"; num.textContent = String(line.n).padStart(2, " ");
    div.appendChild(num);
    for (const [text, cls] of line.parts) {
      const t = document.createElement("span");
      if (cls) t.className = cls;
      t.textContent = text;
      div.appendChild(t);
    }
    pre.appendChild(div);
  }
}

function renderLinks(address, agentId) {
  const el = $("links"); el.replaceChildren();
  const a = document.createElement("a");
  a.target = "_blank"; a.rel = "noopener"; a.href = EXPLORER_ADDR + address;
  a.textContent = "subject ↗"; el.appendChild(a);
  if (agentId && agentId !== 0n) {
    const r = document.createElement("a");
    r.target = "_blank"; r.rel = "noopener";
    r.href = "https://sepolia.mantlescan.xyz/address/0x8004B663056A597Dffe9eCcC1965A193B7388713";
    r.textContent = `ERC-8004 #${agentId} ↗`; el.appendChild(r);
  }
}

async function check(address, isInitial) {
  const cred = $("credential");
  setStatus(isInitial ? "" : "Reading the verdict from Mantle…", isInitial ? "" : "loading");
  try {
    const n = await registry.count(address);
    if (n === 0n) { setStatus("No audit on record for this contract yet.", "warn"); return; }
    const a = await registry.latest(address);
    const sevN = Number(a.highestSeverity);
    const grade = GRADE[sevN] || GRADE[5];

    $("grade").textContent = grade.g;
    $("grade").style.color = grade.tone === "bad" ? "var(--red)" : grade.tone === "med" ? "var(--amber)" : "var(--green)";
    $("verdict-pill").textContent = a.pass ? "PASS" : "FAIL";
    $("verdict-pill").className = "pill " + (a.pass ? "ok" : "bad");
    $("score").textContent = grade.s;
    $("verdict-target").textContent = short(address);
    $("r-hash").textContent = short(a.reportHash);
    $("r-agent").textContent = a.erc8004AgentId === 0n ? "not bound" : "agent #" + a.erc8004AgentId.toString();
    $("r-time").textContent = fmtTime(a.timestamp);
    $("r-auditor").textContent = short(a.auditor);

    const isSample = address.toLowerCase() === SAMPLE.toLowerCase();
    if (isSample) {
      renderSevStrip(SAMPLE_DETAIL.sev);
      $("excerpt-label").textContent = SAMPLE_DETAIL.excerptLabel;
      renderCode(SAMPLE_DETAIL.code);
      $("excerpt").style.display = "";
    } else {
      renderSevStrip([
        { label: "FINDINGS", n: a.vulnCount.toString(), cls: sevN >= 4 ? "high" : sevN === 3 ? "med" : "info" },
        { label: "TOP", n: SEV[sevN] || sevN, cls: sevN >= 4 ? "high" : sevN === 3 ? "med" : "info" },
      ]);
      $("excerpt").style.display = "none";
    }
    renderLinks(address, a.erc8004AgentId);

    if (!isInitial) { cred.classList.remove("enter"); void cred.offsetWidth; cred.classList.add("enter"); }
    setStatus("");
  } catch (e) {
    setStatus("Could not read the verdict: " + (e.shortMessage || e.message), "err");
  }
}

$("check").addEventListener("click", () => check($("addr").value.trim(), false));
$("addr").addEventListener("keydown", (e) => { if (e.key === "Enter") check($("addr").value.trim(), false); });
$("sample").addEventListener("click", () => { $("addr").value = SAMPLE; check(SAMPLE, false); });

const reg = $("reg-link"); reg.textContent = short(REGISTRY); reg.href = EXPLORER_ADDR + REGISTRY;

// populate the credential on load with the live sample verdict
check(SAMPLE, true);
