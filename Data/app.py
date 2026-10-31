from functools import lru_cache
from pathlib import Path
from urllib.parse import quote
import base64
import html
import math
import re
import time
from datetime import date
from concurrent.futures import ThreadPoolExecutor

import numpy as np
import pandas as pd
import requests
import streamlit as st

# =========================================================
# FOOTEM ULTIMATE  v2
# Premium FIFA-style cards - Scout AI - Head-to-Head - Starting XI
# =========================================================

st.set_page_config(page_title="FOOTEM Ultimate", page_icon="⚽", layout="wide")

BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "players_fifa23.csv"

# ---------------------------------------------------------
# THEME / CSS
# ---------------------------------------------------------
CSS = """
@import url('https://fonts.googleapis.com/css2?family=Barlow+Condensed:wght@600;700;800;900&family=Inter:wght@400;500;600;700;800&family=JetBrains+Mono:wght@500;700;800&display=swap');
:root{--cy:#3df5ff;--lime:#c6ff3d;--mag:#ff4df0;--ink:#f5f8ff;--mut:#b4c2de;--panel:rgba(13,21,40,.82);--line:rgba(120,160,255,.26)}
.stApp{font-family:'Inter',sans-serif;color:var(--ink);background:
radial-gradient(1100px 600px at 6% -5%,rgba(61,245,255,.17),transparent 60%),
radial-gradient(900px 600px at 100% 0%,rgba(255,77,240,.15),transparent 55%),
linear-gradient(rgba(120,160,255,.055) 1px,transparent 1px),
linear-gradient(90deg,rgba(120,160,255,.055) 1px,transparent 1px),#060912;
background-size:auto,auto,46px 46px,46px 46px,auto;background-attachment:fixed}
[data-testid="stHeader"]{background:transparent}
.block-container{max-width:1500px;padding-top:1.4rem}
.stApp p,.stApp li,.stApp h1,.stApp h2,.stApp h3,.stApp h4,.stMarkdown{color:var(--ink)}
[data-testid="stCaptionContainer"],[data-testid="stCaptionContainer"] *{color:var(--mut)!important;font-size:.9rem}
[data-testid="stSidebar"]{background:#070d1a;border-right:1px solid var(--line)}
[data-testid="stSidebar"] *{color:var(--ink)}
[data-testid="stWidgetLabel"] p,label{color:#e4ecff!important;font-weight:700!important}
div[data-baseweb="select"]>div,.stTextInput input{background:#0d1526!important;color:#fff!important;border:1px solid #34508f!important;font-weight:600}
div[data-baseweb="select"] *{color:#fff!important}
li[role="option"]{background:#0d1526!important;color:#fff!important}
li[role="option"]:hover{background:#1d3160!important}
.stButton button,.stDownloadButton button{background:linear-gradient(90deg,var(--lime),var(--cy));color:#06101a!important;border:0;font-weight:800;border-radius:10px}
hr{border-color:var(--line)}
@keyframes pulse{0%,100%{opacity:1;transform:scale(1)}50%{opacity:.4;transform:scale(.7)}}
@keyframes flow{to{background-position:300% 0}}
@keyframes marquee{to{transform:translateX(-50%)}}
@keyframes fadein{to{opacity:1}}
@keyframes sheen{0%,55%{transform:translateX(-130%)}100%{transform:translateX(130%)}}
.badge{display:inline-flex;gap:9px;align-items:center;font:800 .78rem 'JetBrains Mono',monospace;color:var(--cy);letter-spacing:.14em;border:1px solid rgba(61,245,255,.5);background:rgba(61,245,255,.09);padding:6px 14px;border-radius:99px}
.dot{width:9px;height:9px;border-radius:50%;background:var(--lime);box-shadow:0 0 12px var(--lime);animation:pulse 1.6s infinite}
.hero{font-family:'Barlow Condensed',sans-serif;font-weight:900;font-size:clamp(3.4rem,7vw,6.4rem);line-height:.95;margin:10px 0 6px;color:#fff}
.hero span{background:linear-gradient(90deg,var(--cy),var(--lime),var(--mag),var(--cy));background-size:300% 100%;-webkit-background-clip:text;background-clip:text;color:transparent;animation:flow 9s linear infinite}
.sub{color:var(--mut);font-size:1.08rem;max-width:780px;margin-bottom:12px}
.ticker{overflow:hidden;border-top:1px solid var(--line);border-bottom:1px solid var(--line);background:rgba(8,14,28,.8);padding:9px 0;margin:12px 0 6px}
.ticker-track{display:inline-flex;gap:42px;white-space:nowrap;animation:marquee 60s linear infinite}
.ticker-track span{font:700 .92rem 'JetBrains Mono',monospace;color:#e6efff}
.ticker-track b{color:var(--lime)}
.sec{font:800 .86rem 'JetBrains Mono',monospace;letter-spacing:.18em;color:var(--lime);text-transform:uppercase;margin:18px 0 10px}
.sec::before{content:"";display:inline-block;width:5px;height:15px;background:var(--lime);margin-right:10px;vertical-align:-2px;box-shadow:0 0 12px var(--lime)}
.panel{background:var(--panel);border:1px solid var(--line);border-radius:16px;padding:18px 20px;backdrop-filter:blur(8px)}
.kpis{display:grid;grid-template-columns:repeat(auto-fit,minmax(180px,1fr));gap:14px;margin:10px 0}
.kpi{background:var(--panel);border:1px solid var(--line);border-radius:14px;padding:14px 18px;border-left:4px solid var(--cy)}
.kpi:nth-child(2){border-left-color:var(--lime)}.kpi:nth-child(3){border-left-color:var(--mag)}.kpi:nth-child(4){border-left-color:#ffd24a}.kpi:nth-child(5){border-left-color:#7c8cff}
.kpi b{display:block;font:900 2.7rem/1 'Barlow Condensed',sans-serif;color:#fff}
.kpi small{display:block;color:var(--mut);font-weight:700;font-size:.82rem;letter-spacing:.08em;margin-top:5px}
.info{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px}
.info div{background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:10px;padding:9px 12px}
.info small{display:block;color:var(--mut);font-weight:700;font-size:.74rem;letter-spacing:.08em}
.info b{font-size:1.02rem;color:#fff}
.report{font-family:'JetBrains Mono',monospace;background:#040813;border:1px solid rgba(61,245,255,.42);border-radius:14px;padding:16px 18px;color:#e2f8ff;font-size:.92rem;line-height:1.75;box-shadow:inset 0 0 36px rgba(61,245,255,.1)}
.report .ln{opacity:0;animation:fadein .5s forwards}
.report .hd{color:var(--cy);font-weight:800;letter-spacing:.1em}
.report b{color:var(--lime)}.report i{color:var(--mag);font-style:normal;font-weight:700}
.report .ft{color:#8ea3c9;font-size:.78rem;margin-top:6px}
.tag{display:inline-block;margin:3px 8px 3px 0;padding:6px 12px;border-radius:99px;font:800 .82rem 'JetBrains Mono',monospace;background:rgba(198,255,61,.12);border:1px solid rgba(198,255,61,.55);color:var(--lime)}
.sim{display:flex;align-items:center;gap:12px;background:rgba(255,255,255,.05);border:1px solid var(--line);border-radius:12px;padding:8px 12px;margin:7px 0}
.sim .ph{width:46px;height:46px;border-radius:50%;background-size:cover;background-position:center top;border:2px solid var(--cy);flex:none}
.sim .nm{flex:1;font-weight:700;color:#fff}.sim .nm small{display:block;color:var(--mut);font-weight:500}
.sim .ov{font:900 1.5rem 'Barlow Condensed',sans-serif;color:var(--lime)}
.sim .mt{font:800 .8rem 'JetBrains Mono',monospace;color:var(--cy);min-width:52px;text-align:right}
.radar svg{width:100%;max-width:430px;display:block;margin:auto}
.rl{fill:#a9bde8;font:800 13px 'JetBrains Mono',monospace;letter-spacing:.1em}
.rv{fill:#fff;font:900 21px 'Barlow Condensed',sans-serif}
.vs{display:grid;grid-template-columns:54px 1fr 64px 1fr 54px;align-items:center;gap:8px;margin:9px 0}
.vs b{font:900 1.5rem 'Barlow Condensed',sans-serif;color:#cfd9f2;text-align:center}
.vs b.win{color:var(--lime);text-shadow:0 0 12px rgba(198,255,61,.6)}
.vs span{font:800 .8rem 'JetBrains Mono',monospace;color:var(--mut);text-align:center}
.bar{height:13px;border-radius:99px;background:rgba(255,255,255,.09);overflow:hidden;display:flex}
.bar.l{justify-content:flex-end}.bar i{display:block;height:100%;border-radius:99px}
.podium{font:900 1.1rem 'Barlow Condensed',sans-serif;color:#06101a;background:linear-gradient(90deg,var(--lime),var(--cy));display:inline-block;padding:3px 14px;border-radius:99px;letter-spacing:.1em}
.fc-wrap{container-type:inline-size;width:100%;max-width:310px;margin:8px auto 18px;filter:drop-shadow(0 18px 22px rgba(0,0,0,.6));transition:transform .25s}
.fc-wrap:hover{transform:translateY(-7px) scale(1.025)}
.fc{position:relative;width:100%;aspect-ratio:300/430;overflow:hidden;color:var(--ink2);font-family:'Inter',sans-serif;clip-path:polygon(50% 0,86% 2.5%,100% 8%,100% 91%,50% 100%,0 91%,0 8%,14% 2.5%);background:linear-gradient(155deg,var(--b1),var(--b3) 48%,var(--b2))}
.fc::before{content:"";position:absolute;inset:0;background:radial-gradient(circle at 70% 28%,rgba(255,255,255,.4),transparent 55%),repeating-linear-gradient(115deg,rgba(255,255,255,.1) 0 2cqw,transparent 2cqw 7cqw)}
.fc::after{content:"";position:absolute;inset:0;background:linear-gradient(115deg,transparent 38%,rgba(255,255,255,.42) 50%,transparent 62%);animation:sheen 6s infinite;pointer-events:none}
.t-bronze{--b1:#f2bc8d;--b2:#a9622f;--b3:#e3a373;--ink2:#2a1304;--acc:#6b3a14}
.t-silver{--b1:#f7f9fb;--b2:#9eabba;--b3:#dfe6ed;--ink2:#121b26;--acc:#41546a}
.t-gold{--b1:#fff3be;--b2:#c99a1d;--b3:#f4d776;--ink2:#2b1d00;--acc:#7a5600}
.t-elite{--b1:#14407e;--b2:#050f26;--b3:#1d58b4;--ink2:#f0f8ff;--acc:#5fe8ff}
.t-icon{--b1:#5a2896;--b2:#0e0418;--b3:#8a3fd6;--ink2:#fff4c2;--acc:#ffd24a}
.fc-brand{position:absolute;top:3.4cqw;left:0;right:0;text-align:center;font:800 3cqw 'JetBrains Mono',monospace;letter-spacing:.5em;opacity:.85;z-index:2}
.fc-left{position:absolute;left:8cqw;top:15cqw;width:21cqw;text-align:center;z-index:3}
.ovr{font:900 19cqw/.9 'Barlow Condensed',sans-serif}
.pos{font:800 7cqw/1.2 'Barlow Condensed',sans-serif;letter-spacing:.06em}
.sep{width:13cqw;height:.8cqw;background:var(--ink2);opacity:.5;margin:2cqw auto 3cqw;border-radius:9px}
.flag{width:11cqw;height:7.4cqw;margin:0 auto 3cqw;background-size:cover;background-position:center;border-radius:1cqw;box-shadow:0 0 0 .5cqw rgba(0,0,0,.35)}
.club{width:11cqw;height:11cqw;margin:0 auto;border-radius:50%;border:.8cqw solid var(--ink2);display:flex;align-items:center;justify-content:center;font:900 3.6cqw 'Inter',sans-serif}
.fc-photo{position:absolute;right:3cqw;top:10cqw;width:66cqw;height:68cqw;background-size:contain,contain;background-repeat:no-repeat;background-position:center bottom;z-index:2;filter:drop-shadow(0 2cqw 2cqw rgba(0,0,0,.28))}
.fc-name{position:absolute;top:80cqw;left:5cqw;right:5cqw;text-align:center;font:900 11cqw/1 'Barlow Condensed',sans-serif;text-transform:uppercase;letter-spacing:.02em;white-space:nowrap;overflow:hidden;text-overflow:clip;z-index:3;padding-bottom:2cqw;border-bottom:.7cqw solid color-mix(in srgb,var(--ink2) 45%,transparent)}
.fc-name.sm{font-size:8.6cqw;padding-top:1.2cqw}.fc-name.xs{font-size:6.8cqw;padding-top:2.2cqw}
.fc-stats{position:absolute;top:94.5cqw;left:15cqw;right:15cqw;display:grid;grid-template-rows:repeat(3,auto);grid-auto-flow:column;gap:1cqw 0;z-index:3}
.st{display:flex;align-items:baseline;justify-content:center;gap:2.4cqw}
.st:nth-child(-n+3){border-right:.7cqw solid color-mix(in srgb,var(--ink2) 35%,transparent)}
.st b{font:900 9cqw/1.1 'Barlow Condensed',sans-serif}
.st span{font:800 5.4cqw/1.1 'Barlow Condensed',sans-serif;letter-spacing:.08em;opacity:.92}
.fc-meta{position:absolute;top:127cqw;left:0;right:0;text-align:center;font:800 3.6cqw 'JetBrains Mono',monospace;letter-spacing:.08em;z-index:3}
.pitch{position:relative;min-height:800px;border-radius:18px;border:3px solid rgba(255,255,255,.85);background:repeating-linear-gradient(0deg,#1c6a39 0 70px,#237a44 70px 140px);padding:28px 8px;display:flex;flex-direction:column;justify-content:space-between;overflow:hidden;box-shadow:0 0 60px rgba(61,245,255,.14)}
.pitch::before{content:"";position:absolute;left:50%;top:-90px;width:190px;height:190px;margin-left:-95px;border:3px solid rgba(255,255,255,.6);border-radius:50%}
.pitch::after{content:"";position:absolute;left:50%;bottom:0;width:60%;height:130px;margin-left:-30%;border:3px solid rgba(255,255,255,.6);border-bottom:0}
.pl-row{display:flex;justify-content:space-around;position:relative;z-index:1}
.chip{width:96px;text-align:center}
.chip-ph{position:relative;width:70px;height:70px;margin:auto;border-radius:50%;background-color:#0b1426;background-size:contain,contain;background-repeat:no-repeat;background-position:center bottom;border:3px solid var(--lime);box-shadow:0 6px 14px rgba(0,0,0,.45)}
.chip-ph em{position:absolute;top:-8px;left:-10px;min-width:30px;padding:2px 5px;border-radius:99px;background:#06101a;color:var(--lime);font:900 .98rem 'Barlow Condensed',sans-serif;font-style:normal;border:2px solid var(--lime)}
.chip-nm{margin-top:6px;background:#06101a;color:#fff;border-radius:7px;padding:3px 4px;font:800 .8rem 'Inter',sans-serif;overflow:hidden;white-space:nowrap;text-overflow:ellipsis}
.chip-rl{color:#fff;font:800 .72rem 'JetBrains Mono',monospace;margin-top:2px;text-shadow:0 1px 3px #000}
[data-testid="stSidebar"] div[role="radiogroup"]{gap:7px}
[data-testid="stSidebar"] div[role="radiogroup"]>label{width:100%;background:rgba(255,255,255,.04);border:1px solid var(--line);border-radius:12px;padding:11px 14px;margin:0;transition:all .18s;cursor:pointer}
[data-testid="stSidebar"] div[role="radiogroup"]>label>div:first-child{display:none}
[data-testid="stSidebar"] div[role="radiogroup"]>label:hover{background:rgba(61,245,255,.1);border-color:var(--cy);transform:translateX(4px)}
[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked){background:linear-gradient(90deg,rgba(61,245,255,.3),rgba(198,255,61,.14));border-color:var(--cy);box-shadow:0 0 20px rgba(61,245,255,.28)}
[data-testid="stSidebar"] div[role="radiogroup"]>label p{font-weight:800!important;font-size:1rem!important;color:#fff!important;margin:0}
.brand{font:900 2.3rem/1 'Barlow Condensed',sans-serif;color:#fff;letter-spacing:.02em}
.brand small{display:block;font:800 .7rem 'JetBrains Mono',monospace;letter-spacing:.2em;color:var(--cy);margin-top:6px}
.navlabel{font:800 .72rem 'JetBrains Mono',monospace;letter-spacing:.2em;color:var(--mut);margin:18px 0 9px}
.sstat{display:flex;justify-content:space-between;align-items:center;padding:9px 13px;border-radius:10px;background:rgba(255,255,255,.05);border:1px solid var(--line);margin:6px 0;font-weight:700;color:#dfe9ff}
.sstat b{font:900 1.35rem 'Barlow Condensed',sans-serif;color:var(--lime)}
[data-testid="stExpander"]{border:1px solid var(--line)!important;border-radius:12px;background:rgba(255,255,255,.03)}
[data-testid="stExpander"] summary p{color:#fff!important;font-weight:800!important}
.fc-wrap{perspective:900px}
.fc{transition:transform .3s ease}
.fc-wrap:hover .fc{transform:rotateY(-7deg) rotateX(5deg)}
.fc-glow{position:absolute;right:7cqw;top:11cqw;width:60cqw;height:60cqw;border-radius:50%;background:radial-gradient(circle,rgba(255,255,255,.6),transparent 68%);z-index:1}
.fc.t-icon::after,.fc.t-elite::after{background:linear-gradient(115deg,transparent 28%,rgba(255,77,240,.32) 40%,rgba(61,245,255,.4) 50%,rgba(198,255,61,.3) 60%,transparent 72%)}
.hbar{display:grid;grid-template-columns:118px 1fr 58px;gap:10px;align-items:center;margin:9px 0;font-weight:700;color:#e8f0ff;font-size:.95rem}
.hbar .tr{height:12px;background:rgba(255,255,255,.09);border-radius:99px;overflow:hidden}
.hbar .tr i{display:block;height:100%;background:linear-gradient(90deg,var(--cy),var(--lime));border-radius:99px}
.hbar em{font:800 .92rem 'JetBrains Mono',monospace;color:var(--lime);text-align:right;font-style:normal}
.hist{display:flex;align-items:flex-end;gap:6px;height:158px}
.hist div{flex:1;display:flex;flex-direction:column;justify-content:flex-end;align-items:center;gap:4px;height:100%}
.hist i{display:block;width:100%;background:linear-gradient(0deg,var(--cy),var(--mag));border-radius:6px 6px 0 0}
.hist b{font:800 .72rem 'JetBrains Mono',monospace;color:#fff}
.hist small{color:var(--mut);font:700 .74rem 'JetBrains Mono',monospace}
.ptitle{font:800 .82rem 'JetBrains Mono',monospace;letter-spacing:.14em;color:var(--cy);margin-bottom:10px}
@keyframes spin{to{transform:rotate(360deg)}}
@keyframes glowline{0%,100%{opacity:.55}50%{opacity:1}}
[data-testid="stSidebar"]{background:linear-gradient(180deg,#081124 0%,#060b18 55%,#0a0d22 100%);border-right:1px solid rgba(61,245,255,.28);box-shadow:6px 0 40px rgba(61,245,255,.07)}
[data-testid="stSidebar"]::before{content:"";position:absolute;left:0;top:0;right:0;height:3px;background:linear-gradient(90deg,var(--cy),var(--lime),var(--mag));animation:glowline 3s infinite}
.sb-brand{display:flex;align-items:center;gap:14px;padding-top:6px}
.sb-orb{position:relative;width:58px;height:58px;border-radius:17px;overflow:hidden;display:grid;place-items:center;flex:none}
.sb-orb::before{content:"";position:absolute;inset:-60%;background:conic-gradient(var(--cy),var(--lime),var(--mag),var(--cy));animation:spin 6s linear infinite}
.sb-orb::after{content:"";position:absolute;inset:3px;border-radius:14px;background:#070d1a}
.sb-orb span{position:relative;z-index:2;font-size:1.8rem}
.sb-title{font:900 2.4rem/.95 'Barlow Condensed',sans-serif;color:#fff;letter-spacing:.03em}
.sb-sub{font:800 .66rem 'JetBrains Mono',monospace;letter-spacing:.2em;color:var(--cy);margin-top:5px}
.sb-status{display:flex;align-items:center;gap:9px;margin:16px 0 2px;padding:9px 12px;border-radius:10px;background:rgba(198,255,61,.08);border:1px solid rgba(198,255,61,.42);font:800 .72rem 'JetBrains Mono',monospace;color:var(--lime);letter-spacing:.12em}
.sb-status em{margin-left:auto;font-style:normal;color:var(--mut)}
[data-testid="stSidebar"] div[role="radiogroup"]>label{position:relative;overflow:hidden;padding:12px 16px 12px 20px}
[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked)::before{content:"";position:absolute;left:0;top:18%;bottom:18%;width:5px;border-radius:5px;background:var(--lime);box-shadow:0 0 14px var(--lime)}
[data-testid="stSidebar"] div[role="radiogroup"]>label:has(input:checked) p{color:var(--lime)!important}
.potd{border-radius:16px;padding:14px;background:linear-gradient(150deg,rgba(61,245,255,.2),rgba(255,77,240,.15));border:1px solid rgba(61,245,255,.5);box-shadow:0 0 26px rgba(61,245,255,.12)}
.potd-top{display:flex;align-items:center;gap:12px}
.potd-ph{width:66px;height:66px;border-radius:50%;flex:none;background-color:#0b1426;background-size:cover;background-position:center 12%;background-repeat:no-repeat;border:3px solid var(--lime);box-shadow:0 0 18px rgba(198,255,61,.5)}
.potd-tx{flex:1;min-width:0}
.potd-nm{font-weight:800;color:#fff;font-size:1rem;line-height:1.15}
.potd-meta{color:var(--mut);font-size:.78rem;font-weight:600;margin-top:2px}
.potd-ovr{font:900 2.7rem/1 'Barlow Condensed',sans-serif;color:var(--lime);text-shadow:0 0 14px rgba(198,255,61,.5)}
.potd-stats{display:grid;grid-template-columns:repeat(3,1fr);gap:7px;margin-top:12px}
.potd-stats div{text-align:center;background:rgba(0,0,0,.4);border-radius:9px;padding:6px 0;font:800 .7rem 'JetBrains Mono',monospace;color:var(--mut);letter-spacing:.1em}
.potd-stats b{display:block;font:900 1.35rem/1.1 'Barlow Condensed',sans-serif;color:#fff;letter-spacing:0}
.sb-grid{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.sb-tile{padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.05);border:1px solid var(--line);border-top:3px solid var(--cy)}
.sb-tile:nth-child(2){border-top-color:var(--lime)}.sb-tile:nth-child(3){border-top-color:var(--mag)}.sb-tile:nth-child(4){border-top-color:#ffd24a}
.sb-tile small{display:block;color:var(--mut);font:800 .64rem 'JetBrains Mono',monospace;letter-spacing:.14em}
.sb-tile b{font:900 1.75rem/1.1 'Barlow Condensed',sans-serif;color:#fff}
.sb-meter{margin-top:10px;padding:10px 12px;border-radius:12px;background:rgba(255,255,255,.05);border:1px solid var(--line)}
.sb-meter small{display:flex;justify-content:space-between;color:var(--mut);font:800 .64rem 'JetBrains Mono',monospace;letter-spacing:.14em;margin-bottom:7px}
.sb-meter small em{font-style:normal;color:var(--lime)}
.sb-meter .tr{height:9px;border-radius:99px;background:rgba(255,255,255,.1);overflow:hidden}
.sb-meter .tr i{display:block;height:100%;background:linear-gradient(90deg,var(--cy),var(--lime));border-radius:99px}
.sb-foot{text-align:center;color:#7f93bd;font:700 .66rem 'JetBrains Mono',monospace;letter-spacing:.16em;margin:20px 0 6px}
@media (prefers-reduced-motion:reduce){.fc::after,.ticker-track,.hero span,.dot{animation:none}}
"""
st.markdown("<style>" + CSS + "</style>", unsafe_allow_html=True)


