"""Styling and small HTML helpers for the control room."""
from __future__ import annotations

import html

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Schibsted+Grotesk:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500&display=swap');
:root{--ink:#1B2A2F;--muted:#5C6B70;--bg:#EEF1EF;--panel:#FBFCFB;--line:#D5DCD8;
--cobalt:#2F5DA8;--ok:#2E7D5B;--warn:#B7791F;--bad:#B3372F;}
.stApp, .stApp p, .stApp label, .stApp li, .stApp td, .stApp th, .stApp input, .stApp textarea,
.stApp button, .stApp h1, .stApp h2, .stApp h3, .stApp h4 {font-family:'Schibsted Grotesk',system-ui,sans-serif;}
.block-container{padding-top:2.2rem;max-width:1240px;}
header[data-testid="stHeader"]{background:transparent;}

.hero h1{font-size:2.15rem;font-weight:700;letter-spacing:-.025em;margin:0 0 .25rem;color:var(--ink);}
.hero p{color:var(--muted);max-width:62ch;margin:0 0 .9rem;font-size:1.02rem;line-height:1.5;}
.env{display:flex;gap:8px;flex-wrap:wrap;margin-bottom:.4rem;}

.chip{display:inline-block;padding:2px 10px;border-radius:999px;font-size:.78rem;font-weight:600;border:1px solid var(--line);color:var(--muted);background:var(--panel);}
.chip.ok{color:var(--ok);border-color:#9CCDB6;background:#EAF5EF;}
.chip.warn{color:var(--warn);border-color:#E3C58B;background:#FBF3E1;}
.chip.bad{color:var(--bad);border-color:#E3A9A4;background:#FBEAE8;}
.chip.info{color:var(--cobalt);border-color:#A9BFE3;background:#E9EFFA;}

.rail{display:flex;align-items:flex-start;background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:20px 22px 14px;margin:12px 0 16px;overflow-x:auto;}
.node{flex:1 1 0;min-width:98px;position:relative;text-align:center;}
.node::before{content:"";position:absolute;top:13px;left:-50%;width:100%;height:2px;background:var(--line);}
.node:first-child::before{display:none;}
.node.done::before{background:var(--ok);}
.node.blocked::before,.node.failed::before{background:var(--bad);}
.dot{position:relative;z-index:1;width:28px;height:28px;border-radius:50%;margin:0 auto 8px;border:2px solid var(--line);background:var(--panel);
display:flex;align-items:center;justify-content:center;font-size:12.5px;font-weight:700;color:var(--muted);}
.node.gate .dot{border-radius:6px;}
.node.done .dot{background:var(--ok);border-color:var(--ok);color:#fff;}
.node.active .dot{border-color:var(--cobalt);color:var(--cobalt);animation:ring 1.6s ease-out infinite;}
.node.waiting .dot{background:var(--warn);border-color:var(--warn);color:#fff;letter-spacing:-1px;}
.node.blocked .dot,.node.failed .dot{background:var(--bad);border-color:var(--bad);color:#fff;}
.node.skipped .dot{border-style:dashed;}
.lbl{font-size:.84rem;font-weight:600;color:var(--ink);line-height:1.25;}
.sub{font-size:.76rem;color:var(--muted);margin-top:1px;}
.node.waiting .sub{color:var(--warn);font-weight:600;}
@keyframes ring{0%{box-shadow:0 0 0 0 rgba(47,93,168,.35);}100%{box-shadow:0 0 0 9px rgba(47,93,168,0);}}
@media (prefers-reduced-motion:reduce){.node.active .dot{animation:none;box-shadow:0 0 0 4px rgba(47,93,168,.18);}}

.banner{border:1px solid var(--line);border-left:4px solid var(--cobalt);background:var(--panel);border-radius:8px;padding:12px 16px;margin-bottom:14px;}
.banner b{display:block;margin-bottom:2px;}
.banner span{color:var(--muted);font-size:.93rem;}
.banner.ok{border-left-color:var(--ok);} .banner.warn{border-left-color:var(--warn);} .banner.bad{border-left-color:var(--bad);}

.sec{font-size:1.02rem;font-weight:700;margin:1.1rem 0 .4rem;color:var(--ink);}
.lead{font-size:1.02rem;line-height:1.55;max-width:70ch;color:var(--ink);}
.row{padding:5px 0;border-bottom:1px solid var(--line);font-size:.93rem;line-height:1.45;}
.row:last-child{border-bottom:none;}
.row .chip{margin-right:8px;}
.kv{display:flex;gap:18px;flex-wrap:wrap;margin:.3rem 0 .6rem;}
.kv div{font-size:.84rem;color:var(--muted);} .kv b{display:block;color:var(--ink);font-size:1rem;}

.trace{background:var(--panel);border:1px solid var(--line);border-radius:10px;padding:12px 14px;}
.tl{display:flex;gap:10px;font-size:.8rem;line-height:1.75;align-items:baseline;}
.tt{font-family:'JetBrains Mono',monospace;color:var(--muted);min-width:46px;}
.tg{font-family:'JetBrains Mono',monospace;font-weight:500;min-width:78px;}
.tg.done{color:var(--ok);} .tg.active{color:var(--cobalt);} .tg.waiting{color:var(--warn);}
.tg.blocked,.tg.failed{color:var(--bad);} .tg.skipped{color:var(--muted);}
.mono{font-family:'JetBrains Mono',monospace;font-size:.82rem;}

div[data-testid="stTabs"] button[role="tab"]{font-weight:600;}
div[data-testid="stMetric"]{background:var(--panel);border:1px solid var(--line);border-radius:8px;padding:10px 14px;}
</style>
"""


def esc(value) -> str:
    return html.escape(str(value))


def nice(value: str) -> str:
    return str(value).replace("_", " ").capitalize()


def chip(text: str, kind: str = "") -> str:
    return f'<span class="chip {kind}">{esc(text)}</span>'


SEVERITY_KIND = {"LOW": "", "MEDIUM": "warn", "HIGH": "bad", "CRITICAL": "bad"}
STATE_TEXT = {
    "pending": "", "active": "Running", "done": "Done", "waiting": "Waiting for you",
    "blocked": "Stopped", "failed": "Failed", "skipped": "Skipped",
}
STATE_MARK = {"done": "&#10003;", "blocked": "&#10005;", "failed": "&#10005;", "waiting": "II", "skipped": "&ndash;"}


def rail(stages: list[dict], states: dict[str, str]) -> str:
    """One horizontal rail. The review stage is square: it is the human checkpoint."""
    nodes = []
    for i, stage in enumerate(stages, start=1):
        state = states.get(stage["id"], "pending")
        gate = " gate" if stage["id"] == "review" else ""
        mark = STATE_MARK.get(state, str(i))
        sub = STATE_TEXT.get(state, "")
        if stage["id"] == "review" and state == "pending":
            sub = "Approval needed"
        nodes.append(
            f'<div class="node {state}{gate}"><div class="dot">{mark}</div>'
            f'<div class="lbl">{esc(stage["label"])}</div><div class="sub">{sub}</div></div>'
        )
    return f'<div class="rail">{"".join(nodes)}</div>'


def trace(events: list[dict]) -> str:
    if not events:
        return '<div class="trace"><div class="tl"><span class="tt"></span>Nothing has run yet.</div></div>'
    lines = "".join(
        f'<div class="tl"><span class="tt">+{e["t"]:.1f}s</span>'
        f'<span class="tg {e["state"]}">{esc(e["stage"])}</span><span>{esc(e["title"])}</span></div>'
        for e in events
    )
    return f'<div class="trace">{lines}</div>'


def banner(title: str, body: str, kind: str = "") -> str:
    return f'<div class="banner {kind}"><b>{esc(title)}</b><span>{esc(body)}</span></div>'
