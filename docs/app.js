// Mantle Sentinel — read-only frontend. Reads live verdicts straight from the registry on
// Mantle Sepolia via a public RPC. No backend, no wallet needed to view a verdict.

const RPC = "https://rpc.sepolia.mantle.xyz";
const REGISTRY = "0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae";
const EXPLORER_ADDR = "https://sepolia.mantlescan.xyz/address/";
const SAMPLE = "0x469C46486d44eE02BB5A8d4FE341e55d13f5dF25"; // the audited demo target

const ABI = [
  "function count(address) view returns (uint256)",
  "function isAttestedSafe(address) view returns (bool)",
  "function latest(address) view returns (tuple(address auditor,bool pass,uint16 vulnCount,uint8 highestSeverity,uint256 erc8004AgentId,bytes32 reportHash,string ipfsCID,uint64 timestamp))",
];

const SEV = ["none", "informational", "low", "medium", "high", "critical"];

const $ = (id) => document.getElementById(id);
const provider = new ethers.JsonRpcProvider(RPC);
const registry = new ethers.Contract(REGISTRY, ABI, provider);

function setStatus(msg, kind = "") {
  const el = $("status");
  el.textContent = msg;
  el.className = "status " + kind;
}

function short(a) {
  return a.slice(0, 6) + "…" + a.slice(-4);
}

async function check(address) {
  $("result").classList.add("hidden");
  if (!ethers.isAddress(address)) {
    setStatus("That doesn't look like a valid address.", "err");
    return;
  }
  setStatus("Reading the verdict from Mantle…");
  try {
    const n = await registry.count(address);
    if (n === 0n) {
      setStatus("No audit on record for this contract yet.", "warn");
      return;
    }
    const a = await registry.latest(address);
    const safe = a.pass;
    $("verdict-pill").textContent = safe ? "PASS" : "FAIL";
    $("verdict-pill").className = "pill " + (safe ? "ok" : "bad");
    $("verdict-target").textContent = address;
    $("r-count").textContent = a.vulnCount.toString();
    $("r-sev").textContent = SEV[Number(a.highestSeverity)] || a.highestSeverity.toString();
    $("r-agent").textContent = a.erc8004AgentId === 0n ? "not registered" : "#" + a.erc8004AgentId.toString();
    const d = new Date(Number(a.timestamp) * 1000);
    $("r-time").textContent = d.toISOString().slice(0, 16).replace("T", " ") + " UTC";
    $("r-hash").textContent = a.reportHash;
    $("r-auditor").textContent = a.auditor;
    const linksEl = $("links");
    linksEl.replaceChildren();
    const explorerLink = document.createElement("a");
    explorerLink.target = "_blank";
    explorerLink.rel = "noopener";
    explorerLink.href = EXPLORER_ADDR + address;
    explorerLink.textContent = "target on explorer ↗";
    linksEl.appendChild(explorerLink);
    if (a.erc8004AgentId !== 0n) {
      const erc = document.createElement("span");
      erc.className = "erc";
      erc.textContent = `bound to ERC-8004 agent #${a.erc8004AgentId} reputation`;
      linksEl.appendChild(erc);
    }
    $("result").classList.remove("hidden");
    setStatus("");
  } catch (e) {
    setStatus("Could not read the verdict: " + (e.shortMessage || e.message), "err");
  }
}

$("check").addEventListener("click", () => check($("addr").value.trim()));
$("addr").addEventListener("keydown", (e) => { if (e.key === "Enter") check($("addr").value.trim()); });
$("sample").addEventListener("click", () => { $("addr").value = SAMPLE; check(SAMPLE); });

const reg = $("reg-link");
reg.textContent = short(REGISTRY);
reg.href = EXPLORER_ADDR + REGISTRY;