def ui(markup):
    """Render HTML. Lines are stripped and joined so markdown never sees code blocks."""
    flat = "".join(line.strip() for line in markup.strip().splitlines())
    st.markdown(flat, unsafe_allow_html=True)


def sec(label):
    ui(f'<div class="sec">{html.escape(label)}</div>')


# ---------------------------------------------------------
# GENERAL HELPERS
# ---------------------------------------------------------
def norm(value):
    return re.sub(r"[^a-z0-9]", "", str(value).lower())


def find_col(data, candidates, exact=False):
    normalized = {norm(c): c for c in data.columns}
    for cand in candidates:
        key = norm(cand)
        if key in normalized:
            return normalized[key]
    if exact:
        return None
    for cand in candidates:
        key = norm(cand)
        if len(key) >= 4:
            for name, original in normalized.items():
                if key in name:
                    return original
    return None


def to_num(series):
    return pd.to_numeric(
        series.astype(str).str.extract(r"(-?\d+(?:\.\d+)?)")[0], errors="coerce"
    )


def txt(value, default="—"):
    if value is None:
        return default
    try:
        if pd.isna(value):
            return default
    except (TypeError, ValueError):
        pass
    value = str(value).strip()
    return default if value.lower() in ("", "nan", "none") else value


def money(value):
    s = txt(value, "")
    if not s:
        return "—"
    if re.search(r"[A-Za-z€£$]", s):
        return s
    try:
        n = float(s.replace(",", ""))
    except ValueError:
        return s
    if n >= 1e6:
        return f"€{n / 1e6:.1f}M"
    if n >= 1e3:
        return f"€{n / 1e3:.0f}K"
    return f"€{n:.0f}"


