// Sentinel registry explorer — reads every Attested event off Mantle Sepolia (chunked getLogs),
// dedupes to the latest verdict per contract, and renders the table + headline stats.

const RPC = "https://rpc.sepolia.mantle.xyz";
const REGISTRY = "0xbCE17E724c0Cd038622a9C4299F86Caf411C1Fae";
const EXPLORER_ADDR = "https://sepolia.mantlescan.xyz/address/";
const START_BLOCK = 39942134; // registry deploy block
const CHUNK = 4000;           // public RPC caps getLogs ranges (~5k); stay under

const EV_ABI = [
  "event Attested(address indexed auditedContract, address indexed auditor, bool pass, uint16 vulnCount, uint8 highestSeverity, uint256 erc8004AgentId, bytes32 reportHash, uint256 index)",
];
const SEV = ["none", "informational", "low", "medium", "high", "critical"];
const GRADE = [
  { g: "A", tone: "ok" }, { g: "A", tone: "ok" }, { g: "B", tone: "ok" },
  { g: "C", tone: "med" }, { g: "D", tone: "bad" }, { g: "F", tone: "bad" },
];

const $ = (id) => document.getElementById(id);
const short = (a) => a.slice(0, 6) + "…" + a.slice(-4);
const fmt = (ts) => new Date(Number(ts) * 1000).toISOString().slice(0, 10);

async function load() {
  const provider = new ethers.JsonRpcProvider(RPC);
  const reg = new ethers.Contract(REGISTRY, EV_ABI, provider);
  let latest;
  try { latest = await provider.getBlockNumber(); }
  catch (e) { $("reg-status").textContent = "Could not reach Mantle: " + (e.shortMessage || e.message); $("reg-status").className = "status err"; return; }

  // collect events in <=CHUNK windows
  const events = [];
  for (let from = START_BLOCK; from <= latest; from += CHUNK + 1) {
    const to = Math.min(from + CHUNK, latest);
    try { events.push(...await reg.queryFilter("Attested", from, to)); }
    catch (_) { /* skip a bad window, keep going */ }
  }

  // dedupe to latest verdict per contract (highest block, then logIndex)
  const byContract = new Map();
  for (const ev of events) {
    const a = ev.args;
    const key = a.auditedContract.toLowerCase();
    const prev = byContract.get(key);
    const rank = ev.blockNumber * 1e6 + (ev.index || 0);
    if (!prev || rank > prev.rank) {
      byContract.set(key, {
        rank, contract: a.auditedContract, pass: a.pass,
        sev: Number(a.highestSeverity), vulnCount: Number(a.vulnCount),
        agentId: a.erc8004AgentId, blockNumber: ev.blockNumber,
      });
    }
  }
  const rows = [...byContract.values()].sort((x, y) => y.rank - x.rank);

  // timestamps (one getBlock per row — fine for a small registry)
  await Promise.all(rows.map(async (r) => {
    try { r.ts = (await provider.getBlock(r.blockNumber)).timestamp; } catch (_) { r.ts = 0; }
  }));

  render(rows);
}

function render(rows) {
  $("s-total").textContent = rows.length;
  $("s-fail").textContent = rows.filter((r) => !r.pass).length;
  $("s-bound").textContent = rows.filter((r) => r.agentId && r.agentId !== 0n).length;

  const body = $("reg-body");
  body.replaceChildren();
  for (const r of rows) {
    const grade = GRADE[r.sev] || GRADE[5];
    const tr = document.createElement("tr");

    const g = document.createElement("td");
    const gb = document.createElement("span");
    gb.className = "rg rg-" + grade.tone; gb.textContent = grade.g; g.appendChild(gb);

    const c = document.createElement("td");
    c.className = "mono"; c.textContent = short(r.contract);

    const v = document.createElement("td");
    const vp = document.createElement("span");
    vp.className = "tag " + (r.pass ? "ok" : "bad"); vp.textContent = r.pass ? "PASS" : "FAIL";
    v.appendChild(vp);

    const s = document.createElement("td");
    s.className = "sev-" + (r.sev >= 4 ? "high" : r.sev === 3 ? "med" : "low");
    s.textContent = SEV[r.sev] || r.sev;

    const a = document.createElement("td");
    a.className = "mono"; a.textContent = r.agentId && r.agentId !== 0n ? "#" + r.agentId.toString() : "—";

    const t = document.createElement("td");
    t.className = "mono dim"; t.textContent = r.ts ? fmt(r.ts) : "—";

    const lk = document.createElement("td");
    const link = document.createElement("a");
    link.href = EXPLORER_ADDR + r.contract; link.target = "_blank"; link.rel = "noopener";
    link.textContent = "↗"; link.className = "rowlink"; lk.appendChild(link);

    tr.append(g, c, v, s, a, t, lk);
    body.appendChild(tr);
  }

  $("reg-status").hidden = true;
  $("reg-table").hidden = false;
  if (rows.length === 0) { $("reg-status").hidden = false; $("reg-status").className = "status warn"; $("reg-status").textContent = "No verdicts on record yet."; $("reg-table").hidden = true; }
}

load();