def tokens(*vals):
    s = " ".join(v for v in vals if isinstance(v, str))
    return frozenset(t for t in re.split(r"[^A-Z]+", s.upper()) if t)


def first_token(s):
    found = re.findall(r"[A-Z]+", str(s).upper())
    return found[0] if found else "—"


def show_df(data):
    try:
        st.dataframe(data, width="stretch", hide_index=True)
    except Exception:
        st.dataframe(data, use_container_width=True, hide_index=True)


# ---------------------------------------------------------
# DATA LOADING + DERIVED STATS
# ---------------------------------------------------------
OUT_LABELS = ["PAC", "SHO", "PAS", "DRI", "DEF", "PHY"]
OUT_KEYS = ["_pac", "_sho", "_pas", "_dri", "_def", "_phy"]
GK_LABELS = ["DIV", "HAN", "KIC", "REF", "SPD", "POS"]
GK_KEYS = ["_div", "_han", "_kic", "_ref", "_spd", "_gpo"]

DIRECT = {
    "_pac": ["PAC", "Pace", "Pace Total", "PaceTotal"],
    "_sho": ["SHO", "Shooting", "Shooting Total"],
    "_pas": ["PAS", "Passing", "Passing Total"],
    "_dri": ["DRI", "Dribbling", "Dribbling Total"],
    "_def": ["DEF", "Defending", "Defending Total"],
    "_phy": ["PHY", "Physic", "Physical", "Physicality", "Physicality Total"],
}
PARTS = {
    "_pac": [(["Acceleration"], .45), (["Sprint Speed"], .55)],
    "_sho": [(["Finishing"], .45), (["Shot Power"], .2), (["Long Shots"], .2),
             (["Volleys"], .05), (["Penalties"], .05)],
    "_pas": [(["Short Passing"], .35), (["Vision"], .2), (["Crossing"], .2),
             (["Long Passing"], .15), (["Curve"], .1)],
    "_dri": [(["Dribbling"], .5), (["Ball Control"], .3), (["Agility"], .1),
             (["Balance"], .05), (["Reactions"], .05)],
    "_def": [(["Interceptions"], .2), (["Heading Accuracy"], .1),
             (["Marking", "Defensive Awareness"], .3),
             (["Standing Tackle"], .3), (["Sliding Tackle"], .1)],
    "_phy": [(["Strength"], .5), (["Stamina"], .25), (["Aggression"], .15), (["Jumping"], .1)],
}
GK_DIRECT = {
    "_div": ["GK Diving", "GKDiving", "goalkeeping_diving"],
    "_han": ["GK Handling", "GKHandling", "goalkeeping_handling"],
    "_kic": ["GK Kicking", "GKKicking", "goalkeeping_kicking"],
    "_ref": ["GK Reflexes", "GKReflexes", "goalkeeping_reflexes"],
    "_gpo": ["GK Positioning", "GKPositioning", "goalkeeping_positioning"],
}


@st.cache_resource(show_spinner="Booting FOOTEM engine…")
def load_data(path_str, mtime):
    data = pd.read_csv(path_str, low_memory=False)

    cols = {
        "name": find_col(data, ["Known As", "KnownAs", "short_name", "ShortName", "Name",
                                "Player", "player_name", "LongName", "long_name", "Full Name"]),
        "full": find_col(data, ["Full Name", "LongName", "long_name", "Name"]),
        "overall": find_col(data, ["Overall", "OVR", "overall_rating"]),
        "potential": find_col(data, ["Potential"]),
        "age": find_col(data, ["Age"]),
        "best": find_col(data, ["Best Position", "BestPosition", "Position", "Pos"]),
        "positions": find_col(data, ["Positions Played", "Positions", "player_positions",
                                     "Player Positions"]),
        "club": find_col(data, ["Club Name", "Club", "club_name", "Team"]),
        "nation": find_col(data, ["Nationality", "Nation", "nationality_name", "Country"]),
        "photo": find_col(data, ["Image Link", "Photo", "image_url", "Image URL",
                                 "player_face_url", "player_face", "Player Image",
                                 "player_image", "picture", "headshot"]),
        "id": find_col(data, ["ID", "sofifa_id", "Player ID", "playerid", "Sofifa ID"]),
        "value": find_col(data, ["Value(in Euro)", "Value", "value_eur", "Market Value"]),
        "wage": find_col(data, ["Wage(in Euro)", "Wage", "wage_eur"]),
        "height": find_col(data, ["Height(in cm)", "Height", "height_cm"]),
        "weak_foot": find_col(data, ["Weak Foot Rating", "Weak Foot", "weak_foot"]),
        "skill_moves": find_col(data, ["Skill Moves", "skill_moves"]),
    }
    if not cols["name"]:
        return None, cols, False, None

    n = len(data)
    zero = pd.Series(0.0, index=data.index)

    def numcol(key):
        return to_num(data[cols[key]]) if cols[key] else pd.Series(np.nan, index=data.index)

    def blank(key):
        if cols[key]:
            return data[cols[key]].fillna("").astype(str)
        return pd.Series("", index=data.index)

    data["_name"] = data[cols["name"]].fillna("Unknown Player").astype(str)
    full_col = cols["full"] or cols["name"]
    data["_full"] = data[full_col].fillna("").astype(str)
    data["_overall"] = numcol("overall").fillna(0)
    data["_pot"] = numcol("potential").fillna(data["_overall"])
    data["_age"] = numcol("age").fillna(0)
    data["_club"] = blank("club").replace("", "—")
    data["_nation"] = blank("nation").replace("", "—")

    best, plist = blank("best"), blank("positions")
    data["_tokens"] = [tokens(b, p) for b, p in zip(best, plist)]
    pos = best.map(first_token)
    fallback = plist.map(first_token)
    data["_pos"] = np.where(pos == "—", fallback, pos)
    data["_gk"] = data["_pos"] == "GK"

    for key, aliases in DIRECT.items():
        col = find_col(data, aliases, exact=True)
        if col:
            data[key] = to_num(data[col]).fillna(0)
            continue
        total, weight = zero.copy(), 0.0
        for names, w in PARTS[key]:
            c = find_col(data, names)
            if c:
                total = total + to_num(data[c]).fillna(0) * w
                weight += w
        data[key] = (total / weight).round() if weight else zero

    has_gk = True
    for key, aliases in GK_DIRECT.items():
        col = find_col(data, aliases, exact=True)
        if col:
            data[key] = to_num(data[col]).fillna(0)
        else:
            data[key] = zero
            has_gk = False
    sprint = find_col(data, ["Sprint Speed", "SprintSpeed"], exact=True)
    data["_spd"] = to_num(data[sprint]).fillna(0) if sprint else data["_pac"]

    out = np.column_stack([data[k] for k in OUT_KEYS])
    gk = np.column_stack([data[k] for k in GK_KEYS])
    use_gk = (data["_gk"].to_numpy() & has_gk)[:, None]
    feats = np.where(use_gk, gk, out)
    for i in range(6):
        data[f"_f{i + 1}"] = feats[:, i]
    data["_gkmode"] = use_gk[:, 0]

    data = data.sort_values(["_overall", "_pot"], ascending=False,
                            kind="mergesort").reset_index(drop=True)
    data["_rank"] = data.index + 1
    data["_option"] = (
        data["_name"] + "  ·  " + data["_pos"] + "  ·  "
        + data["_overall"].astype(int).astype(str) + " OVR  ·  #" + data["_rank"].astype(str)
    )
    data["_search"] = (data["_name"] + " " + data["_full"] + " " + data["_club"]
                       + " " + data["_nation"]).str.lower()
    feats = np.column_stack([data[f"_f{i}"] for i in range(1, 7)]
                            + [data["_overall"] * 1.5, data["_gkmode"].astype(float) * 200])
    return data, cols, has_gk, feats


if not CSV_PATH.exists():
    st.error(f"Cannot find {CSV_PATH.name}. Put it in the same folder as app.py.")
    st.stop()

try:
    df, columns, HAS_GK, FEATS = load_data(str(CSV_PATH), CSV_PATH.stat().st_mtime)
except Exception as error:
    st.error(f"Could not read the CSV: {error}")
    st.stop()

if df is None or df.empty:
    st.error("Player-name column not detected or the CSV is empty.")
    st.stop()

@st.cache_resource
def club_strength(_n):
    g = df[df["_club"] != "—"].groupby("_club")["_overall"]
    out = g.apply(lambda x: x.nlargest(11).mean() if len(x) >= 11 else np.nan).dropna()
    return out.sort_values(ascending=False)


# ---------------------------------------------------------
# PHOTO SYSTEM  (CSV link -> sofifa ID -> web lookup -> avatar)
# ---------------------------------------------------------
@lru_cache(maxsize=2048)
def search_photo_url(player_name):
    if not player_name:
        return ""
    try:
        r = requests.get("https://www.thesportsdb.com/api/v1/json/123/searchplayers.php",
                         params={"p": player_name}, timeout=6)
        r.raise_for_status()
        for p in (r.json() or {}).get("player") or []:
            got = txt(p.get("strPlayer"), "")
            if got and (norm(player_name) in norm(got) or norm(got) in norm(player_name)):
                for key in ("strCutout", "strThumb", "strRender"):
                    url = p.get(key)
                    if url and url.startswith("https://"):
                        return url
    except Exception:
        pass
    return ""


@lru_cache(maxsize=512)
def avatar_uri(name):
    initials = "".join(w[0] for w in re.findall(r"[A-Za-z]+", name)[:2]).upper() or "?"
    svg = (
        '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 200 200">'
        '<circle cx="100" cy="72" r="36" fill="#000" fill-opacity=".30"/>'
        '<path d="M26 200C26 142 66 122 100 122s74 20 74 78z" fill="#000" fill-opacity=".30"/>'
        f'<text x="100" y="178" text-anchor="middle" font-family="Arial" font-weight="800" '
        f'font-size="34" fill="#fff" fill-opacity=".85">{html.escape(initials)}</text></svg>'
    )
    return "data:image/svg+xml;utf8," + quote(svg)


@lru_cache(maxsize=256)
def local_image(path_str):
    try:
        p = (BASE_DIR / path_str).resolve()
        mime = {".png": "image/png", ".jpg": "image/jpeg",
                ".jpeg": "image/jpeg", ".webp": "image/webp"}.get(p.suffix.lower())
        if mime and p.is_file() and BASE_DIR.resolve() in p.parents and p.stat().st_size < 1_500_000:
            return f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")
    except Exception:
        pass
    return ""


PHOTO_DIR = BASE_DIR / "photo_cache"
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36",
    "Referer": "https://sofifa.com/",
    "Accept": "image/avif,image/webp,image/png,image/*,*/*;q=0.8",
}
MIMES = {".png": "image/png", ".jpg": "image/jpeg", ".webp": "image/webp"}


@st.cache_resource
def photo_store():
    try:
        PHOTO_DIR.mkdir(exist_ok=True)
    except OSError:
        pass
    return {"mem": {}, "miss": {}}


def photo_key(row):
    if columns["id"]:
        try:
            return f"p{int(float(row.get(columns['id'])))}"
        except (TypeError, ValueError):
            pass
    return f"r{int(row['_rank'])}_{norm(row['_name'])[:16]}"


def candidate_urls(row):
    urls = []
    raw = txt(row.get(columns["photo"]), "") if columns["photo"] else ""
    if raw.startswith(("http://", "https://")):
        base = raw.replace("http://", "https://").replace("cdn.sofifa.com", "cdn.sofifa.net")
        if re.search(r"/\d{2}_\d+\.png$", base):
            for size in (PHOTO_SIZE, 120, 60, 180):
                urls.append(re.sub(r"(/\d{2}_)\d+(\.png)$", rf"\g<1>{size}\g<2>", base))
        else:
            urls.append(base)
    if columns["id"]:
        try:
            pid = f"{int(float(row.get(columns['id']))):06d}"
            for size in (PHOTO_SIZE, 120, 60):
                urls.append(f"https://cdn.sofifa.net/players/{pid[:3]}/{pid[3:]}/{FIFA_YEAR}_{size}.png")
        except (TypeError, ValueError):
            pass
    return list(dict.fromkeys(urls))[:5]


def fetch_one(store, key, urls, full_name, live):
    """Memory -> disk -> network. Runs safely inside worker threads."""
    if key in store["mem"]:
        return store["mem"][key]
    if time.time() - store["miss"].get(key, 0) < 600:
        return ""
    try:
        for p in PHOTO_DIR.glob(f"{key}.*"):
            mime = MIMES.get(p.suffix)
            if mime:
                uri = f"data:{mime};base64," + base64.b64encode(p.read_bytes()).decode("ascii")
                store["mem"][key] = uri
                return uri
    except OSError:
        pass

    def attempt(url_list):
        for u in url_list:
            try:
                r = requests.get(u, timeout=6, headers=HEADERS)
                ctype = r.headers.get("Content-Type", "").lower()
                if r.status_code == 200 and ctype.startswith("image/") and 400 < len(r.content) < 3_000_000:
                    ext = ".png" if "png" in ctype else ".webp" if "webp" in ctype else ".jpg"
                    try:
                        (PHOTO_DIR / f"{key}{ext}").write_bytes(r.content)
                    except OSError:
                        pass
                    return f"data:{MIMES[ext]};base64," + base64.b64encode(r.content).decode("ascii")
            except Exception:
                continue
        return ""

    uri = attempt(urls)
    if not uri and live and full_name:
        found = search_photo_url(full_name)
        if found:
            uri = attempt([found])
    if uri:
        store["mem"][key] = uri
    else:
        store["miss"][key] = time.time()
    return uri


def prefetch(rows):
    """Download all missing photos for these rows in parallel."""
    store = photo_store()
    jobs = []
    for r in rows:
        key = photo_key(r)
        if key not in store["mem"]:
            jobs.append((key, candidate_urls(r), r["_full"] or r["_name"]))
    if not jobs:
        return
    with ThreadPoolExecutor(max_workers=12) as pool:
        list(pool.map(lambda j: fetch_one(store, j[0], j[1], j[2], LIVE_LOOKUP), jobs))


def photo_uri(row):
    raw = txt(row.get(columns["photo"]), "") if columns["photo"] else ""
    if raw and not raw.startswith(("http://", "https://")):
        local = local_image(raw)
        if local:
            return local
    return fetch_one(photo_store(), photo_key(row), candidate_urls(row),
                     row["_full"] or row["_name"], LIVE_LOOKUP)


def bg_layers(row):
    uri = photo_uri(row)
    if uri:
        return f"url('{uri}')"
    return f"url('{avatar_uri(row['_name'])}')"


# ---------------------------------------------------------
# FLAGS / TIERS / CARD
# ---------------------------------------------------------
ISO = {norm(k): v for k, v in {
    "Argentina": "ar", "Brazil": "br", "Portugal": "pt", "France": "fr", "England": "gb-eng",
    "Scotland": "gb-sct", "Wales": "gb-wls", "Northern Ireland": "gb-nir", "Ireland": "ie",
    "Republic of Ireland": "ie", "Spain": "es", "Germany": "de", "Italy": "it",
    "Netherlands": "nl", "Belgium": "be", "Croatia": "hr", "Serbia": "rs", "Switzerland": "ch",
    "Austria": "at", "Denmark": "dk", "Sweden": "se", "Norway": "no", "Finland": "fi",
    "Iceland": "is", "Poland": "pl", "Czech Republic": "cz", "Slovakia": "sk", "Slovenia": "si",
    "Hungary": "hu", "Romania": "ro", "Bulgaria": "bg", "Greece": "gr", "Turkey": "tr",
    "Ukraine": "ua", "Russia": "ru", "Bosnia and Herzegovina": "ba", "Albania": "al",
    "North Macedonia": "mk", "Kosovo": "xk", "Montenegro": "me", "Georgia": "ge",
    "Armenia": "am", "Israel": "il", "Morocco": "ma", "Algeria": "dz", "Tunisia": "tn",
    "Egypt": "eg", "Senegal": "sn", "Ghana": "gh", "Nigeria": "ng", "Cameroon": "cm",
    "Ivory Coast": "ci", "Côte d'Ivoire": "ci", "Mali": "ml", "Guinea": "gn", "DR Congo": "cd",
    "Congo DR": "cd", "Congo": "cg", "South Africa": "za", "Zambia": "zm", "Gabon": "ga",
    "Burkina Faso": "bf", "Cape Verde": "cv", "Uruguay": "uy", "Chile": "cl", "Colombia": "co",
    "Peru": "pe", "Ecuador": "ec", "Paraguay": "py", "Venezuela": "ve", "Bolivia": "bo",
    "Mexico": "mx", "United States": "us", "USA": "us", "Canada": "ca", "Costa Rica": "cr",
    "Jamaica": "jm", "Honduras": "hn", "Panama": "pa", "Japan": "jp", "Korea Republic": "kr",
    "South Korea": "kr", "China PR": "cn", "China": "cn", "Australia": "au",
    "New Zealand": "nz", "Iran": "ir", "Saudi Arabia": "sa", "Qatar": "qa", "Iraq": "iq",
    "Uzbekistan": "uz", "India": "in",
}.items()}


def flag_url(nation):
    code = ISO.get(norm(nation))
    return f"https://flagcdn.com/w80/{code}.png" if code else ""


def tier_of(ovr):
    if ovr >= 90:
        return "icon"
    if ovr >= 85:
        return "elite"
    if ovr >= 75:
        return "gold"
    if ovr >= 65:
        return "silver"
    return "bronze"


def card_stats(row):
    labels = GK_LABELS if row["_gkmode"] else OUT_LABELS
    return [(l, int(row[f"_f{i + 1}"])) for i, l in enumerate(labels)]


def card_html(row):
    name = row["_name"]
    ovr = int(row["_overall"])
    pot = int(row["_pot"])
    age = int(row["_age"])
    club, nation = row["_club"], row["_nation"]
    t = tier_of(ovr)
    flag = flag_url(nation)
    flag_html = (f'<div class="flag" style="background-image:url(\'{flag}\')"></div>'
                 if flag else "")
    initials = "".join(w[0] for w in re.findall(r"[A-Za-z]+", club)[:3]).upper() or "FC"
    size = "xs" if len(name) > 18 else "sm" if len(name) > 13 else ""
    stats = "".join(f'<div class="st"><b>{v}</b><span>{l}</span></div>'
                    for l, v in card_stats(row))
    extra = ""
    if columns["weak_foot"] and columns["skill_moves"]:
        wf = txt(row.get(columns["weak_foot"]), "")
        sm = txt(row.get(columns["skill_moves"]), "")
        if wf and sm:
            extra = f" · WF {html.escape(wf[:1])} · SM {html.escape(sm[:1])}"
    return f"""
    <div class="fc-wrap"><div class="fc t-{t}">
    <div class="fc-brand">FOOTEM</div>
    <div class="fc-left">
    <div class="ovr">{ovr}</div><div class="pos">{html.escape(row["_pos"])}</div>
    <div class="sep"></div>{flag_html}
    <div class="club">{html.escape(initials)}</div>
    </div>
    <div class="fc-glow"></div>
    <div class="fc-photo" style="background-image:{bg_layers(row)}"></div>
    <div class="fc-name {size}">{html.escape(name)}</div>
    <div class="fc-stats">{stats}</div>
    <div class="fc-meta">AGE {age} · POT {pot}{extra}</div>
    </div></div>
    """


def render_card(row):
    ui(card_html(row))


def card_grid(items, ncols=4):
    """items: list of (caption, row)."""
    prefetch([r for _, r in items])
    for start in range(0, len(items), ncols):
        cols = st.columns(ncols)
        for col, (cap, row) in zip(cols, items[start:start + ncols]):
            with col:
                if cap:
                    ui(f'<div style="text-align:center"><span class="podium">{html.escape(cap)}</span></div>')
                render_card(row)


# ---------------------------------------------------------
# RADAR + REPORT + SIMILAR
# ---------------------------------------------------------
def radar_html(sets, labels):
    cx, cy, R = 180, 160, 100

    def pt(i, f):
        a = math.radians(-90 + 60 * i)
        return cx + R * f * math.cos(a), cy + R * f * math.sin(a)

    g = ""
    for f in (.25, .5, .75, 1):
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in (pt(i, f) for i in range(6)))
        g += f'<polygon points="{pts}" fill="none" stroke="rgba(150,180,255,.3)" stroke-width="1"/>'
    for i in range(6):
        x, y = pt(i, 1)
        g += f'<line x1="{cx}" y1="{cy}" x2="{x:.1f}" y2="{y:.1f}" stroke="rgba(150,180,255,.25)"/>'
    for vals, color in sets:
        pts = " ".join(f"{x:.1f},{y:.1f}" for x, y in
                       (pt(i, max(.04, min(1, v / 100))) for i, v in enumerate(vals)))
        g += (f'<polygon points="{pts}" fill="{color}" fill-opacity=".25" stroke="{color}" '
              f'stroke-width="2.6" stroke-linejoin="round"/>')
        for i, v in enumerate(vals):
            x, y = pt(i, max(.04, min(1, v / 100)))
            g += f'<circle cx="{x:.1f}" cy="{y:.1f}" r="3.6" fill="{color}"/>'
    for i, label in enumerate(labels):
        x, y = pt(i, 1.3)
        g += f'<text x="{x:.1f}" y="{y - 4:.1f}" text-anchor="middle" class="rl">{label}</text>'
        if len(sets) == 1:
            g += (f'<text x="{x:.1f}" y="{y + 17:.1f}" text-anchor="middle" class="rv">'
                  f'{int(sets[0][0][i])}</text>')
    return f'<div class="radar"><svg viewBox="0 0 360 330" xmlns="http://www.w3.org/2000/svg">{g}</svg></div>'


OUT_ARCH = {"PAC": "Speed demon", "SHO": "Clinical finisher", "PAS": "Creative playmaker",
            "DRI": "Elite ball-carrier", "DEF": "Defensive anchor", "PHY": "Physical powerhouse"}
GK_ARCH = {"DIV": "Shot-stopper", "HAN": "Safe pair of hands", "KIC": "Distribution specialist",
           "REF": "Reflex specialist", "SPD": "Sweeper-keeper", "POS": "Commanding presence"}


def scout_report(row):
    stats = card_stats(row)
    ovr, pot, age = int(row["_overall"]), int(row["_pot"]), int(row["_age"])
    best = max(stats, key=lambda s: s[1])
    worst = min(stats, key=lambda s: s[1])
    top2 = sorted(stats, key=lambda s: -s[1])[:2]
    arche = (GK_ARCH if row["_gkmode"] else OUT_ARCH).get(best[0], "All-rounder")
    top_pct = max(0.1, 100 - (df["_overall"] < ovr).mean() * 100)
    gap = pot - ovr
    if age and age <= 21 and gap >= 6:
        traj = "RISING STAR"
    elif age and age <= 25 and gap >= 3:
        traj = "DEVELOPING"
    elif age >= 31:
        traj = "VETERAN"
    else:
        traj = "PRIME"
    role = ("priority signing target" if gap >= 5 and age <= 23
            else "reliable first-team starter" if ovr >= 75 else "squad depth option")
    name = html.escape(row["_name"])
    lines = [
        '<span class="hd">▌SCOUT.ENGINE // ANALYSIS COMPLETE</span>',
        f'PLAYER ........ <b>{name}</b>',
        f'ARCHETYPE ..... <b>{arche}</b>',
        f'RANK .......... <b>#{int(row["_rank"]):,}</b> of {len(df):,} · TOP {top_pct:.1f}%',
        f'STRENGTHS ..... <b>{top2[0][0]} {top2[0][1]}</b> · <b>{top2[1][0]} {top2[1][1]}</b>',
        f'WEAK POINT .... <i>{worst[0]} {worst[1]}</i>',
        f'TRAJECTORY .... <b>{traj}</b> (potential {pot}, headroom {gap:+d})',
        f'VERDICT ....... best used as <b>{html.escape(row["_pos"])}</b> · {role}',
        '<span class="ft">Generated locally from the ratings in your CSV.</span>',
    ]
    body = "".join(f'<div class="ln" style="animation-delay:{i * .35:.2f}s">{l}</div>'
                   for i, l in enumerate(lines))
    return f'<div class="report">{body}</div>'


def similar_players(i, k=5):
    dist = np.linalg.norm(FEATS - FEATS[i], axis=1)
    dist[i] = np.inf
    idx = np.argsort(dist)[:k]
    prefetch([df.iloc[j] for j in idx])
    out = ""
    for j in idx:
        r = df.iloc[j]
        sim = 100 * math.exp(-dist[j] / 45)
        out += (f'<div class="sim"><div class="ph" style="background-image:{bg_layers(r)}"></div>'
                f'<div class="nm">{html.escape(r["_name"])}<small>{html.escape(r["_club"])} · '
                f'{html.escape(r["_pos"])}</small></div><div class="ov">{int(r["_overall"])}</div>'
                f'<div class="mt">{sim:.0f}%</div></div>')
    return out


def info_grid(row):
    items = [("CLUB", row["_club"]), ("NATION", row["_nation"]), ("POSITION", row["_pos"]),
             ("AGE", int(row["_age"]) or "—")]
    if columns["value"]:
        items.append(("MARKET VALUE", money(row.get(columns["value"]))))
    if columns["wage"]:
        items.append(("WAGE", money(row.get(columns["wage"]))))
    if columns["height"]:
        items.append(("HEIGHT", txt(row.get(columns["height"]))))
    items.append(("POTENTIAL", int(row["_pot"])))
    cells = "".join(f'<div><small>{k}</small><b>{html.escape(str(v))}</b></div>' for k, v in items)
    return f'<div class="info">{cells}</div>'


def pick_player(label, key, default=0):
    """Search box + short result list, so the browser never receives 18k options."""
    q = st.text_input(f"{label}: search", key=f"{key}_q",
                      placeholder="Type a name, club or nation, e.g. Mbappé, Haaland, Brazil").strip().lower()
    if q:
        idx = np.flatnonzero(df["_search"].str.contains(q, regex=False).to_numpy())[:60]
    else:
        idx = np.arange(min(60, len(df)))
    if len(idx) == 0:
        st.warning("No player found. Try a shorter name.")
        idx = np.array([default])
    start = 0 if q else min(default, len(idx) - 1)
    pos = st.selectbox(label, [int(i) for i in idx], index=start,
                       format_func=lambda k: df["_option"].iat[k],
                       key=f"{key}_s_{q}", label_visibility="collapsed")
    return pos, df.iloc[pos]


# ---------------------------------------------------------
# SCOUT AI  (natural-language player search)
# ---------------------------------------------------------
POS_WORDS = [
    ("goalkeeper", ["GK"]), ("keeper", ["GK"]),
    ("left back", ["LB", "LWB"]), ("right back", ["RB", "RWB"]),
    ("full back", ["LB", "RB", "LWB", "RWB"]), ("fullback", ["LB", "RB", "LWB", "RWB"]),
    ("centre back", ["CB"]), ("center back", ["CB"]), ("centre-back", ["CB"]),
    ("defender", ["CB", "LB", "RB", "LWB", "RWB"]),
    ("defensive mid", ["CDM"]), ("holding mid", ["CDM"]), ("attacking mid", ["CAM"]),
    ("left wing", ["LW", "LM"]), ("right wing", ["RW", "RM"]),
    ("winger", ["LW", "RW", "LM", "RM"]),
    ("midfielder", ["CM", "CDM", "CAM", "LM", "RM"]),
    ("striker", ["ST", "CF"]), ("forward", ["ST", "CF", "LW", "RW"]),
]
STAT_WORDS = [
    (["fast", "pace", "quick", "rapid", "speed"], "_pac", "PAC"),
    (["shoot", "finisher", "clinical", "scorer"], "_sho", "SHO"),
    (["passing", "playmaker", "creative", "vision"], "_pas", "PAS"),
    (["dribbl", "skillful", "tricky", "flair"], "_dri", "DRI"),
    (["tackl", "solid", "wall", "stopper"], "_def", "DEF"),
    (["strong", "physical", "powerful", "tank"], "_phy", "PHY"),
]
DEMONYMS = {"brazilian": "Brazil", "french": "France", "spanish": "Spain", "english": "England",
            "german": "Germany", "italian": "Italy", "portuguese": "Portugal",
            "argentine": "Argentina", "argentinian": "Argentina", "dutch": "Netherlands",
            "belgian": "Belgium", "indian": "India", "japanese": "Japan",
            "american": "United States", "croatian": "Croatia", "moroccan": "Morocco",
            "senegalese": "Senegal", "uruguayan": "Uruguay", "norwegian": "Norway"}


def find_entity(series, ql):
    names = [n for n in series.unique() if isinstance(n, str) and len(n) >= 4 and n != "—"]
    hits = [n for n in names if re.search(r"\b" + re.escape(n.lower()) + r"\b", ql)]
    hits.sort(key=len, reverse=True)
    return hits[0] if hits else None


def scout_query(q):
    ql = " " + q.lower().strip() + " "
    work = ql
    tags = []
    mask = pd.Series(True, index=df.index)

    def grab(pattern):
        nonlocal work
        m = re.search(pattern, work)
        if not m:
            return None
        work = work[:m.start()] + " " + work[m.end():]
        return int(m.group(1))

    ovr_max = grab(r"(?:rated|rating|ovr|overall)\s*(?:under|below|<)\s*(\d{2,3})")
    ovr_min = (grab(r"(?:rated|rating|ovr|overall)\s*(?:of|over|above|at least|>=|>)?\s*(\d{2,3})")
               or grab(r"(?:over|above|at least|min)\s*(\d{2,3})\s*(?:ovr|overall|rated|rating)")
               or grab(r"(\d{2,3})\s*\+"))
    pot_min = grab(r"(?:potential|pot)\s*(?:of|over|above|at least|>=|>)?\s*(\d{2,3})")
    age_min = grab(r"(?:over|above|older than)\s*(\d{2})\s*(?:years|yrs|yo|y/o|year)")
    age_max = (grab(r"(?:under|below|younger than|less than)\s*(\d{2})")
               or grab(r"\bu-?(\d{2})\b"))
    loose = grab(r"(?:over|above|at least)\s*(\d{2})\b")
    if loose:
        if loose >= 50:
            ovr_min = ovr_min or loose
        else:
            age_min = age_min or loose

    wanted = set()
    for phrase, poss in POS_WORDS:
        if phrase in work:
            wanted.update(poss)
            work = work.replace(phrase, " ")
    wanted.update(t.upper() for t in re.findall(
        r"\b(gk|cb|lb|rb|lwb|rwb|cdm|cm|cam|lm|rm|lw|rw|st|cf)\b", work))

    sort_keys = []
    for words, key, label in STAT_WORDS:
        if any(w in work for w in words):
            sort_keys.append((key, label))

    young = any(w in work for w in ["young", "wonderkid", "prospect", "talent", "future"])
    veteran = any(w in work for w in ["veteran", "experienced", "elder"])

    if ovr_min:
        mask &= df["_overall"] >= ovr_min
        tags.append(f"OVR ≥ {ovr_min}")
    if ovr_max:
        mask &= df["_overall"] <= ovr_max
        tags.append(f"OVR ≤ {ovr_max}")
    if pot_min:
        mask &= df["_pot"] >= pot_min
        tags.append(f"POT ≥ {pot_min}")
    if age_max:
        mask &= (df["_age"] > 0) & (df["_age"] < age_max)
        tags.append(f"AGE < {age_max}")
    elif young:
        mask &= (df["_age"] > 0) & (df["_age"] <= 21)
        tags.append("AGE ≤ 21 (young)")
    if age_min:
        mask &= df["_age"] > age_min
        tags.append(f"AGE > {age_min}")
    elif veteran:
        mask &= df["_age"] >= 31
        tags.append("AGE ≥ 31 (veteran)")
    if wanted:
        mask &= df["_pos"].isin(wanted)
        tags.append("POS: " + "/".join(sorted(wanted)))

    nat = next((n for d, n in DEMONYMS.items() if re.search(rf"\b{d}\b", ql)), None)
    nat = nat if nat and (df["_nation"].str.lower() == nat.lower()).any() else find_entity(
        df["_nation"], ql)
    if nat:
        mask &= df["_nation"].str.lower() == nat.lower()
        tags.append(f"NATION: {nat}")
    club = find_entity(df["_club"], ql)
    if club:
        mask &= df["_club"] == club
        tags.append(f"CLUB: {club}")

    if sort_keys:
        if "GK" not in wanted:
            mask &= ~df["_gk"]
        for key, _ in sort_keys:
            mask &= df[key] >= 70
        tags.append("SORT: " + " + ".join(l for _, l in sort_keys))

    res = df[mask].copy()
    if sort_keys:
        res["_score"] = sum(res[k] for k, _ in sort_keys) / len(sort_keys) + .3 * res["_overall"]
        res = res.sort_values("_score", ascending=False)
    elif young or ((pot_min or age_max) and not ovr_min):
        res = res.sort_values(["_pot", "_overall"], ascending=False)
    return res, tags


# ---------------------------------------------------------
# STARTING XI
# ---------------------------------------------------------
FORMATIONS = {
    "4-3-3": [["LW", "ST", "RW"], ["CM", "CM", "CM"], ["LB", "CB", "CB", "RB"], ["GK"]],
    "4-2-3-1": [["ST"], ["LW", "CAM", "RW"], ["CDM", "CDM"], ["LB", "CB", "CB", "RB"], ["GK"]],
    "4-4-2": [["ST", "ST"], ["LM", "CM", "CM", "RM"], ["LB", "CB", "CB", "RB"], ["GK"]],
    "3-5-2": [["ST", "ST"], ["LM", "CM", "CAM", "CM", "RM"], ["CB", "CB", "CB"], ["GK"]],
    "4-1-4-1": [["ST"], ["LM", "CM", "CM", "RM"], ["CDM"], ["LB", "CB", "CB", "RB"], ["GK"]],
    "3-4-3": [["LW", "ST", "RW"], ["LM", "CM", "CM", "RM"], ["CB", "CB", "CB"], ["GK"]],
}
ALIASES = {
    "GK": ["GK"], "LB": ["LB", "LWB"], "RB": ["RB", "RWB"], "CB": ["CB"],
    "CDM": ["CDM", "CM"], "CM": ["CM", "CDM", "CAM"], "CAM": ["CAM", "CM", "CF"],
    "LM": ["LM", "LW", "LWB"], "RM": ["RM", "RW", "RWB"],
    "LW": ["LW", "LM", "ST"], "RW": ["RW", "RM", "ST"], "ST": ["ST", "CF", "LW", "RW"],
}


def position_score(row, target):
    if row["_pos"] == target:
        return 100
    if target in row["_tokens"]:
        return 92
    for i, choice in enumerate(ALIASES.get(target, [target])):
        if choice == row["_pos"]:
            return 80 - i * 8
        if choice in row["_tokens"]:
            return 70 - i * 8
    return 0


def build_starting_xi(club_df, formation):
    pool = club_df.sort_values("_overall", ascending=False)
    used, xi = set(), []
    for line in FORMATIONS[formation]:
        for target in line:
            cand = pool[~pool.index.isin(used)]
            if cand.empty:
                return xi
            sub = cand[cand["_gk"] == (target == "GK")]
            if sub.empty:
                sub = cand
            scores = sub.apply(lambda r: position_score(r, target) * 1000 + r["_overall"], axis=1)
            idx = scores.idxmax()
            used.add(idx)
            xi.append((target, pool.loc[idx]))
    return xi


def pitch_html(xi, formation):
    prefetch([p for _, p in xi])
    rows, counter = "", 0
    for line in FORMATIONS[formation]:
        chips = ""
        for _ in line:
            if counter >= len(xi):
                break
            target, p = xi[counter]
            counter += 1
            nm = p["_name"].split()[-1] if len(p["_name"]) > 12 else p["_name"]
            chips += (f'<div class="chip"><div class="chip-ph" style="background-image:{bg_layers(p)}">'
                      f'<em>{int(p["_overall"])}</em></div><div class="chip-nm">{html.escape(nm)}</div>'
                      f'<div class="chip-rl">{target}</div></div>')
        rows += f'<div class="pl-row">{chips}</div>'
    return f'<div class="pitch">{rows}</div>'


# ---------------------------------------------------------
# SIDEBAR + HEADER
# ---------------------------------------------------------
valid = df.loc[df["_overall"] > 0, "_overall"]
PHOTO_SIZE, FIFA_YEAR, LIVE_LOOKUP = 120, 23, True
PAGES = {
    "🏠  Command Center": "Command Center",
    "🧠  Scout AI": "Scout AI",
    "⚔️  Head to Head": "Head to Head",
    "🏟️  Club Starting XI": "Club Starting XI",
    "🌱  Talent Radar": "Talent Radar",
    "🏆  Leaderboard": "Leaderboard",
}

with st.sidebar:
    ui("""
    <div class="sb-brand"><div class="sb-orb"><span>⚽</span></div>
    <div><div class="sb-title">FOOTEM</div><div class="sb-sub">ULTIMATE · SCOUT OS</div></div></div>
    <div class="sb-status"><span class="dot"></span>ENGINE ONLINE<em>v2.1</em></div>
    <div class="navlabel">MISSION CONTROL</div>
    """)
    nav_box = st.container()
    potd_box = st.container()
    stats_box = st.container()
    set_box = st.container()

with nav_box:
    page = PAGES[st.radio("Navigation", list(PAGES), label_visibility="collapsed")]

with set_box:
    ui('<div class="navlabel">SYSTEM</div>')
    with st.expander("⚙️  Photos & performance"):
        PHOTO_SIZE = st.selectbox("Photo quality", [240, 120, 60], index=1)
        FIFA_YEAR = st.selectbox("Game year (ID photo URLs)", [23, 24, 22, 21], index=0)
        LIVE_LOOKUP = st.checkbox("Web photo fallback", value=True,
                                  help="Used only when the CSV link and player-ID photo both fail.")
        st.caption("Photos are saved in the photo_cache folder and load instantly next time.")
        if st.button("Retry missing photos"):
            photo_store()["miss"].clear()
            st.rerun()
        if st.button("Clear photo cache"):
            photo_store()["mem"].clear()
            photo_store()["miss"].clear()
            for f in PHOTO_DIR.glob("*.*"):
                try:
                    f.unlink()
                except OSError:
                    pass
            st.rerun()

with potd_box:
    ui('<div class="navlabel">PLAYER OF THE DAY</div>')
    potd = df.iloc[int(date.today().strftime("%Y%m%d")) % min(60, len(df))]
    prefetch([potd])
    pills = "".join(f"<div><b>{v}</b>{l}</div>"
                    for l, v in sorted(card_stats(potd), key=lambda x: -x[1])[:3])
    ui(f"""
    <div class="potd"><div class="potd-top">
    <div class="potd-ph" style="background-image:{bg_layers(potd)}"></div>
    <div class="potd-tx"><div class="potd-nm">{html.escape(potd["_name"])}</div>
    <div class="potd-meta">{html.escape(potd["_pos"])} · {html.escape(potd["_club"])}</div></div>
    <div class="potd-ovr">{int(potd["_overall"])}</div></div>
    <div class="potd-stats">{pills}</div></div>
    """)

with stats_box:
    try:
        cached = len(list(PHOTO_DIR.glob("*.*")))
    except OSError:
        cached = 0
    cover = min(100.0, cached / max(len(df), 1) * 100)
    ui(f"""
    <div class="navlabel">LIVE DATABASE</div>
    <div class="sb-grid">
    <div class="sb-tile"><small>PLAYERS</small><b>{len(df):,}</b></div>
    <div class="sb-tile"><small>AVG OVR</small><b>{valid.mean():.1f}</b></div>
    <div class="sb-tile"><small>CLUBS</small><b>{df.loc[df["_club"] != "—", "_club"].nunique():,}</b></div>
    <div class="sb-tile"><small>ELITE 85+</small><b>{int((df["_overall"] >= 85).sum()):,}</b></div>
    </div>
    <div class="sb-meter"><small>PHOTO CACHE<em>{cached:,} / {len(df):,}</em></small>
    <div class="tr"><i style="width:{max(cover, 2):.1f}%"></i></div></div>
    <div class="sb-foot">FOOTEM OS · BUILD 2.1</div>
    """)

ui('<div class="badge"><span class="dot"></span>SCOUT ENGINE ONLINE</div>')
ui('<div class="hero">FOOTEM <span>ULTIMATE</span></div>')
ui('<div class="sub">Premium player cards, natural-language scouting, head-to-head radar '
   'analysis and auto-built starting elevens, powered by your FIFA dataset.</div>')

# ---------------------------------------------------------
# PAGES
# ---------------------------------------------------------
if page == "Command Center":
    n_clubs = df.loc[df["_club"] != "—", "_club"].nunique()
    n_nat = df.loc[df["_nation"] != "—", "_nation"].nunique()
    top = df.iloc[0]
    ui(f"""
    <div class="kpis">
    <div class="kpi"><b>{len(df):,}</b><small>PLAYERS</small></div>
    <div class="kpi"><b>{int(top["_overall"])}</b><small>TOP RATED · {html.escape(top["_name"])}</small></div>
    <div class="kpi"><b>{valid.mean():.1f}</b><small>AVERAGE OVERALL</small></div>
    <div class="kpi"><b>{n_clubs:,}</b><small>CLUBS</small></div>
    <div class="kpi"><b>{n_nat:,}</b><small>NATIONS</small></div>
    </div>
    """)
    items = "".join(f'<span>▲ {html.escape(r["_name"])} <b>{int(r["_overall"])}</b></span>'
                    for _, r in df.head(16).iterrows())
    ui(f'<div class="ticker"><div class="ticker-track">{items}{items}</div></div>')

    sec("Player spotlight")
    i, row = pick_player("Search any player (type a name)", "spot")
    c1, c2, c3 = st.columns([1, 1.1, 1.1], gap="large")
    with c1:
        render_card(row)
    with c2:
        stats = card_stats(row)
        ui('<div class="panel">' + radar_html([([v for _, v in stats], "#3df5ff")],
                                              [l for l, _ in stats]) + info_grid(row) + '</div>')
    with c3:
        ui(scout_report(row))
        sec("Similar players")
        ui(similar_players(i))

    sec("Database analytics")
    a1, a2, a3 = st.columns(3, gap="large")
    counts, _ = np.histogram(valid, bins=list(range(45, 100, 5)))
    mx = max(int(counts.max()), 1)
    hist = "".join(f'<div><b>{int(c):,}</b><i style="height:{int(c / mx * 100)}px"></i>'
                   f'<small>{45 + 5 * n}</small></div>' for n, c in enumerate(counts))
    nat = df.loc[df["_nation"] != "—", "_nation"].value_counts().head(7)
    nmx = int(nat.iloc[0]) if len(nat) else 1
    nat_html = "".join(f'<div class="hbar"><span>{html.escape(n)}</span><div class="tr">'
                       f'<i style="width:{c / nmx * 100:.0f}%"></i></div><em>{c:,}</em></div>'
                       for n, c in nat.items())
    strong = club_strength(len(df)).head(7)
    smax = float(strong.iloc[0]) if len(strong) else 100.0
    club_html = "".join(f'<div class="hbar"><span>{html.escape(n)}</span><div class="tr">'
                        f'<i style="width:{max(4, (v - 50) / max(smax - 50, 1) * 100):.0f}%"></i></div>'
                        f'<em>{v:.1f}</em></div>' for n, v in strong.items())
    with a1:
        ui(f'<div class="panel"><div class="ptitle">RATING DISTRIBUTION</div><div class="hist">{hist}</div></div>')
    with a2:
        ui(f'<div class="panel"><div class="ptitle">MOST REPRESENTED NATIONS</div>{nat_html}</div>')
    with a3:
        ui(f'<div class="panel"><div class="ptitle">STRONGEST CLUBS · TOP-11 AVERAGE</div>{club_html}</div>')

    sec("Top rated players")
    card_grid([(f"#{n + 1}", r) for n, (_, r) in enumerate(df.head(4).iterrows())], 4)

elif page == "Scout AI":
    sec("Scout AI · describe the player you want")
    q = st.text_input("Search in plain English",
                      value="young fast left winger under 23 rated above 80")
    st.caption("Examples: best goalkeeper over 85 · strong centre back rated above 80 · "
               "Brazilian playmaker under 25 · young talent Real Madrid")
    res, tags = scout_query(q)
    ui("".join(f'<span class="tag">{html.escape(t)}</span>' for t in
               (tags or ["NO FILTERS · SHOWING BEST OVERALL"])))
    st.markdown(f"**{len(res):,} players matched**")
    if res.empty:
        st.warning("No players matched. Relax a filter, such as a lower rating or older age limit.")
    else:
        card_grid([(f"#{n + 1}", r) for n, (_, r) in enumerate(res.head(8).iterrows())], 4)
        sec("Full result list")
        cols = [c for c in ["_name", "_pos", "_overall", "_pot", "_age", "_club", "_nation"]]
        view = res[cols].head(100).rename(columns={
            "_name": "Player", "_pos": "Pos", "_overall": "Overall", "_pot": "Potential",
            "_age": "Age", "_club": "Club", "_nation": "Nation"})
        show_df(view)

elif page == "Head to Head":
    sec("Head to head")
    ca, cb = st.columns(2)
    with ca:
        _, pa = pick_player("Player A", "pa", 0)
    with cb:
        _, pb = pick_player("Player B", "pb", min(1, len(df) - 1))
    prefetch([pa, pb])
    left, mid, right = st.columns([1, 1.25, 1], gap="large")
    with left:
        render_card(pa)
    with right:
        render_card(pb)
    with mid:
        sa, sb = card_stats(pa), card_stats(pb)
        labels = [a[0] if a[0] == b[0] else f"{a[0]}/{b[0]}" for a, b in zip(sa, sb)]
        rows = [(l, a[1], b[1]) for l, a, b in zip(labels, sa, sb)]
        rows += [("OVR", int(pa["_overall"]), int(pb["_overall"])),
                 ("POT", int(pa["_pot"]), int(pb["_pot"]))]
        wins_a = sum(a > b for _, a, b in rows)
        wins_b = sum(b > a for _, a, b in rows)
        bars = ""
        for l, a, b in rows:
            bars += (f'<div class="vs"><b class="{"win" if a > b else ""}">{a}</b>'
                     f'<div class="bar l"><i style="width:{min(a, 100)}%;background:#3df5ff"></i></div>'
                     f'<span>{l}</span>'
                     f'<div class="bar"><i style="width:{min(b, 100)}%;background:#ff4df0"></i></div>'
                     f'<b class="{"win" if b > a else ""}">{b}</b></div>')
        verdict = (f"{pa['_name']} leads in {wins_a} of {len(rows)} categories" if wins_a > wins_b
                   else f"{pb['_name']} leads in {wins_b} of {len(rows)} categories" if wins_b > wins_a
                   else "Dead even: both players win the same number of categories")
        ui('<div class="panel">' + radar_html(
            [([a[1] for a in sa], "#3df5ff"), ([b[1] for b in sb], "#ff4df0")], labels[:6])
           + f'<div style="text-align:center;font-weight:800;margin:4px 0 10px">'
             f'<span style="color:#3df5ff">■ {html.escape(pa["_name"])}</span> &nbsp; '
             f'<span style="color:#ff4df0">■ {html.escape(pb["_name"])}</span></div>'
           + bars + f'<div class="tag" style="display:block;text-align:center;margin-top:12px">'
                    f'{html.escape(verdict)}</div></div>')

elif page == "Club Starting XI":
    sec("Club starting XI")
    clubs = sorted(c for c in df["_club"].unique() if c != "—")
    if not clubs:
        st.error("Your CSV needs a Club or Club Name column for this feature.")
        st.stop()
    c1, c2 = st.columns(2)
    with c1:
        club = st.selectbox("Select club", clubs,
                            index=clubs.index("Real Madrid") if "Real Madrid" in clubs else 0)
    with c2:
        formation = st.selectbox("Select formation", list(FORMATIONS))
    squad = df[df["_club"] == club]
    st.caption(f"{club}: {len(squad)} players in your dataset. Picks use position fit first, then overall rating.")
    if len(squad) < 11:
        st.warning("This club has fewer than 11 players in the CSV, so a full XI is not possible.")
    xi = build_starting_xi(squad, formation)
    if not xi:
        st.error("Could not build a lineup for this club.")
        st.stop()

    def avg(group):
        vals = [p["_overall"] for t, p in xi if t in group]
        return f"{sum(vals) / len(vals):.1f}" if vals else "—"

    team = sum(p["_overall"] for _, p in xi) / len(xi)
    ui(f"""
    <div class="kpis">
    <div class="kpi"><b>{formation}</b><small>FORMATION</small></div>
    <div class="kpi"><b>{team:.1f}</b><small>TEAM OVERALL</small></div>
    <div class="kpi"><b>{avg({"LW", "RW", "ST", "CF"})}</b><small>ATTACK</small></div>
    <div class="kpi"><b>{avg({"CM", "CDM", "CAM", "LM", "RM"})}</b><small>MIDFIELD</small></div>
    <div class="kpi"><b>{avg({"LB", "RB", "CB", "LWB", "RWB", "GK"})}</b><small>DEFENCE + GK</small></div>
    </div>
    """)
    sec("Tactical pitch")
    ui(pitch_html(xi, formation))
    sec("Starting XI player cards")
    card_grid([(t, p) for t, p in xi], 4)
    sec("Starting XI table")
    lineup = pd.DataFrame([{
        "Role": t, "Player": p["_name"], "Natural position": p["_pos"],
        "Overall": int(p["_overall"]), "Potential": int(p["_pot"]),
        "Age": int(p["_age"]), "Club": p["_club"]} for t, p in xi])
    show_df(lineup)
    st.download_button("Download Starting XI CSV", lineup.to_csv(index=False).encode("utf-8"),
                       file_name=f"{re.sub(r'[^a-zA-Z0-9]+', '_', club)}_starting_xi.csv",
                       mime="text/csv")
    st.caption("This is a rating-based suggested XI from your CSV, not a verified match lineup.")

elif page == "Talent Radar":
    sec("Talent radar · future stars")
    t1, t2, t3 = st.columns(3)
    with t1:
        max_age = st.slider("Maximum age", 16, 30, 21)
    with t2:
        min_pot = st.slider("Minimum potential", 60, 95, 80)
    with t3:
        pos_f = st.selectbox("Position", ["All positions"] + sorted(df["_pos"].unique()))
    res = df[(df["_age"] > 0) & (df["_age"] <= max_age) & (df["_pot"] >= min_pot)]
    if pos_f != "All positions":
        res = res[res["_pos"] == pos_f]
    res = res.assign(_growth=res["_pot"] - res["_overall"]).sort_values(
        ["_pot", "_growth"], ascending=False)
    st.markdown(f"**{len(res):,} prospects found**")
    if res.empty:
        st.warning("No prospects match. Lower the potential or raise the age limit.")
    else:
        card_grid([(f"+{int(r['_growth'])} GROWTH", r) for _, r in res.head(8).iterrows()], 4)
        sec("Age vs potential")
        try:
            st.scatter_chart(res.head(400)[["_age", "_pot"]].rename(
                columns={"_age": "Age", "_pot": "Potential"}), x="Age", y="Potential")
        except Exception:
            pass
        table = res[["_name", "_pos", "_age", "_overall", "_pot", "_growth", "_club"]].head(100)
        table.columns = ["Player", "Pos", "Age", "Overall", "Potential", "Growth", "Club"]
        show_df(table)

elif page == "Leaderboard":
    sec("Leaderboard")
    c1, c2, c3 = st.columns(3)
    with c1:
        min_rating = st.slider("Minimum overall", 0, 100, 75)
    with c2:
        sel_pos = st.selectbox("Position", ["All positions"] + sorted(df["_pos"].unique()))
    with c3:
        max_rows = st.selectbox("Rows", [10, 25, 50, 100], index=1)
    flt = df[df["_overall"] >= min_rating]
    if sel_pos != "All positions":
        flt = flt[flt["_pos"] == sel_pos]
    flt = flt.head(max_rows)
    if flt.empty:
        st.warning("No players match these filters.")
    else:
        card_grid([(f"#{n + 1}", r) for n, (_, r) in enumerate(flt.head(4).iterrows())], 4)
        table = flt[["_name", "_pos", "_overall", "_pot", "_age", "_club", "_nation",
                     "_f1", "_f2", "_f3", "_f4", "_f5", "_f6"]].copy()
        table.columns = ["Player", "Pos", "Overall", "Potential", "Age", "Club", "Nation",
                         "Stat 1", "Stat 2", "Stat 3", "Stat 4", "Stat 5", "Stat 6"]
        table.insert(0, "Rank", range(1, len(table) + 1))
        show_df(table)
        st.download_button("Download leaderboard CSV", table.to_csv(index=False).encode("utf-8"),
                           file_name="footem_leaderboard.csv", mime="text/csv")
        st.caption("Stat 1-6 are PAC, SHO, PAS, DRI, DEF, PHY (or DIV, HAN, KIC, REF, SPD, POS for goalkeepers).")


st.divider()
st.caption("FOOTEM ULTIMATE · Ratings and lineups depend on your FIFA CSV. Photos use the CSV link, "
           "then a player-ID URL, then optional web lookup, then an initials avatar.")