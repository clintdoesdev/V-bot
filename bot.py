"""
Vireon Africa Telegram Userbot + Live Dashboard
==========================================
Railway-ready. Uses StringSession so no .session file needed.

FLOW
----
A brand-new contact only enters the scripted funnel if their first message
matches the start prompt (see START_PROMPT_PHRASES) — the exact opener
advertised behind your "Message us" link/button. Anything else from a
brand-new contact is queued for your personal reply instead. Once someone's
in, they go through one fixed sequence:
  1. WELCOME     -> bot sends the Vireon Africa intro
  2. OPPORTUNITIES -> bot sends the about image with the earning-opportunities
                    list as its caption
  3. SIGNUP      -> once they signal they're ready to join, bot sends the
                    signup/referral link and the registration fee
  4. HUMAN TAKEOVER -> anything that isn't a clean "next step" — someone
     who didn't use the start prompt, already joined, is hesitating, making
     small talk, or sending a flagged message — gets ZERO auto-reply. It's
     queued on the dashboard under "Needs Your Reply" (with a push
     notification) so you can jump in personally. The bot never improvises
     small talk.

State survives restarts: chat progress + the pending-reply queue are written
to STATE_FILE after every change, so a user who replies days later picks up
exactly where they left off.

Live dashboard at / — real-time logs, stats, a "Needs Your Reply" queue,
Web Push notifications, PWA-installable.
"""

import os

# ════════════════════════════════════════════════════════════════
# ✏️  PROMPTS CONFIG — Edit all bot reply texts here
#     Each list entry is a variation; the bot picks one randomly
#     so replies never feel copy-pasted.
# ════════════════════════════════════════════════════════════════

# Set the SIGNUP_URL env var to change the link everywhere it's quoted below
# without touching any code. This should be your real Vireon Africa signup
# or referral link.
SIGNUP_URL = os.environ.get("SIGNUP_URL", "https://vireonwebsite.com.ng/payments")

# One-time registration fee to unlock Vireon Premiere and the full set of
# earning features. Quoted wherever a reply mentions the cost of joining.
REGISTRATION_FEE = os.environ.get("REGISTRATION_FEE", "₦14,500")

# Image sent alongside step 2 (the earning-opportunities message).
ABOUT_IMAGE_URL = os.environ.get(
    "ABOUT_IMAGE_URL",
    "https://vireonwebsite.com.ng/assets/images/about.jpg",
)

# ── Step 1: first contact — a short Vireon Africa welcome, then ask their
#    name. Kept to 4 lines max so it reads well as a chat bubble.
WELCOME_REPLIES = [
    (
        "💙 Welcome to Vireon Africa 🌍\n\n"
        "You get to earn from surveys, remote tasks, reviews, and referrals, all from one "
        "place, wherever you are.\n\n"
        "Ready to get started? What's your name?"
    ),
]

# ── Step 2: earning opportunities — sent as an image (ABOUT_IMAGE_URL) with
#    this text as the caption. Each feature gets its own line with a blank
#    line between them so it's easy to scan on a phone. Everything is framed
#    in 2nd person ("you earn/pocket/withdraw/pay") rather than describing
#    the feature in the abstract. Each entry is a variation; the bot picks
#    one at random.
OPPORTUNITIES_BODIES = [
    (
        "💰 VIREON EARNING OPPORTUNITIES\n\n"
        "You get to earn through multiple features on one platform.\n\n"
        "📊 Surveys – You earn up to £5 per approved survey.\n\n"
        "💬 Vireon Converse – You get paid for remote chat, virtual assistance, research, and "
        "client support tasks.\n\n"
        "🧠 Vireon IQ – You pocket £5 for every approved movie trailer or content review.\n\n"
        "📞 CallCash – You earn up to ₦13,333 (£6.35) from qualifying international calls.\n\n"
        "🔍 Google Monetization – You collect up to £5 daily from simple Google-related "
        "activities.\n\n"
        "📌 Pin-to-Profit – You earn up to £3 through Pinterest activities.\n\n"
        "🔥 Daily Login Streak – You bank up to £30 (₦60,000) every 30-day streak.\n\n"
        "👻 Snap Pro – You earn £50 for approved Snapchat sounds, £5 per sound use, or up to "
        "£5 per approved post.\n\n"
        "✖️ X Revenue Program – You receive a £3 welcome reward plus ongoing campaign "
        "earnings.\n\n"
        "🤝 Referral Rewards – You earn onboarding bonuses, partner rewards, and indirect "
        "commissions.\n\n"
        "💳 QuickLoan & EasyOwn – You get access to collateral-free loans and can buy gadgets "
        "on installment using your Vireon earnings.\n\n"
        "💸 Withdrawal Options – You get to withdraw via Bank Transfer, Vireon Wallet/Credit, "
        "or VTU (Airtime & Data).\n\n"
        f"💳 Registration Fee – You pay a one-time {REGISTRATION_FEE} to unlock Vireon Premiere "
        "and every earning feature above.\n\n"
        "Are you ready to register? 🚀"
    ),
]

# ── Step 3: signup link (personalised opener is added in code) ────────────
SIGNUP_LINK_BODIES = [
    (
        "Here's how to get started. Tap the link below, create your Vireon Africa account, then "
        f"join Vireon Premiere ({REGISTRATION_FEE}) to unlock every earning feature above.\n\n"
        f"👇 {SIGNUP_URL}\n\n"
        "Quick and straightforward, let's get you earning 🔥"
    ),
    (
        "Joining only takes a couple of minutes. Click the link below, register your account, "
        f"then complete the {REGISTRATION_FEE} Vireon Premiere registration to start earning "
        "from surveys, referrals, and every other feature above.\n\n"
        f"👇 {SIGNUP_URL}\n\n"
        "Get in now and build your first stream of income 🔥"
    ),
    (
        "Here are the quick steps to get you in. Open the link below, complete your "
        f"registration, then join Vireon Premiere ({REGISTRATION_FEE}) to unlock the earning "
        "features and start cashing out.\n\n"
        f"👇 {SIGNUP_URL}\n\n"
        "Let's get you earning 🔥"
    ),
]

SIGNUP_LINK_REMINDER = (
    "Here's your signup link again.\n"
    f"👇 {SIGNUP_URL}\n\n"
    f"It's a one-time {REGISTRATION_FEE} to join Vireon Premiere, then you can start earning "
    "right away 🚀"
)

REFERRAL_INFO_REPLY = (
    "🤝 Referral Rewards\n\n"
    "You get paid for growing the platform, not just using it. You earn an onboarding bonus "
    "for every new member you bring in, ongoing partner rewards tied to your referrals' "
    "activity, and indirect commissions as your network keeps earning.\n\n"
    "You'll get your personal referral link right inside the app after you sign up.\n\n"
    f"👇 {SIGNUP_URL}\n\n"
    "Ready to grab your spot and start referring? 🚀"
)

# ════════════════════════════════════════════════════════════════
# END PROMPTS CONFIG
# ════════════════════════════════════════════════════════════════

import os
import re
import asyncio
import random
import logging
import json
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

from telethon import TelegramClient, events
from telethon.sessions import StringSession

from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, Response, StreamingResponse
import uvicorn

# ─── Config ──────────────────────────────────────────────────────────────────
API_ID            = int(os.environ["API_ID"])
API_HASH          = os.environ["API_HASH"]
SESSION_STR       = os.environ.get("SESSION_STRING", "").strip()
VAPID_PRIVATE_KEY = os.environ.get("VAPID_PRIVATE_KEY", "")
VAPID_PUBLIC_KEY  = os.environ.get("VAPID_PUBLIC_KEY", "")
PORT              = int(os.environ.get("PORT", 8080))
# Where chat progress + the pending-reply queue are persisted so a Railway
# restart/redeploy doesn't lose anyone's place in the flow. Point this at a
# mounted Railway Volume path for durability across redeploys.
STATE_FILE = os.environ.get("STATE_FILE", os.path.join(os.path.dirname(os.path.abspath(__file__)), "bot_state.json"))

# Comma-separated Telegram @usernames (with or without the @) that always get
# a live reply from the bot — bypasses the owner-silence / manual-takeover
# rules and the master pause switch, so you can test the funnel from a second
# account at any time. These accounts can also message "stats" to get a
# stats summary back instead of a funnel reply.
TEST_USERNAMES = {
    u.strip().lstrip("@").lower()
    for u in os.environ.get("TEST_USERNAMES", "").split(",")
    if u.strip()
}

# ─── Chat stages ───────────────────────────────────────────────────────────
STAGE_NEW      = "new"             # never messaged before
STAGE_WELCOMED = "welcomed"        # welcome message sent, opportunities not sent yet
STAGE_EXPLAINED = "explained"      # earning-opportunities message has been sent
STAGE_SIGNUP   = "signup_sent"     # signup/referral link has been sent
STAGE_OWNER    = "owner_handling"  # pre-existing contact, or you stepped in manually — bot is silent forever

# ─── Scam filter ─────────────────────────────────────────────────────────────
SCAM_KEYWORDS = [
    "scam", "fraud", "fake", "419", "ponzi", "pyramid", "legit?",
    "is this real", "is this legit", "you people are scammers",
    "this is a scam", "reported", "efcc", "police", "illegal",
    "money ritual", "cheat", "stealing", "don't trust", "wayo",
    "una be scam", "na scam", "yahoo yahoo",
]

# ─── Intent matchers ─────────────────────────────────────────────────────────

def is_scam_message(text: str) -> bool:
    t = text.lower()
    return any(kw in t for kw in SCAM_KEYWORDS)


# The exact opener advertised behind your "Message us" link/button, e.g.
# t.me/YourVendor?text=... New contacts are only auto-welcomed if their first
# message matches this — anything else from a brand-new contact is queued for
# your personal reply instead of triggering the scripted funnel.
START_PROMPT_PHRASES = [
    "vireon vendor",
    "ready to register",
]

def matches_start_prompt(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in START_PROMPT_PHRASES)


ALREADY_JOINED_PHRASES = [
    "i have registered", "i've registered", "ive registered",
    "i have signed up", "i've signed up", "ive signed up",
    "i already registered", "i already signed up", "already registered",
    "already signed up", "i'm already a member", "im already a member",
    "i am already registered", "i already joined", "i've joined", "ive joined",
    "i have joined", "just registered", "just signed up", "just joined",
    "i already have an account", "i already have a vireon account",
    # Pidgin / Nigerian shorthand
    "i don register", "i don sign up", "i don join", "i don do am already",
]

def matches_already_joined(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in ALREADY_JOINED_PHRASES)


HESITATION_PHRASES = [
    "not ready", "im not ready", "i'm not ready", "i am not ready",
    "not now", "not right now", "maybe later", "maybe some other time",
    "let me think", "i'll think about it", "ill think about it",
    "i need to think", "give me time", "give me some time",
    "not sure", "i'm not sure", "im not sure", "still deciding",
    "still thinking", "not today", "another time", "i'll get back to you",
    "ill get back to you", "later maybe", "let me get back to you",
    "i need more time", "not convinced", "still considering", "not interested",
    "no thanks", "not just yet",
]

def matches_hesitation(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in HESITATION_PHRASES)


CHITCHAT_PHRASES = [
    "thank you", "thanks", "thank u", "tanx", "thnx", "thx",
    "ok noted", "okay noted", "noted", "i see", "i understand",
    "understood", "alright", "cool", "nice", "lol", "haha", "lmao",
    "good", "nice one", "great", "awesome",
]

def matches_chitchat(text: str) -> bool:
    t = text.lower().strip().rstrip("!?.").strip()
    return t in CHITCHAT_PHRASES or any(
        t.startswith(p + " ") for p in CHITCHAT_PHRASES
    )


STANDALONE_YES = {
    "yes", "yes.", "yep", "yeah", "yh", "yess", "yesss", "yeahh",
    "sure", "ok", "okay", "okayyy", "oya", "oya now", "oya na",
    "ready", "am ready", "am redy", "am readdy", "am rdy",
    "im ready", "i'm ready", "i ready", "i dey ready", "i don ready",
    "am set", "am in", "am down", "am game",
    "start", "start now", "okay start", "okay start now", "ok start now",
    "ok start", "begin", "begin now", "okay begin", "ok begin",
    "continue", "proceed", "lets go", "let's go", "letsgo",
    "go ahead", "gogogo", "do it", "do it now",
}

JOIN_KEYWORDS = [
    # standard join phrases
    "i want to join", "want to join", "i wanna join", "wanna join",
    "i wan to join", "i wan join", "wan to join", "i want join",
    "i want to register", "want to register", "let me join", "let me register",
    # ready / set variants
    "i'm ready", "im ready", "i am ready", "am ready", "i ready",
    "ready to join", "ready to start", "ready to begin", "ready to register",
    "i'm ready to register", "im ready to register",
    "i dey ready", "i don ready", "i dey set", "am set to join",
    # in / counting in
    "i'm in", "im in", "i am in", "am in", "count me in",
    # sign up / enroll
    "sign me up", "register me", "get me started", "start me up",
    "i'll join", "ill join", "i will join", "i'd like to join", "id like to join",
    "i want in", "take me in", "add me", "enroll me", "i want to enroll",
    # start / begin variants
    "okay start", "ok start", "start now", "begin now", "okay begin",
    "let me start", "let me begin", "i want to start", "i wanna start",
    "i want to begin", "i'm starting", "im starting",
    # action / movement phrases
    "let's go", "lets go", "let's do this", "lets do this",
    "let's begin", "lets begin", "let's start", "lets start",
    "go ahead", "move forward",
    # affirmation variants
    "yes please", "yes i want", "i want to proceed", "i want to continue",
    "proceed", "continue",
    # how to join
    "how do i join", "how to join", "how can i join",
    "i want to be part", "i want to be a part",
    # Pidgin / Nigerian informal
    "abeg add me", "abeg register me", "add me now", "put me in",
    "i dey interested", "i am interested in joining",
    "e don do", "make we go", "make i join", "abeg make i join",
    "i wan register", "abeg register me now",
    # "what's next" family
    "how do we continue", "how do we proceed", "how do i continue",
    "how do i proceed", "what's next", "whats next", "what next",
    "what do i do next", "what's the next step", "whats the next step",
    "next step", "how do we start", "how do i get started", "how do i start",
    "i want to get started", "i wanna get started", "lets get started",
    "let's get started",
    # signup-forward phrasing
    "how do i register", "how do i sign up", "how to sign up", "how to register",
    "where do i sign up", "where do i register", "how do i get membership",
    "how to get membership", "how much is membership", "is it free to join",
    "send the link", "send me the link", "drop the link", "share the link",
    "link please", "signup link please", "send me the signup link",
    "send me the registration link", "registration link please",
]

# Words that negate readiness/action — short messages with these are NOT join intent
_NEGATION_WORDS = {"not", "no", "never", "don't", "dont", "can't", "cant", "won't", "wont"}
# Action words that signal readiness in a short message (≤5 words, no negation)
_ACTION_WORDS = {"ready", "start", "begin", "proceed", "continue", "join", "register"}

def matches_join_intent(text: str) -> bool:
    t = " ".join(text.lower().strip().split())
    t_bare = t.rstrip("!?. ").strip()
    # Exact short-phrase match
    if t in STANDALONE_YES or t_bare in STANDALONE_YES:
        return True
    # Substring match against keyword list
    if any(kw in t for kw in JOIN_KEYWORDS):
        return True
    # Catch short messages (≤5 words) containing an action word but no negation
    words = set(t_bare.split())
    if len(words) <= 5 and _ACTION_WORDS.intersection(words) and not _NEGATION_WORDS.intersection(words):
        return True
    return False


INFO_TRIGGERS = [
    "how vireon work", "vireon work how", "what is vireon", "tell me about vireon",
    "explain vireon", "how does it work", "tell me more", "more info", "more details",
    "how much can i earn", "how much do i earn", "how do i earn", "how to earn",
    "what do i do", "what will i be doing", "what are the tasks", "what features",
    "how do i withdraw", "how to withdraw", "withdrawal process", "withdrawal options",
    "how real is this", "tell me everything", "break it down", "explain everything",
    "is it free", "any fee", "any charges", "does it cost anything",
    "what is the fee", "how much is it", "how much to start", "what surveys",
    "what is callcash", "what is snap pro", "what is vireon iq", "what is vireon converse",
    "what is pin to profit", "what is quickloan", "what is easyown",
]

def matches_info_request(text: str) -> bool:
    t = text.lower()
    return any(trigger in t for trigger in INFO_TRIGGERS)


REFERRAL_TRIGGERS = [
    "referral", "referrals", "refer a friend", "refer friends",
    "how do referrals work", "referral bonus", "referral link",
    "referral program", "referral rewards", "who do i refer",
    "invite friends", "invite a friend", "onboarding bonus",
]

def matches_referral_inquiry(text: str) -> bool:
    t = text.lower()
    return any(p in t for p in REFERRAL_TRIGGERS)


_NAME_LEAD_PHRASES = ("my name is ", "i am ", "i'm ", "im ", "its ", "it's ", "name is ", "name:")

def extract_name(text: str, fallback: str = "") -> str:
    """Best-effort extraction of a name from a free-text reply."""
    t = (text or "").strip()
    if not t:
        return fallback
    low = t.lower()
    for lead in _NAME_LEAD_PHRASES:
        if low.startswith(lead):
            t = t[len(lead):].strip()
            break
    words = [w for w in t.split() if re.match(r"^[A-Za-z'\-]+$", w)]
    if not words:
        return fallback
    name = " ".join(words[:3])
    if len(name) > 40:
        return fallback
    return name.title()


# ─── Persisted state ───────────────────────────────────────────────────────
# chat_states[chat_id]    = {stage, name, display_name, username, first_seen,
#                             last_seen, last_bot_msg_id}
# pending_review[chat_id] = {name, username, reason, text, time}
chat_states: dict = {}
pending_review: dict = {}


def _now_iso() -> str:
    return datetime.now(timezone.utc).isoformat()


def load_state() -> bool:
    """Load persisted state. Returns True if a state file existed (bot restart),
    False if no file was found (first run or file was lost)."""
    global stats_date, daily_history
    if not os.path.exists(STATE_FILE):
        return False
    try:
        with open(STATE_FILE, "r") as f:
            data = json.load(f)
        chat_states.update({int(k): v for k, v in data.get("chat_states", {}).items()})
        pending_review.update({int(k): v for k, v in data.get("pending_review", {}).items()})
        if data.get("pipeline"):
            pipeline.update(data["pipeline"])
        if data.get("daily_history"):
            daily_history.extend(data["daily_history"])
        today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        saved_date = data.get("stats_date", today)
        if data.get("stats"):
            if saved_date == today:
                stats.update(data["stats"])
                stats_date = today
            else:
                # Day rolled over while bot was offline — archive yesterday's stats
                entry = {
                    "date": saved_date,
                    **{k: data["stats"].get(k, 0) for k in
                       ("messages_today", "new_chats_today", "replies_sent", "flags_total")},
                    "welcomed":     data.get("pipeline", {}).get("welcomed", 0),
                    "info_sent":    data.get("pipeline", {}).get("info_sent", 0),
                    "signup_sent": data.get("pipeline", {}).get("signup_sent", 0),
                }
                daily_history.append(entry)
                while len(daily_history) > 7:
                    daily_history.pop(0)
                pipeline.update({"welcomed": 0, "info_sent": 0, "signup_sent": 0})
                stats_date = today
                log.info(f"📅 Day rollover detected ({saved_date} → {today}) — stats reset")
        log.info(f"Loaded persisted state — {len(chat_states)} known chats, {len(pending_review)} pending review")
        return True
    except Exception as e:
        log.warning(f"Could not load persisted state: {e}")
        return False


def save_state():
    try:
        tmp = STATE_FILE + ".tmp"
        with open(tmp, "w") as f:
            json.dump({
                "chat_states": {str(k): v for k, v in chat_states.items()},
                "pending_review": {str(k): v for k, v in pending_review.items()},
                "stats": stats,
                "pipeline": pipeline,
                "stats_date": stats_date,
                "daily_history": daily_history[-7:],
            }, f)
        os.replace(tmp, STATE_FILE)
    except Exception as e:
        log.warning(f"Could not save state: {e}")


def _reset_daily_stats():
    global stats_date
    today = datetime.now(timezone.utc).strftime("%Y-%m-%d")
    daily_history.append({
        "date": stats_date,
        "messages_today":   stats["messages_today"],
        "new_chats_today":  stats["new_chats_today"],
        "replies_sent":     stats["replies_sent"],
        "flags_total":      stats["flags_total"],
        "welcomed":         pipeline["welcomed"],
        "info_sent":        pipeline["info_sent"],
        "signup_sent":     pipeline["signup_sent"],
    })
    while len(daily_history) > 7:
        daily_history.pop(0)
    stats["messages_today"]  = 0
    stats["new_chats_today"] = 0
    stats["replies_sent"]    = 0
    stats["referral_inquiries"] = 0
    stats["flags_total"]     = 0
    pipeline["welcomed"]     = 0
    pipeline["info_sent"]    = 0
    pipeline["signup_sent"] = 0
    for i in range(24):
        hourly_messages[i] = 0
    stats_date = today
    save_state()
    log.info(f"📅 Daily stats reset — starting fresh for {today}")


async def daily_reset_task():
    while True:
        now = datetime.now(timezone.utc)
        tomorrow = (now + timedelta(days=1)).replace(hour=0, minute=0, second=0, microsecond=0)
        await asyncio.sleep((tomorrow - now).total_seconds())
        _reset_daily_stats()


def get_stage(chat_id: int) -> str:
    return chat_states.get(chat_id, {}).get("stage", STAGE_NEW)


def get_name(chat_id: int) -> str:
    return chat_states.get(chat_id, {}).get("name") or ""


def set_stage(chat_id: int, stage: str, sender_name: str = None, username: str = None, name: str = None):
    cs = chat_states.setdefault(chat_id, {})
    cs["stage"] = stage
    if sender_name:
        cs["display_name"] = sender_name
    if username is not None:
        cs["username"] = username
    if name:
        cs["name"] = name
    cs["last_seen"] = _now_iso()
    cs.setdefault("first_seen", cs["last_seen"])
    save_state()


PENDING_REASON_META = {
    "off_script":       {"label": "Didn't use the start prompt", "icon": "ph-chat-circle-dots",  "cls": "rb-chat"},
    "already_joined":   {"label": "Already joined/registered", "icon": "ph-receipt",             "cls": "rb-pay"},
    "hesitant":         {"label": "Hesitant / not ready",       "icon": "ph-hourglass-medium",   "cls": "rb-hesit"},
    "chitchat":         {"label": "Just chatting",              "icon": "ph-chat-teardrop-text", "cls": "rb-chat"},
    "photo":            {"label": "Sent a photo / file",        "icon": "ph-image",              "cls": "rb-photo"},
    "flagged":          {"label": "Flagged message",            "icon": "ph-shield-warning",     "cls": "rb-flag"},
}


def add_pending(chat_id: int, sender_name: str, username: str, reason: str, text: str):
    pending_review[chat_id] = {
        "name": sender_name,
        "username": username,
        "reason": reason,
        "text": (text or "")[:200],
        "time": _now_iso(),
    }
    stats["flags_total"] = stats.get("flags_total", 0) + 1
    save_state()
    meta = PENDING_REASON_META.get(reason, {"label": reason})
    _record_action(sender_name, "flag")
    try:
        asyncio.create_task(send_push_notification(
            f"🔔 {sender_name} needs your reply",
            f"{meta['label']}: {(text or '[no text]')[:80]}",
        ))
    except RuntimeError:
        pass


def clear_pending(chat_id: int):
    if chat_id in pending_review:
        del pending_review[chat_id]
        save_state()


# ─── Dashboard state ──────────────────────────────────────────────────────────
log_history: deque = deque(maxlen=500)
sse_subscribers: list = []
push_subscriptions: list = []
bot_status: dict = {"online": False, "since": None}
bot_paused: bool = False  # master kill switch — pauses all auto-replies and catch-up
stats: dict = {
    "messages_today": 0,
    "new_chats_today": 0,
    "failed_sends": 0,
    "replies_sent": 0,
    "referral_inquiries": 0,
    "flags_total": 0,
}
_push_executor = ThreadPoolExecutor(max_workers=2)

# 24-slot hourly message counter
hourly_messages: list = [0] * 24
# Per-pipeline action counts
pipeline: dict = {"welcomed": 0, "info_sent": 0, "signup_sent": 0}
# Live action feed (last 20 actions)
recent_actions: deque = deque(maxlen=20)
# Daily tracking
stats_date: str = datetime.now(timezone.utc).strftime("%Y-%m-%d")
daily_history: list = []  # last 7 days [{date, messages, new_chats, replies, flags, welcomed, info_sent, signup_sent}]


def _record_action(name: str, action: str):
    recent_actions.appendleft({
        "t": datetime.now(timezone.utc).strftime("%H:%M"),
        "name": name,
        "action": action,
    })
    hourly_messages[datetime.now(timezone.utc).hour] += 1


# ─── Logging ─────────────────────────────────────────────────────────────────

class WebLogHandler(logging.Handler):
    def emit(self, record):
        entry = json.dumps({
            "t": datetime.now(timezone.utc).strftime("%H:%M:%S"),
            "lvl": record.levelname,
            "msg": record.getMessage(),
        })
        log_history.append(entry)
        for q in list(sse_subscribers):
            try:
                q.put_nowait(entry)
            except Exception:
                pass


logging.basicConfig(
    format="[%(asctime)s] %(levelname)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("vireon-bot")
logging.getLogger().addHandler(WebLogHandler())

# ─── Helpers ─────────────────────────────────────────────────────────────────

async def human_delay(event, client, min_sec: float = 4.0, max_sec: float = 9.0):
    """Wait a human-feeling amount of time, showing a real 'typing…' indicator
    in Telegram the whole time so replies never feel instant or bot-like."""
    delay = random.uniform(min_sec, max_sec)
    log.info(f"Typing for {delay:.1f}s before replying...")
    try:
        async with client.action(event.chat_id, "typing"):
            await asyncio.sleep(delay)
    except Exception:
        await asyncio.sleep(delay)


async def already_replied(client, chat_id: int) -> bool:
    """True if the most recent outgoing message in this chat was NOT sent by
    the bot — i.e. you've personally jumped into the conversation.

    Guards:
    - If bot has never replied here (last_bot_msg_id is None), return False so
      we don't mistake old personal message history for a manual takeover.
    - Scan newest-first and stop at the first outgoing message found. Only that
      message needs to match the bot's last sent ID — older outgoing messages
      (from before the bot was set up) are irrelevant.
    """
    last_bot_id = chat_states.get(chat_id, {}).get("last_bot_msg_id")
    if last_bot_id is None:
        return False  # bot hasn't spoken here yet — not a manual takeover
    try:
        messages = await client.get_messages(chat_id, limit=15)
        for msg in messages:  # newest first
            if msg.out:
                # First outgoing message: is it the one the bot sent?
                return msg.id != last_bot_id
    except Exception as e:
        log.warning(f"Could not check reply history: {e}")
    return False


async def send_reply(event, text: str, max_retries: int = 3) -> bool:
    chat_id = event.chat_id
    for attempt in range(max_retries + 1):
        try:
            msg = await event.reply(text)
            cs = chat_states.setdefault(chat_id, {"stage": STAGE_NEW})
            cs["last_bot_msg_id"] = msg.id
            cs["last_seen"] = _now_iso()
            save_state()
            stats["replies_sent"] += 1
            try:
                await event.client.send_read_acknowledge(chat_id)
            except Exception as e:
                log.warning(f"Mark-read failed: {e}")
            return True
        except Exception as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                log.warning(
                    f"[{chat_id}] Send attempt {attempt + 1}/{max_retries + 1} "
                    f"failed: {e} — retrying in {wait}s"
                )
                await asyncio.sleep(wait)
            else:
                stats["failed_sends"] += 1
                log.error(
                    f"[{chat_id}] SEND FAILED after {max_retries + 1} attempts: {e}"
                )
    return False


# Telegram truncates/rejects photo captions past this length.
TELEGRAM_CAPTION_LIMIT = 1024


async def send_reply_with_image(event, caption: str, image_url: str, followup: str = "", max_retries: int = 3) -> bool:
    """Sends image_url as a photo with caption, then — always, by design —
    sends followup as a separate text message right after (the "two bubble"
    how-it-works reply: image+intro, then plan details).

    Telegram also caps photo captions at TELEGRAM_CAPTION_LIMIT chars as a
    safety net: if caption alone is too long, it's trimmed at the nearest
    paragraph/word break and the overflow is prepended to followup so nothing
    is lost."""
    chat_id = event.chat_id
    if len(caption) > TELEGRAM_CAPTION_LIMIT:
        split_at = caption.rfind("\n\n", 0, TELEGRAM_CAPTION_LIMIT)
        if split_at == -1:
            split_at = caption.rfind(" ", 0, TELEGRAM_CAPTION_LIMIT)
        if split_at == -1:
            split_at = TELEGRAM_CAPTION_LIMIT
        overflow = caption[split_at:].lstrip()
        caption = caption[:split_at].rstrip()
        followup = f"{overflow}\n\n{followup}".strip() if followup else overflow

    for attempt in range(max_retries + 1):
        try:
            msg = await event.reply(caption, file=image_url)
            cs = chat_states.setdefault(chat_id, {"stage": STAGE_NEW})
            cs["last_bot_msg_id"] = msg.id
            cs["last_seen"] = _now_iso()
            save_state()
            stats["replies_sent"] += 1
            try:
                await event.client.send_read_acknowledge(chat_id)
            except Exception as e:
                log.warning(f"Mark-read failed: {e}")
            if followup:
                await send_reply(event, followup)
            return True
        except Exception as e:
            if attempt < max_retries:
                wait = 2 ** attempt
                log.warning(
                    f"[{chat_id}] Image send attempt {attempt + 1}/{max_retries + 1} "
                    f"failed: {e} — retrying in {wait}s"
                )
                await asyncio.sleep(wait)
            else:
                stats["failed_sends"] += 1
                log.error(
                    f"[{chat_id}] IMAGE SEND FAILED after {max_retries + 1} attempts: {e}"
                )
    return False


# ─── Push notifications ───────────────────────────────────────────────────────

def _push_sync(title: str, body: str):
    try:
        from pywebpush import webpush  # type: ignore
    except ImportError:
        log.warning("pywebpush not installed — push notifications disabled.")
        return
    payload = json.dumps({"title": title, "body": body})
    dead = []
    for sub in list(push_subscriptions):
        try:
            webpush(
                subscription_info=sub,
                data=payload,
                vapid_private_key=VAPID_PRIVATE_KEY,
                vapid_claims={"sub": "mailto:support@vireonwebsite.com.ng"},
            )
        except Exception as e:
            s = str(e)
            if "410" in s or "404" in s:
                dead.append(sub)
            else:
                log.warning(f"Push error: {e}")
    for d in dead:
        try:
            push_subscriptions.remove(d)
        except ValueError:
            pass


async def send_push_notification(title: str, body: str):
    if not VAPID_PRIVATE_KEY or not push_subscriptions:
        return
    loop = asyncio.get_event_loop()
    await loop.run_in_executor(_push_executor, _push_sync, title, body)


# ─── Preload existing chats ───────────────────────────────────────────────────

async def preload_existing_chats(client):
    """Mark pre-existing contacts as owner-handled so the bot stays silent for
    conversations you're already managing. Contacts whose last message is
    INCOMING and from TODAY are intentionally skipped — they're new leads who
    messaged while the bot was being set up and catch_up_unreplied() will
    welcome them."""
    log.info("Loading existing conversations...")
    today_start = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
    count = 0
    skipped_new = 0
    try:
        async for dialog in client.iter_dialogs():
            if not dialog.is_user or getattr(dialog.entity, "bot", False):
                continue
            cid = dialog.entity.id
            if cid in chat_states:
                continue
            last_msg = dialog.message
            if last_msg and not last_msg.out:
                msg_date = last_msg.date
                if msg_date.tzinfo is None:
                    msg_date = msg_date.replace(tzinfo=timezone.utc)
                if msg_date >= today_start:
                    # New lead who messaged today — leave as STAGE_NEW for catch_up
                    skipped_new += 1
                    continue
            chat_states[cid] = {
                "stage": STAGE_OWNER,
                "display_name": dialog.name or str(cid),
                "username": getattr(dialog.entity, "username", None),
                "name": None,
                "first_seen": _now_iso(),
                "last_seen": _now_iso(),
            }
            count += 1
    except Exception as e:
        log.warning(f"Could not fully load existing chats: {e}")
    save_state()
    log.info(f"Preload: {count} existing contact(s) silenced, {skipped_new} today's lead(s) left for catch-up.")


async def catch_up_unreplied(client):
    """On startup, welcome every contact who messaged today with no reply yet.

    Phase 1 — collect candidates from dialog list (no per-dialog API calls).
    Phase 2 — sort oldest-first (first come, first served).
    Phase 3 — fetch real Telegram history for every candidate; if ANY outgoing
               message exists you've talked to them before → skip.
               Only truly first-time contacts get the welcome.
               Sends with a minimal 0.5 s gap to stay under flood limits.
    """
    cutoff = datetime.now(timezone.utc) - timedelta(hours=12)

    # ── Phase 1: collect ──────────────────────────────────────────────────────
    candidates = []  # (msg_date, dialog, cs, stage)
    try:
        async for dialog in client.iter_dialogs():
            if not dialog.is_user or getattr(dialog.entity, "bot", False):
                continue
            cid = dialog.entity.id
            cs = chat_states.get(cid, {})
            stage = cs.get("stage", STAGE_NEW)
            if stage not in (STAGE_NEW, STAGE_OWNER):
                continue
            if stage == STAGE_OWNER and cs.get("last_bot_msg_id") is not None:
                continue
            last_msg = dialog.message
            if not last_msg or last_msg.out:
                continue
            msg_date = last_msg.date
            if msg_date.tzinfo is None:
                msg_date = msg_date.replace(tzinfo=timezone.utc)
            if msg_date < cutoff:
                continue
            candidates.append((msg_date, dialog, cs, stage))
    except Exception as e:
        log.warning(f"Catch-up scan error: {e}")

    if not candidates:
        log.info("📬 Catch-up check — no missed contacts found")
        return

    # ── Phase 2: oldest first (first come, first served) ─────────────────────
    candidates.sort(key=lambda x: x[0])
    log.info(f"📬 Catch-up: {len(candidates)} contact(s) to process, oldest first")

    # ── Phase 3: verify & send ────────────────────────────────────────────────
    welcomed = 0
    confirmed_owner = 0
    for _, dialog, cs, stage in candidates:
        cid = dialog.entity.id
        entity = dialog.entity
        sender_name = (
            f"@{entity.username}" if getattr(entity, "username", None)
            else (getattr(entity, "first_name", None) or str(cid))
        )
        username = getattr(entity, "username", None)

        # Always check real Telegram history before sending — if ANY outgoing
        # message exists (even from before the bot was set up), you've
        # talked to this person before and the bot must stay silent.
        try:
            recent = await client.get_messages(cid, limit=20)
            if any(m.out for m in recent):
                chat_states[cid] = {
                    "stage": STAGE_OWNER,
                    "display_name": sender_name,
                    "username": username,
                    "name": cs.get("name"),
                    "first_seen": cs.get("first_seen", _now_iso()),
                    "last_seen": _now_iso(),
                }
                confirmed_owner += 1
                log.info(f"[{sender_name}] Catch-up: has chat history — skipped")
                continue
        except Exception as e:
            log.warning(f"[{sender_name}] History check failed: {e}")
            continue

        # No outgoing messages at all — truly a new contact. Only auto-welcome
        # if their message used the start prompt; otherwise queue it for you.
        last_msg = dialog.message
        msg_text = getattr(last_msg, "raw_text", None) or "" if last_msg else ""
        if not matches_start_prompt(msg_text):
            add_pending(cid, sender_name, username, "off_script", msg_text or "[no text]")
            log.info(f"[{sender_name}] Catch-up: didn't use the start prompt — queued for reply")
            continue

        if bot_paused:
            log.info(f"[{sender_name}] Catch-up paused — stopping")
            break

        try:
            sent = await client.send_message(cid, random.choice(WELCOME_REPLIES))
            chat_states[cid] = {
                "stage": STAGE_WELCOMED,
                "display_name": sender_name,
                "username": username,
                "name": None,
                "last_bot_msg_id": sent.id,
                "first_seen": cs.get("first_seen", _now_iso()),
                "last_seen": _now_iso(),
            }
            stats["new_chats_today"] += 1
            pipeline["welcomed"] += 1
            _record_action(sender_name, "welcome")
            log.info(f"[{sender_name}] Catch-up: welcome sent ({welcomed + 1}/{len(candidates)})")
            welcomed += 1
            await asyncio.sleep(0.5)
        except Exception as e:
            log.warning(f"[{sender_name}] Catch-up welcome failed: {e}")

    if welcomed or confirmed_owner:
        save_state()
    log.info(f"📬 Catch-up done — {welcomed} welcomed, {confirmed_owner} already owner-handled")

# ─── FastAPI dashboard ────────────────────────────────────────────────────────

app = FastAPI(docs_url=None, redoc_url=None)

SERVICE_WORKER_JS = """\
const CACHE = 'vireon-v1';
const SHELL = ['/'];

self.addEventListener('install', e => {
  e.waitUntil(
    caches.open(CACHE).then(c => c.addAll(SHELL)).then(() => self.skipWaiting())
  );
});
self.addEventListener('activate', e => {
  e.waitUntil(
    caches.keys()
      .then(ks => Promise.all(ks.filter(k => k !== CACHE).map(k => caches.delete(k))))
      .then(() => self.clients.claim())
  );
});
self.addEventListener('fetch', e => {
  if (e.request.method !== 'GET' || e.request.url.includes('/api/')) return;
  e.respondWith(
    fetch(e.request)
      .then(r => { caches.open(CACHE).then(c => c.put(e.request, r.clone())); return r; })
      .catch(() => caches.match(e.request))
  );
});
self.addEventListener('push', e => {
  const d = e.data ? e.data.json() : {title:'Vireon Africa Bot',body:'Alert'};
  e.waitUntil(self.registration.showNotification(d.title||'Vireon Africa Bot', {
    body:d.body||'', tag:'vireon-bot', requireInteraction:true, vibrate:[200,100,200]
  }));
});
self.addEventListener('notificationclick', e => {
  e.notification.close();
  e.waitUntil(clients.openWindow('/'));
});
"""

MANIFEST_JSON = json.dumps({
    "name": "Vireon Africa Bot",
    "short_name": "Vireon",
    "description": "Vireon Africa Telegram Bot — Live Console",
    "start_url": "/",
    "display": "standalone",
    "background_color": "#07070e",
    "theme_color": "#2f6fed",
    "orientation": "portrait-primary",
    "icons": [
        {"src": "/icon.svg", "sizes": "any", "type": "image/svg+xml", "purpose": "any maskable"}
    ]
})

ICON_SVG = """\
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 512 512">
  <defs>
    <linearGradient id="g" x1="0" y1="0" x2="1" y2="1">
      <stop offset="0" stop-color="#2f6fed"/>
      <stop offset="1" stop-color="#7fb3ff"/>
    </linearGradient>
  </defs>
  <rect width="512" height="512" rx="108" fill="#07070e"/>
  <circle cx="256" cy="256" r="152" fill="none" stroke="url(#g)" stroke-width="20"/>
  <text x="256" y="304" font-family="Georgia, 'Times New Roman', serif" font-size="204" font-weight="700"
        fill="url(#g)" text-anchor="middle">V</text>
</svg>"""

DASHBOARD_HTML = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <meta name="theme-color" content="#2f6fed">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Vireon">
  <title>Vireon Africa · Bot Console</title>
  <link rel="manifest" href="/manifest.json">
  <link rel="apple-touch-icon" href="/icon.svg">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/fill/style.css">
  <link rel="stylesheet" href="https://unpkg.com/@phosphor-icons/web@2.0.3/src/duotone/style.css">
  <style>
    *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }
    :root {
      --bg:    #07070e;
      --s1:    #0c0c16;
      --s2:    #11111e;
      --b1:    #1c1c2e;
      --b2:    #252538;
      --b3:    #2e2e45;
      --gold:  #f5a623;
      --gd:    rgba(245,166,35,.14);
      --green: #22d3a0;
      --gnd:   rgba(34,211,160,.14);
      --red:   #f43f5e;
      --rdd:   rgba(244,63,94,.12);
      --blue:  #60a5fa;
      --bld:   rgba(96,165,250,.14);
      --prp:   #a78bfa;
      --prd:   rgba(167,139,250,.14);
      --teal:  #2dd4bf;
      --tld:   rgba(45,212,191,.14);
      --pink:  #f472b6;
      --pkd:   rgba(244,114,182,.14);
      --ylw:   #fbbf24;
      --text:  #e2e8f0;
      --t2:    #94a3b8;
      --t3:    #4b5675;
    }
    html, body { height: 100%; }
    body {
      background: var(--bg);
      color: var(--text);
      font-family: 'Inter', sans-serif;
      height: 100dvh;
      display: flex;
      flex-direction: column;
      overflow: hidden;
    }
    body::before {
      content:''; position:fixed; top:0; left:0; right:0; height:2px; z-index:10000;
      background: linear-gradient(90deg, var(--gold), var(--prp), var(--teal), var(--gold));
      background-size: 200% 100%; animation: gradientMove 7s linear infinite;
    }
    @keyframes gradientMove { 0%{background-position:0% 0} 100%{background-position:200% 0} }

    /* ── Topbar ── */
    .topbar {
      background: var(--s1);
      border-bottom: 1px solid var(--b1);
      padding: 9px 16px 8px;
      display: flex; align-items: center; gap: 10px;
      flex-shrink: 0;
    }
    .brand { display: flex; align-items: center; gap: 9px; }
    .brand-ico {
      width: 32px; height: 32px; border-radius: 9px;
      background: linear-gradient(135deg, var(--gd), rgba(245,166,35,.04));
      border: 1px solid rgba(245,166,35,.35);
      display: flex; align-items: center; justify-content: center;
      color: var(--gold); font-size: 16px; flex-shrink: 0;
      box-shadow: 0 0 14px rgba(245,166,35,.18);
    }
    .brand-name {
      font-size: 14.5px; font-weight: 800; letter-spacing: -.2px;
      background: linear-gradient(135deg, #f5a623, #e8d48b);
      -webkit-background-clip: text; -webkit-text-fill-color: transparent;
      background-clip: text;
    }
    .brand-sub { font-size: 9px; color: var(--t3); letter-spacing: .6px; text-transform: uppercase; margin-top: 1px; }
    .vd { width: 1px; height: 20px; background: var(--b2); flex-shrink: 0; }
    .chip {
      display: flex; align-items: center; gap: 6px;
      background: var(--s2); border: 1px solid var(--b2);
      border-radius: 100px; padding: 3px 11px;
      font-size: 11px; font-weight: 500; white-space: nowrap;
    }
    .dot { width: 6px; height: 6px; border-radius: 50%; background: var(--t3); flex-shrink: 0; }
    .dot.on { background: var(--green); animation: pulse-ring 2s ease-out infinite; }
    .dot.off { background: var(--red); animation: blink 1.4s infinite; }
    @keyframes pulse-ring {
      0%  { box-shadow: 0 0 0 0 rgba(34,211,160,.7); }
      70% { box-shadow: 0 0 0 7px rgba(34,211,160,0); }
      100%{ box-shadow: 0 0 0 0 rgba(34,211,160,0); }
    }
    @keyframes blink { 0%,100%{opacity:1}50%{opacity:.2} }
    #uptime { font-size: 10px; color: var(--t3); white-space: nowrap; }
    #sparkline { display: flex; align-items: flex-end; gap: 1px; height: 18px; }
    #sparkline svg { display: block; }
    .sp { flex: 1; }
    .tbns { display: flex; gap: 6px; }
    .tbtn {
      background: var(--s2); border: 1px solid var(--b2); border-radius: 7px;
      padding: 5px 11px; font-family: 'Inter', sans-serif;
      font-size: 11px; font-weight: 500; cursor: pointer; color: var(--t2);
      display: flex; align-items: center; gap: 4px;
      transition: border-color .2s, color .2s, background .15s; white-space: nowrap;
      text-decoration: none;
    }
    .tbtn i { font-size: 13px; }
    .tbtn:hover { border-color: var(--gold); color: var(--gold); }
    .tbtn.active { color: var(--green); border-color: rgba(34,211,160,.4); background: rgba(34,211,160,.07); }
    .tbtn.denied { color: var(--t3); cursor: not-allowed; }
    .tbtn.inst { color: var(--prp); border-color: rgba(167,139,250,.35); }
    .tbtn.inst:hover { background: var(--prd); }
    .tbtn.copy { color: var(--teal); border-color: rgba(45,212,191,.35); }
    .tbtn.copy:hover { background: var(--tld); }
    .tbtn.copied { color: var(--green) !important; border-color: rgba(34,211,160,.4) !important; }

    /* ── Needs Your Reply ── */
    .nr-wrap {
      flex-shrink: 0; background: var(--s1); border-bottom: 1px solid var(--b1);
      padding: 10px 16px 11px; transition: box-shadow .3s;
    }
    .nr-wrap.has-items {
      background: linear-gradient(180deg, rgba(244,63,94,.06), rgba(12,12,22,1) 70%);
      box-shadow: inset 0 -1px 0 rgba(244,63,94,.15);
    }
    .nr-head { display:flex; align-items:baseline; justify-content:space-between; gap:8px; margin-bottom:8px; flex-wrap:wrap; }
    .nr-title { font-size: 12.5px; font-weight: 700; display:flex; align-items:center; gap:6px; color: var(--text); }
    .nr-title i { font-size: 15px; color: var(--red); }
    .nr-count {
      background: var(--rdd); color: var(--red); border: 1px solid rgba(244,63,94,.35);
      border-radius: 100px; font-size: 10.5px; font-weight: 700; padding: 1px 8px; min-width:18px; text-align:center;
    }
    .nr-wrap:not(.has-items) .nr-count { background: var(--gnd); color: var(--green); border-color: rgba(34,211,160,.35); }
    .nr-sub { font-size: 10px; color: var(--t3); }
    .nr-list {
      display: flex; gap: 8px; overflow-x: auto; padding-bottom: 2px;
      -webkit-overflow-scrolling: touch; scrollbar-width: thin;
    }
    .nr-list::-webkit-scrollbar { height: 4px; }
    .nr-list::-webkit-scrollbar-thumb { background: var(--b2); border-radius: 3px; }
    .nr-empty {
      font-size: 11.5px; color: var(--t3); display: flex; align-items: center; gap: 6px;
      padding: 8px 2px;
    }
    .nr-empty i { color: var(--green); font-size: 15px; }
    .nr-card {
      flex-shrink: 0; width: 226px; background: var(--s2); border: 1px solid var(--b2);
      border-left: 3px solid var(--t3); border-radius: 11px; padding: 10px 11px;
      display: flex; flex-direction: column; gap: 7px;
      box-shadow: 0 2px 10px rgba(0,0,0,.25);
    }
    .nr-card.rb-pay   { border-left-color: var(--gold); }
    .nr-card.rb-prev  { border-left-color: var(--blue); }
    .nr-card.rb-money { border-left-color: var(--teal); }
    .nr-card.rb-hesit { border-left-color: var(--prp); }
    .nr-card.rb-chat  { border-left-color: var(--t3); }
    .nr-card.rb-photo { border-left-color: var(--blue); }
    .nr-card.rb-flag  { border-left-color: var(--red); }
    .nr-row1 { display: flex; align-items: center; gap: 8px; }
    .nr-avatar {
      width: 30px; height: 30px; border-radius: 50%; flex-shrink: 0;
      background: linear-gradient(135deg, var(--gold), #e8d48b);
      display: flex; align-items: center; justify-content: center;
      font-weight: 800; font-size: 12px; color: #1a1206;
    }
    .nr-who { flex: 1; min-width: 0; }
    .nr-name { font-size: 12px; font-weight: 600; color: var(--text); overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .nr-time { font-size: 9.5px; color: var(--t3); font-family: 'JetBrains Mono', monospace; }
    .nr-badge {
      display: inline-flex; align-items: center; gap: 5px; align-self: flex-start;
      font-size: 10px; font-weight: 600; padding: 2px 8px; border-radius: 100px;
      background: var(--b1); color: var(--t2);
    }
    .nr-badge i { font-size: 12px; }
    .rb-pay .nr-badge   { background: var(--gd);  color: var(--gold); }
    .rb-prev .nr-badge  { background: var(--bld); color: var(--blue); }
    .rb-money .nr-badge { background: var(--tld); color: var(--teal); }
    .rb-hesit .nr-badge { background: var(--prd); color: var(--prp); }
    .rb-chat .nr-badge  { background: var(--b1);  color: var(--t2); }
    .rb-photo .nr-badge { background: var(--bld); color: var(--blue); }
    .rb-flag .nr-badge  { background: var(--rdd); color: var(--red); }
    .nr-snippet {
      font-size: 11px; color: var(--t2); line-height: 1.4; font-style: italic;
      overflow: hidden; display: -webkit-box; -webkit-line-clamp: 2; -webkit-box-orient: vertical;
      min-height: 15px;
    }
    .nr-actions { display: flex; gap: 6px; margin-top: 1px; }
    .nr-btn {
      flex: 1; display: flex; align-items: center; justify-content: center; gap: 4px;
      font-size: 10.5px; font-weight: 600; padding: 5px 6px; border-radius: 7px;
      border: 1px solid var(--b2); background: var(--s1); color: var(--t2); cursor: pointer;
      font-family: 'Inter', sans-serif; transition: all .15s;
    }
    .nr-btn i { font-size: 12px; }
    .nr-open:hover { border-color: var(--green); color: var(--green); }
    .nr-open.disabled { opacity: .45; cursor: default; }
    .nr-dismiss:hover { border-color: var(--red); color: var(--red); }

    /* ── Stats grid (8 cards) ── */
    .stats {
      display: grid; grid-template-columns: repeat(4,1fr); gap: 8px;
      padding: 10px 14px; border-bottom: 1px solid var(--b1); flex-shrink: 0;
    }
    .stat {
      background: linear-gradient(165deg, rgba(255,255,255,.025), rgba(255,255,255,0)), var(--s1);
      border: 1px solid var(--b1); border-radius: 11px; padding: 10px 12px;
      position: relative; overflow: hidden; cursor: default;
      transition: transform .15s, border-color .15s;
    }
    .stat:hover { transform: translateY(-1px); border-color: var(--b3); }
    .stat.urgent { border-color: rgba(244,63,94,.5); animation: urgentPulse 2s ease-in-out infinite; }
    @keyframes urgentPulse {
      0%,100% { box-shadow: 0 0 0 0 rgba(244,63,94,.25); }
      50%     { box-shadow: 0 0 0 5px rgba(244,63,94,0); }
    }
    .st { display:flex; align-items:flex-start; justify-content:space-between; margin-bottom:7px; }
    .sl { font-size:9px; font-weight:700; text-transform:uppercase; letter-spacing:.7px; color:var(--t3); }
    .si { font-size:16px; opacity:.7; }
    .sv { font-size:21px; font-weight:800; line-height:1; }
    .sn { font-size:9px; color:var(--t3); margin-top:3px; }
    .cg  .sv,.cg  .si { color:var(--gold);  } .cg  .si { background:var(--gd); }
    .cgn .sv,.cgn .si { color:var(--green); }
    .ct  .sv,.ct  .si { color:var(--teal);  }
    .cb  .sv,.cb  .si { color:var(--blue);  }
    .cp  .sv,.cp  .si { color:var(--prp);   }
    .cpk .sv,.cpk .si { color:var(--pink);  }
    .cr  .sv,.cr  .si { color:var(--red);   }

    /* ── Middle panel ── */
    .panel {
      display: grid; grid-template-columns: 1fr 1fr 1fr;
      border-bottom: 1px solid var(--b1); flex-shrink: 0;
      height: 172px;
    }
    .pcol {
      background: var(--s1); border-right: 1px solid var(--b1);
      padding: 11px 13px; overflow: hidden; display: flex; flex-direction: column;
    }
    .pcol:last-child { border-right: none; }
    .ph2 {
      font-size: 9px; font-weight: 700; text-transform: uppercase;
      letter-spacing: .8px; color: var(--t3); margin-bottom: 9px; flex-shrink: 0;
      display: flex; align-items: center; gap: 5px;
    }
    .ph2 i { font-size: 12px; color: var(--gold); }
    .chart { flex:1; display:flex; align-items:flex-end; gap:2px; padding-bottom:2px; overflow:hidden; }
    .bw { flex:1; display:flex; flex-direction:column; align-items:center; gap:2px; min-width:0; }
    .bar { width:100%; border-radius:2px 2px 0 0; background:linear-gradient(to top,var(--gold),rgba(245,166,35,.35)); min-height:2px; }
    .bh { font-size:7px; color:var(--t3); font-family:'JetBrains Mono',monospace; }
    .funnel { flex:1; display:flex; flex-direction:column; justify-content:space-between; }
    .frow { display:flex; align-items:center; gap:6px; }
    .fbadge { font-size:8px; font-weight:700; padding:1px 5px; border-radius:3px; flex-shrink:0; min-width:50px; text-align:center; }
    .fbar-wrap { flex:1; background:var(--b1); border-radius:3px; height:5px; overflow:hidden; }
    .fbar-fill { height:100%; border-radius:3px; transition:width .5s; }
    .fcount { font-size:10px; font-weight:600; flex-shrink:0; min-width:22px; text-align:right; }
    .fpct { font-size:9px; color:var(--t3); flex-shrink:0; min-width:28px; }
    .feed { flex:1; overflow-y:auto; display:flex; flex-direction:column; gap:4px; }
    .feed::-webkit-scrollbar { width:3px; }
    .feed::-webkit-scrollbar-thumb { background:var(--b2); border-radius:3px; }
    .feed-empty { font-size:10px; color:var(--t3); text-align:center; margin:auto; }
    .arow { display:flex; align-items:center; gap:6px; flex-shrink:0; }
    .at { font-family:'JetBrains Mono',monospace; font-size:9px; color:var(--t3); flex-shrink:0; }
    .aname { font-size:11px; color:var(--t2); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .abadge { font-size:8px; font-weight:700; padding:1px 5px; border-radius:3px; flex-shrink:0; }
    .ab-welcome  { background:var(--tld); color:var(--teal); }
    .ab-info     { background:var(--bld); color:var(--blue); }
    .ab-payment  { background:var(--gd);  color:var(--gold); }
    .ab-prime    { background:var(--pkd); color:var(--pink); }
    .ab-flag     { background:var(--rdd); color:var(--red); }
    .fb-new  { background:var(--gnd); color:var(--green); }
    .fb-wlc  { background:var(--tld); color:var(--teal); }
    .fb-info { background:var(--bld); color:var(--blue); }
    .fb-pay  { background:var(--gd);  color:var(--gold); }
    .ff-new  { background:var(--green); }
    .ff-wlc  { background:var(--teal); }
    .ff-info { background:var(--blue); }
    .ff-pay  { background:var(--gold); }

    /* ── Main content: log + sidebar ── */
    .main {
      flex: 1; display: flex; overflow: hidden;
    }
    .log-col {
      flex: 1; display: flex; flex-direction: column; overflow: hidden;
      border-right: 1px solid var(--b1);
    }

    /* ── Filter bar ── */
    .fbar {
      background: var(--s1); border-bottom: 1px solid var(--b1);
      padding: 6px 12px; display: flex; align-items: center; gap: 4px;
      flex-shrink: 0; flex-wrap: wrap; gap: 4px;
    }
    .fb-btn {
      background:transparent; border:1px solid transparent; border-radius:5px;
      padding:3px 9px; font-family:'Inter',sans-serif; font-size:11px;
      font-weight:500; cursor:pointer; color:var(--t3); transition:all .15s;
    }
    .fb-btn:hover { color:var(--t2); border-color:var(--b2); }
    .fb-btn.act     { background:var(--s2); color:var(--text);   border-color:var(--b2); }
    .fb-btn.fi.act  { color:var(--blue);   border-color:rgba(96,165,250,.35); }
    .fb-btn.fw.act  { color:var(--ylw);    border-color:rgba(251,191,36,.35); }
    .fb-btn.fe.act  { color:var(--red);    border-color:rgba(244,63,94,.35); }
    #searchWrap {
      flex: 1; min-width: 100px; position: relative;
    }
    #searchInput {
      width: 100%; background: var(--s2); border: 1px solid var(--b2);
      border-radius: 5px; padding: 3px 9px 3px 26px;
      font-family: 'Inter', sans-serif; font-size: 11px; color: var(--text);
      outline: none; transition: border-color .2s;
    }
    #searchInput::placeholder { color: var(--t3); }
    #searchInput:focus { border-color: var(--b3); }
    #searchWrap i {
      position: absolute; left: 7px; top: 50%; transform: translateY(-50%);
      font-size: 12px; color: var(--t3); pointer-events: none;
    }
    .ml { margin-left: auto; }
    .clr {
      background:transparent; border:none; color:var(--t3);
      font-family:'Inter',sans-serif; font-size:11px;
      cursor:pointer; padding:3px 8px; border-radius:5px;
      display:flex; align-items:center; gap:3px; transition:color .15s;
    }
    .clr:hover { color:var(--red); }
    .export-btn {
      background:transparent; border:1px solid var(--b2); color:var(--t3);
      font-family:'Inter',sans-serif; font-size:11px;
      cursor:pointer; padding:3px 8px; border-radius:5px;
      display:flex; align-items:center; gap:3px; transition:all .15s;
    }
    .export-btn:hover { color:var(--blue); border-color:rgba(96,165,250,.35); }

    /* ── Banner ── */
    #banner {
      display:none; background:rgba(244,63,94,.07);
      border-bottom:1px solid rgba(244,63,94,.2);
      color:var(--red); padding:5px 12px; font-size:11px;
      font-weight:500; flex-shrink:0;
      align-items:center; justify-content:center; gap:6px;
    }

    /* ── Log pane ── */
    #pane {
      flex:1; overflow-y:auto;
      background-image: radial-gradient(circle, rgba(255,255,255,.025) 1px, transparent 1px);
      background-size: 24px 24px;
    }
    #pane::-webkit-scrollbar { width:3px; }
    #pane::-webkit-scrollbar-thumb { background:var(--b2); border-radius:3px; }
    .row {
      display:flex; align-items:center; gap:8px;
      padding:4px 14px; border-left:2px solid transparent; transition:background .1s;
    }
    .row:hover { background:rgba(255,255,255,.02); }
    .row.lw { border-left-color:var(--ylw); }
    .row.le { border-left-color:var(--red); background:rgba(244,63,94,.04); }
    .row.le:hover { background:rgba(244,63,94,.08); }
    .rt { font-family:'JetBrains Mono',monospace; font-size:10px; color:var(--t3); flex-shrink:0; }
    .rl { font-size:9px; font-weight:700; letter-spacing:.5px; flex-shrink:0; min-width:48px; }
    .rl.INFO { color:var(--blue); } .rl.WARNING { color:var(--ylw); }
    .rl.ERROR { color:var(--red); } .rl.DEBUG { color:var(--t3); }
    .msg-tag {
      font-size:8px; font-weight:700; padding:1px 5px; border-radius:3px;
      letter-spacing:.3px; flex-shrink:0; align-self:center;
    }
    .tag-SIGNUP  { background:var(--gd);  color:var(--gold); }
    .tag-REFERRAL { background:var(--pkd); color:var(--pink); }
    .tag-INFO    { background:var(--bld); color:var(--blue); }
    .tag-WELCOME { background:var(--tld); color:var(--teal); }
    .tag-FLAG    { background:var(--rdd); color:var(--red); }
    .tag-SILENT  { background:var(--b2);  color:var(--t3); }
    .tag-SCAM    { background:var(--rdd); color:var(--red); }
    .rm { font-size:12px; color:var(--t2); line-height:1.5; word-break:break-word; flex:1; }
    .rm .u { color:var(--gold); font-weight:600; }
    #empty {
      display:flex; flex-direction:column; align-items:center;
      justify-content:center; height:100%; gap:8px; color:var(--t3);
    }
    #empty i { font-size:42px; opacity:.12; }
    #empty p { font-size:12px; font-weight:500; }

    /* ── Sidebar ── */
    .sidebar {
      width: 230px; background: var(--s1);
      display: flex; flex-direction: column;
      overflow-y: auto; flex-shrink: 0;
    }
    .sidebar::-webkit-scrollbar { width: 3px; }
    .sidebar::-webkit-scrollbar-thumb { background: var(--b2); border-radius: 3px; }
    .sidebar-sec {
      border-bottom: 1px solid var(--b1);
      padding: 12px 12px;
    }
    .sidebar-sec:last-child { border-bottom: none; }
    .sh2 {
      font-size: 9px; font-weight: 700; text-transform: uppercase;
      letter-spacing: .8px; color: var(--t3); margin-bottom: 10px;
      display: flex; align-items: center; gap: 5px;
    }
    .sh2 i { font-size: 12px; color: var(--gold); }
    .side-action {
      display: flex; align-items: center; gap: 6px;
      padding: 4px 0; border-bottom: 1px solid var(--b1);
    }
    .side-action:last-child { border-bottom: none; }
    .side-name { font-size: 11px; color: var(--t2); flex:1; overflow:hidden; text-overflow:ellipsis; white-space:nowrap; }
    .side-time { font-size: 9px; color: var(--t3); font-family: 'JetBrains Mono', monospace; flex-shrink:0; }
    .side-empty { font-size: 11px; color: var(--t3); text-align: center; padding: 8px 0; }
    .health-row {
      display: flex; align-items: center; justify-content: space-between;
      padding: 4px 0; border-bottom: 1px solid var(--b1);
    }
    .health-row:last-child { border-bottom: none; }
    .hl { font-size: 11px; color: var(--t3); }
    .hv { font-size: 11px; font-weight: 600; color: var(--text); }

    /* ── Footer ── */
    footer {
      background: var(--s1); border-top: 1px solid var(--b1);
      padding: 6px 14px; display: flex; align-items: center; gap: 14px;
      flex-shrink: 0; font-size: 11px; color: var(--t3);
    }
    footer label { display: flex; align-items: center; gap: 5px; cursor: pointer; }
    footer input[type=checkbox] { accent-color: var(--gold); cursor: pointer; }
    #known { margin-left: auto; }

    /* ── Toasts ── */
    #toastZone {
      position: fixed; top: 14px; right: 14px; z-index: 9999;
      display: flex; flex-direction: column; gap: 8px; pointer-events: none;
    }
    .toast {
      background: var(--s2); border: 1px solid var(--b2); border-radius: 9px;
      padding: 9px 14px; font-size: 12px; color: var(--text);
      max-width: 260px; pointer-events: all;
      opacity: 0; transform: translateX(16px);
      transition: opacity .25s, transform .25s;
      box-shadow: 0 6px 18px rgba(0,0,0,.35);
    }
    .toast.show { opacity: 1; transform: translateX(0); }
    .toast-SIGNUP   { border-color: rgba(244,63,94,.55); }
    .toast-REFERRAL { border-color: rgba(167,139,250,.55); }

    /* ── Mobile ── */
    @media (max-width: 900px) {
      .sidebar { display: none; }
      .log-col { border-right: none; }
      .stats { grid-template-columns: repeat(2,1fr); }
    }
    @media (max-width: 620px) {
      .panel { grid-template-columns: 1fr; height: auto; }
      .pcol { height: 150px; border-right: none; border-bottom: 1px solid var(--b1); }
      .pcol:last-child { border-bottom: none; }
      .brand-sub, #uptime, #sparkline { display: none; }
      .tbtn span { display: none; }
    }
  </style>
</head>
<body>

<div id="toastZone"></div>

<!-- ── Topbar ── -->
<div class="topbar">
  <div class="brand">
    <div class="brand-ico"><i class="ph-duotone ph-crown"></i></div>
    <div>
      <div class="brand-name">Vireon Africa</div>
      <div class="brand-sub">Vendor Console</div>
    </div>
  </div>
  <div class="vd"></div>
  <div class="chip">
    <div class="dot" id="sdot"></div>
    <span id="stxt">Connecting…</span>
  </div>
  <span id="uptime"></span>
  <div id="sparkline" title="Messages per minute (last 20 min)"></div>
  <div class="sp"></div>
  <div class="tbns">
    <button class="tbtn inst" id="installBtn" onclick="installApp()" style="display:none">
      <i class="ph-fill ph-download-simple"></i><span>Install</span>
    </button>
    <button class="tbtn copy" id="copyBtn" onclick="copyLink()">
      <i class="ph-fill ph-link" id="copyIco"></i><span id="copyTxt">Copy Link</span>
    </button>
    <button class="tbtn" id="notifyBtn" onclick="setupPush()">
      <i class="ph-fill ph-bell" id="nIco"></i><span id="nTxt">Alerts</span>
    </button>
    <button class="tbtn" id="pauseBtn" onclick="togglePause()" style="background:var(--acc);color:#fff">
      <i class="ph-fill ph-pause-circle" id="pauseIco"></i><span id="pauseTxt">Pause Bot</span>
    </button>
  </div>
</div>

<!-- ── Needs Your Reply ── -->
<div class="nr-wrap" id="needsReplyWrap">
  <div class="nr-head">
    <div class="nr-title"><i class="ph-fill ph-bell-ringing"></i>Needs Your Reply<span class="nr-count" id="nrCount">0</span></div>
    <div class="nr-sub">Paused on purpose — these need your personal touch</div>
  </div>
  <div class="nr-list" id="nrList">
    <div class="nr-empty"><i class="ph-fill ph-check-circle"></i>All caught up — nothing waiting on you</div>
  </div>
</div>

<!-- ── Stats (8 cards) ── -->
<div class="stats">
  <div class="stat cg">
    <div class="st"><div class="sl">Messages</div><i class="ph-fill ph-chat-circle-dots si"></i></div>
    <div class="sv" id="sMsgs">—</div><div class="sn">Today</div>
  </div>
  <div class="stat cgn">
    <div class="st"><div class="sl">New Contacts</div><i class="ph-fill ph-user-plus si"></i></div>
    <div class="sv" id="sNew">—</div><div class="sn">Today</div>
  </div>
  <div class="stat ct">
    <div class="st"><div class="sl">Welcomed</div><i class="ph-fill ph-hand-waving si"></i></div>
    <div class="sv" id="sWlc">—</div><div class="sn">Step 1 done</div>
  </div>
  <div class="stat cb">
    <div class="st"><div class="sl">Explained</div><i class="ph-fill ph-info si"></i></div>
    <div class="sv" id="sInfo">—</div><div class="sn">Step 2 done</div>
  </div>
  <div class="stat cp">
    <div class="st"><div class="sl">Signup Links</div><i class="ph-fill ph-currency-circle-dollar si"></i></div>
    <div class="sv" id="sPay">—</div><div class="sn">Step 3 done</div>
  </div>
  <div class="stat cpk">
    <div class="st"><div class="sl">Referral Inquiries</div><i class="ph-fill ph-crown si"></i></div>
    <div class="sv" id="sPrime">—</div><div class="sn">Asked about referrals</div>
  </div>
  <div class="stat cr" id="stPending">
    <div class="st"><div class="sl">Needs Reply</div><i class="ph-fill ph-bell-ringing si"></i></div>
    <div class="sv" id="sPending">—</div><div class="sn">Waiting on you</div>
  </div>
  <div class="stat cr">
    <div class="st"><div class="sl">Failed</div><i class="ph-fill ph-warning-circle si"></i></div>
    <div class="sv" id="sFail">—</div><div class="sn">After retries</div>
  </div>
</div>

<!-- ── Panel: Chart | Funnel | Feed ── -->
<div class="panel">
  <div class="pcol">
    <div class="ph2"><i class="ph-fill ph-chart-bar"></i>12-Hour Activity</div>
    <div class="chart" id="chart"><div class="feed-empty">No data yet</div></div>
  </div>
  <div class="pcol">
    <div class="ph2"><i class="ph-fill ph-funnel"></i>Contact Funnel</div>
    <div class="funnel" id="funnel"><div class="feed-empty">No contacts yet</div></div>
  </div>
  <div class="pcol">
    <div class="ph2"><i class="ph-fill ph-activity"></i>Live Actions</div>
    <div class="feed" id="feed"><div class="feed-empty">No actions yet</div></div>
  </div>
</div>

<!-- ── 7-day history ── -->
<div class="panel" id="historyPanel" style="display:none">
  <div class="pcol" style="flex:1">
    <div class="ph2"><i class="ph-fill ph-calendar-dots"></i>7-Day History</div>
    <div id="historyBars" style="display:flex;gap:8px;align-items:flex-end;height:80px;padding:8px 0"></div>
  </div>
</div>

<!-- ── Main: log + sidebar ── -->
<div class="main">
  <div class="log-col">
    <!-- Filter bar -->
    <div class="fbar">
      <button class="fb-btn act" data-f="ALL"     onclick="setFilter('ALL')">All</button>
      <button class="fb-btn fi"  data-f="INFO"    onclick="setFilter('INFO')">Info</button>
      <button class="fb-btn fw"  data-f="WARNING" onclick="setFilter('WARNING')">Warn</button>
      <button class="fb-btn fe"  data-f="ERROR"   onclick="setFilter('ERROR')">Errors</button>
      <div id="searchWrap">
        <i class="ph-fill ph-magnifying-glass"></i>
        <input type="text" id="searchInput" placeholder="Search logs…">
      </div>
      <button class="export-btn" onclick="exportLogs()">
        <i class="ph-fill ph-export"></i>Export
      </button>
      <button class="clr" onclick="clearLogs()"><i class="ph-fill ph-x-circle"></i>Clear</button>
    </div>

    <div id="banner"><i class="ph-fill ph-warning-circle"></i>Connection lost — reconnecting…</div>

    <div id="pane">
      <div id="empty"><i class="ph-duotone ph-tray"></i><p>Waiting for activity…</p></div>
    </div>
  </div>

  <!-- Sidebar -->
  <div class="sidebar">
    <div class="sidebar-sec">
      <div class="sh2"><i class="ph-fill ph-activity"></i>Recent Actions</div>
      <div id="sideActions"><div class="side-empty">No actions yet</div></div>
    </div>
    <div class="sidebar-sec">
      <div class="sh2"><i class="ph-fill ph-heartbeat"></i>Bot Health</div>
      <div id="sideHealth">
        <div class="health-row"><span class="hl">Uptime</span><span class="hv" id="hUptime">—</span></div>
        <div class="health-row"><span class="hl">Platform</span><span class="hv" style="color:var(--green)">Railway</span></div>
        <div class="health-row"><span class="hl">Auto-replies sent</span><span class="hv" id="hReplies">—</span></div>
        <div class="health-row"><span class="hl">Total flagged</span><span class="hv" id="hFlags">—</span></div>
        <div class="health-row"><span class="hl">SSE Reconnects</span><span class="hv" id="hReconn">0</span></div>
        <div class="health-row"><span class="hl">Known Chats</span><span class="hv" id="hKnown">—</span></div>
      </div>
    </div>
  </div>
</div>

<footer>
  <span id="cnt">0 entries</span>
  <label><input type="checkbox" id="aScroll" checked> Auto-scroll</label>
  <span id="reconnCnt" style="color:var(--t3)">SSE reconnects: 0</span>
  <span id="known" style="margin-left:auto"></span>
</footer>

<script>
(function () {
  'use strict';

  var sdot      = document.getElementById('sdot');
  var stxt      = document.getElementById('stxt');
  var uptime    = document.getElementById('uptime');
  var pane      = document.getElementById('pane');
  var empty     = document.getElementById('empty');
  var banner    = document.getElementById('banner');
  var cnt       = document.getElementById('cnt');
  var aScroll   = document.getElementById('aScroll');
  var notifyBtn = document.getElementById('notifyBtn');
  var installBtn= document.getElementById('installBtn');
  var known     = document.getElementById('known');
  var hKnown    = document.getElementById('hKnown');
  var hUptime   = document.getElementById('hUptime');
  var hReconn   = document.getElementById('hReconn');
  var hReplies  = document.getElementById('hReplies');
  var hFlags    = document.getElementById('hFlags');
  var reconnCnt = document.getElementById('reconnCnt');

  var total = 0, curFilter = 'ALL', searchQ = '';
  var uptimeSecs = 0, uptimeFetched = 0;
  var deferredPrompt = null;
  var SIGNUP_URL = '""" + SIGNUP_URL + """';
  var sseReconnects = 0;

  // ── Sparkline (client-side, 20 minutes) ────────────────────────────────────
  var sparkData = new Array(20).fill(0);
  var sparkMin  = -1;

  function bumpSparkline() {
    var now = new Date();
    var m = now.getHours() * 60 + now.getMinutes();
    if (sparkMin !== m) {
      if (sparkMin !== -1) { sparkData.push(0); sparkData.shift(); }
      sparkMin = m;
    }
    sparkData[sparkData.length - 1]++;
    drawSparkline();
  }
  function drawSparkline() {
    var max = Math.max.apply(null, sparkData) || 1;
    var W = 60, H = 18, n = sparkData.length;
    var bw = Math.max(1, Math.floor(W / n) - 1);
    var rects = sparkData.map(function(v, i) {
      var h = Math.max(Math.round((v / max) * H), v > 0 ? 2 : 1);
      var x = i * (bw + 1), y = H - h;
      var op = v > 0 ? 0.7 : 0.15;
      return '<rect x="'+x+'" y="'+y+'" width="'+bw+'" height="'+h+'" rx="1" fill="rgba(245,166,35,'+op+')"/>';
    }).join('');
    document.getElementById('sparkline').innerHTML =
      '<svg width="'+W+'" height="'+H+'" viewBox="0 0 '+W+' '+H+'">'+rects+'</svg>';
  }
  drawSparkline();

  // ── Stats cache (localStorage) ─────────────────────────────────────────────
  var SK = 'vireon_v1';
  function todayUTC() {
    var d = new Date();
    return d.getUTCFullYear()+'-'+String(d.getUTCMonth()+1).padStart(2,'0')+'-'+String(d.getUTCDate()).padStart(2,'0');
  }
  function restoreStats() {
    try {
      var c = JSON.parse(localStorage.getItem(SK) || 'null');
      if (!c) return;
      // Stale cache from a previous day — discard it so yesterday's numbers don't show as today's
      if (c.date && c.date !== todayUTC()) { localStorage.removeItem(SK); return; }
      if (c.msg    != null) document.getElementById('sMsgs').textContent    = c.msg;
      if (c.nw     != null) document.getElementById('sNew').textContent     = c.nw;
      if (c.wlc    != null) document.getElementById('sWlc').textContent     = c.wlc;
      if (c.inf    != null) document.getElementById('sInfo').textContent    = c.inf;
      if (c.pay    != null) document.getElementById('sPay').textContent     = c.pay;
      if (c.fail   != null) document.getElementById('sFail').textContent    = c.fail;
      if (c.prime  != null) document.getElementById('sPrime').textContent   = c.prime;
      if (c.rep    != null) hReplies.textContent = c.rep;
      if (c.flags  != null) hFlags.textContent = c.flags;
      if (c.pend   != null) document.getElementById('sPending').textContent = c.pend;
      if (c.kc     != null) { known.textContent = c.kc+' known'; hKnown.textContent = c.kc; }
    } catch(_) {}
  }
  function saveStats(d) {
    try {
      localStorage.setItem(SK, JSON.stringify({
        date:  d.stats_date || todayUTC(),
        msg:   d.stats   ? d.stats.messages_today   : 0,
        nw:    d.stats   ? d.stats.new_chats_today  : 0,
        wlc:   d.pipeline? d.pipeline.welcomed       : 0,
        inf:   d.pipeline? d.pipeline.info_sent      : 0,
        pay:   d.pipeline? d.pipeline.signup_sent   : 0,
        fail:  d.stats   ? d.stats.failed_sends      : 0,
        prime: d.stats   ? d.stats.referral_inquiries   : 0,
        rep:   d.stats   ? d.stats.replies_sent      : 0,
        flags: d.stats   ? d.stats.flags_total       : 0,
        pend:  d.pending_review ? d.pending_review.length : 0,
        kc:    d.known_chats || 0,
        at:    Date.now()
      }));
    } catch(_) {}
  }
  restoreStats();

  // ── Uptime counter ─────────────────────────────────────────────────────────
  function fmtUp(s) {
    var d=Math.floor(s/86400), h=Math.floor((s%86400)/3600);
    var m=Math.floor((s%3600)/60), sec=s%60;
    if(d>0) return d+'d '+h+'h';
    if(h>0) return h+'h '+m+'m';
    if(m>0) return m+'m '+sec+'s';
    return sec+'s';
  }
  setInterval(function(){
    if(uptimeSecs>0){
      var e=Math.floor((Date.now()-uptimeFetched)/1000);
      var s=fmtUp(uptimeSecs+e);
      uptime.textContent='Up '+s;
      hUptime.textContent=s;
    }
  }, 1000);

  // ── Action meta ────────────────────────────────────────────────────────────
  var ACTION_META = {
    welcome:  {lbl:'WELCOME',  cls:'ab-welcome'},
    info:     {lbl:'EXPLAIN',  cls:'ab-info'},
    signup:   {lbl:'SIGNUP',   cls:'ab-payment'},
    referral: {lbl:'REFERRAL', cls:'ab-prime'},
    flag:     {lbl:'FLAGGED',  cls:'ab-flag'},
  };

  // ── Chart ─────────────────────────────────────────────────────────────────
  function renderChart(hourly) {
    var el = document.getElementById('chart');
    if (!hourly || !hourly.length) return;
    var now = new Date().getUTCHours();
    var slots = [];
    for (var i = 11; i >= 0; i--) slots.push((now - i + 24) % 24);
    var data = slots.map(function(h){ return {h:('0'+h).slice(-2), c:hourly[h]||0}; });
    var max = Math.max.apply(null, data.map(function(d){return d.c;})) || 1;
    el.innerHTML = data.map(function(d){
      var pct = Math.max(Math.round((d.c/max)*100), d.c>0?4:2);
      return '<div class="bw"><div class="bar" style="height:'+pct+'%" title="'+d.c+' msgs"></div><div class="bh">'+d.h+'</div></div>';
    }).join('');
  }

  // ── Funnel ────────────────────────────────────────────────────────────────
  function renderFunnel(total, pipeline) {
    var el = document.getElementById('funnel');
    if (!total) { el.innerHTML = '<div class="feed-empty" style="font-size:10px">No contacts yet</div>'; return; }
    var p = pipeline || {};
    var rows = [
      {lbl:'New',     cls:'fb-new',  fill:'ff-new',  count:total,             pct:100},
      {lbl:'Welcome', cls:'fb-wlc',  fill:'ff-wlc',  count:p.welcomed||0,     pct:Math.round((p.welcomed||0)/total*100)},
      {lbl:'Explain', cls:'fb-info', fill:'ff-info', count:p.info_sent||0,    pct:Math.round((p.info_sent||0)/total*100)},
      {lbl:'Signup',  cls:'fb-pay',  fill:'ff-pay',  count:p.signup_sent||0, pct:Math.round((p.signup_sent||0)/total*100)},
    ];
    el.innerHTML = rows.map(function(r){
      return '<div class="frow">'
        +'<span class="fbadge '+r.cls+'">'+r.lbl+'</span>'
        +'<div class="fbar-wrap"><div class="fbar-fill '+r.fill+'" style="width:'+r.pct+'%"></div></div>'
        +'<span class="fcount">'+r.count+'</span>'
        +'<span class="fpct">'+r.pct+'%</span>'
        +'</div>';
    }).join('');
  }

  // ── 7-day history bars ────────────────────────────────────────────────────
  function renderDailyHistory(history) {
    var panel = document.getElementById('historyPanel');
    var wrap = document.getElementById('historyBars');
    if (!history || !history.length) { panel.style.display='none'; return; }
    panel.style.display='';
    var maxVal = Math.max.apply(null, history.map(function(d){ return d.messages_today||0; })) || 1;
    wrap.innerHTML = history.map(function(d){
      var pct = Math.round(((d.messages_today||0) / maxVal) * 100);
      var label = (d.date||'').slice(5); // MM-DD
      return '<div style="display:flex;flex-direction:column;align-items:center;flex:1;gap:3px">'
        +'<span style="font-size:9px;color:var(--fg2)">'+(d.messages_today||0)+'</span>'
        +'<div style="width:100%;background:var(--acc);border-radius:3px 3px 0 0;height:'+pct+'%;min-height:2px;opacity:0.8"></div>'
        +'<span style="font-size:9px;color:var(--fg2)">'+esc(label)+'</span>'
        +'</div>';
    }).join('');
  }

  // ── Action feed ───────────────────────────────────────────────────────────
  function renderFeed(actions) {
    var el = document.getElementById('feed');
    if (!actions || !actions.length) { el.innerHTML = '<div class="feed-empty">No actions yet</div>'; return; }
    el.innerHTML = actions.map(function(a){
      var m = ACTION_META[a.action] || {lbl:a.action.toUpperCase(), cls:'ab-flag'};
      return '<div class="arow">'
        +'<span class="at">'+esc(a.t)+'</span>'
        +'<span class="aname">'+esc(a.name)+'</span>'
        +'<span class="abadge '+m.cls+'">'+m.lbl+'</span>'
        +'</div>';
    }).join('');
  }

  // ── Sidebar actions ───────────────────────────────────────────────────────
  function renderSideActions(actions) {
    var el = document.getElementById('sideActions');
    if (!actions || !actions.length) { el.innerHTML = '<div class="side-empty">No actions yet</div>'; return; }
    el.innerHTML = actions.slice(0,7).map(function(a){
      var m = ACTION_META[a.action] || {lbl:a.action.toUpperCase(), cls:'ab-flag'};
      return '<div class="side-action">'
        +'<span class="abadge '+m.cls+'">'+m.lbl+'</span>'
        +'<span class="side-name">'+esc(a.name)+'</span>'
        +'<span class="side-time">'+esc(a.t)+'</span>'
        +'</div>';
    }).join('');
  }

  // ── Needs Your Reply ─────────────────────────────────────────────────────
  var REASON_META = {
    off_script:       {label:'Didn\'t use the start prompt', icon:'ph-chat-circle-dots', cls:'rb-chat'},
    already_joined:   {label:'Already joined/registered', icon:'ph-receipt',           cls:'rb-pay'},
    hesitant:         {label:'Hesitant / not ready',       icon:'ph-hourglass-medium',  cls:'rb-hesit'},
    chitchat:         {label:'Just chatting',              icon:'ph-chat-teardrop-text',cls:'rb-chat'},
    photo:            {label:'Sent a photo / file',        icon:'ph-image',             cls:'rb-photo'},
    flagged:          {label:'Flagged message',            icon:'ph-shield-warning',    cls:'rb-flag'}
  };
  var lastPendingIds = [];
  function timeAgo(iso) {
    var diff = (Date.now() - new Date(iso).getTime()) / 1000;
    if (diff < 5) return 'just now';
    if (diff < 60) return Math.round(diff)+'s ago';
    if (diff < 3600) return Math.round(diff/60)+'m ago';
    if (diff < 86400) return Math.round(diff/3600)+'h ago';
    return Math.round(diff/86400)+'d ago';
  }
  function renderNeedsReply(items) {
    items = items || [];
    var wrap = document.getElementById('needsReplyWrap');
    var list = document.getElementById('nrList');
    var count = document.getElementById('nrCount');
    var statCard = document.getElementById('stPending');
    count.textContent = items.length;
    wrap.classList.toggle('has-items', items.length > 0);
    statCard.classList.toggle('urgent', items.length > 0);
    if (!items.length) {
      list.innerHTML = '<div class="nr-empty"><i class="ph-fill ph-check-circle"></i>All caught up — nothing waiting on you</div>';
      lastPendingIds = [];
      return;
    }
    var newIds = items.map(function(i){ return i.chat_id; });
    var brandNew = newIds.filter(function(id){ return lastPendingIds.indexOf(id) === -1; });
    list.innerHTML = items.map(function(it){
      var m = REASON_META[it.reason] || {label: it.reason, icon:'ph-warning-circle', cls:'rb-flag'};
      var initials = (it.name || '?').replace('@','').trim().slice(0,2).toUpperCase();
      var openBtn = it.username
        ? '<a class="nr-btn nr-open" href="https://t.me/'+esc(it.username)+'" target="_blank" rel="noopener"><i class="ph-fill ph-paper-plane-tilt"></i>Open Chat</a>'
        : '<span class="nr-btn nr-open disabled"><i class="ph-fill ph-paper-plane-tilt"></i>No username</span>';
      return '<div class="nr-card '+m.cls+'">'
        + '<div class="nr-row1"><div class="nr-avatar">'+esc(initials)+'</div>'
        + '<div class="nr-who"><div class="nr-name">'+esc(it.name)+'</div><div class="nr-time">'+timeAgo(it.time)+'</div></div></div>'
        + '<div class="nr-badge"><i class="ph-fill '+m.icon+'"></i>'+esc(m.label)+'</div>'
        + '<div class="nr-snippet">'+esc(it.text || '—')+'</div>'
        + '<div class="nr-actions">'+openBtn+'<button class="nr-btn nr-dismiss" onclick="dismissPending('+it.chat_id+')"><i class="ph-fill ph-x-circle"></i>Dismiss</button></div>'
        + '</div>';
    }).join('');
    if (brandNew.length) {
      var first = items.filter(function(i){ return brandNew.indexOf(i.chat_id) > -1; })[0];
      if (first) {
        var m2 = REASON_META[first.reason] || {label: first.reason};
        showToast('🔔 '+esc(first.name)+' needs your reply — '+esc(m2.label), 'SIGNUP');
      }
    }
    lastPendingIds = newIds;
  }
  function dismissPending(chatId) {
    fetch('/api/dismiss/' + chatId, {method:'POST'}).then(pollStatus).catch(function(){});
  }
  window.dismissPending = dismissPending;

  // ── Pause / resume ────────────────────────────────────────────────────────
  var _paused = false;
  function togglePause() {
    var url = _paused ? '/api/resume' : '/api/pause';
    fetch(url, {method:'POST'}).then(function(r){return r.json();}).then(function(d){
      _paused = d.paused;
      updatePauseBtn();
      pollStatus();
    }).catch(function(){});
  }
  function updatePauseBtn() {
    var btn = document.getElementById('pauseBtn');
    var ico = document.getElementById('pauseIco');
    var txt = document.getElementById('pauseTxt');
    if (_paused) {
      btn.style.background='#e53935'; btn.style.color='#fff';
      ico.className='ph-fill ph-play-circle';
      txt.textContent='Resume Bot';
    } else {
      btn.style.background='var(--acc)'; btn.style.color='#fff';
      ico.className='ph-fill ph-pause-circle';
      txt.textContent='Pause Bot';
    }
  }
  window.togglePause = togglePause;

  // ── Poll status ───────────────────────────────────────────────────────────
  function pollStatus() {
    fetch('/api/status').then(function(r){return r.json();}).then(function(d){
      if(d.online){
        sdot.className='dot on'; stxt.textContent= d.paused ? 'Paused' : 'Online';
        uptimeSecs=d.uptime_seconds||0; uptimeFetched=Date.now();
      } else {
        sdot.className='dot off'; stxt.textContent='Offline';
        uptimeSecs=0; uptime.textContent='';
      }
      if(d.paused !== undefined && d.paused !== _paused){ _paused=d.paused; updatePauseBtn(); }
      if(d.stats){
        document.getElementById('sMsgs').textContent    = d.stats.messages_today;
        document.getElementById('sNew').textContent     = d.stats.new_chats_today;
        document.getElementById('sFail').textContent    = d.stats.failed_sends;
        document.getElementById('sPrime').textContent   = d.stats.referral_inquiries;
        hReplies.textContent = d.stats.replies_sent;
        hFlags.textContent   = d.stats.flags_total || 0;
      }
      if(d.pipeline){
        document.getElementById('sWlc').textContent  = d.pipeline.welcomed;
        document.getElementById('sInfo').textContent = d.pipeline.info_sent;
        document.getElementById('sPay').textContent  = d.pipeline.signup_sent;
      }
      document.getElementById('sPending').textContent = (d.pending_review||[]).length;
      if(d.known_chats!=null){
        known.textContent = d.known_chats+' known';
        hKnown.textContent = d.known_chats;
      }
      renderChart(d.hourly);
      renderFunnel(d.stats ? d.stats.new_chats_today : 0, d.pipeline);
      renderFeed(d.recent_actions);
      renderSideActions(d.recent_actions);
      renderNeedsReply(d.pending_review);
      renderDailyHistory(d.daily_history);
      drawSparkline();
      saveStats(d);
    }).catch(function(){
      sdot.className='dot off'; stxt.textContent='Unreachable';
    });
  }
  window.pollStatus = pollStatus;
  pollStatus();
  setInterval(pollStatus, 8000);

  // ── Utilities ─────────────────────────────────────────────────────────────
  function esc(s){ return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
  function fmtMsg(m){ return esc(m).replace(/\\[@([^\\]]+)\\]/g,'[@<span class="u">$1</span>]'); }

  function getMsgTag(msg) {
    var m = msg.toLowerCase();
    if (m.includes('signup link')) return 'SIGNUP';
    if (m.includes('referral program')) return 'REFERRAL';
    if (m.includes('earning opportunities')) return 'INFO';
    if (m.includes('welcome') || m.includes('first contact')) return 'WELCOME';
    if (m.includes('flagged') || m.includes('needs manual') || m.includes('needs a reply')) return 'FLAG';
    if (m.includes('silent') || m.includes('owner') || m.includes('skip')) return 'SILENT';
    if (m.includes('scam')) return 'SCAM';
    return null;
  }

  // ── Log filter ────────────────────────────────────────────────────────────
  function setFilter(f){
    curFilter=f;
    document.querySelectorAll('.fb-btn').forEach(function(b){ b.classList.toggle('act', b.dataset.f===f); });
    applyFilters();
  }
  window.setFilter=setFilter;

  function applyFilters(){
    document.querySelectorAll('.row').forEach(function(r){
      var lvlOk = curFilter==='ALL' || r.dataset.lvl===curFilter;
      var srchOk = !searchQ || (r.querySelector('.rm')?.textContent.toLowerCase().includes(searchQ));
      r.style.display = (lvlOk && srchOk) ? '' : 'none';
    });
  }

  document.getElementById('searchInput').addEventListener('input', function(){
    searchQ = this.value.toLowerCase();
    applyFilters();
  });

  // ── Add log row ───────────────────────────────────────────────────────────
  function addRow(data){
    if(data.type==='ping') return;
    // bump sparkline on incoming message events
    if(data.msg && data.msg.includes('[@')) bumpSparkline();
    if(empty.parentNode===pane) pane.removeChild(empty);
    var lvl=data.lvl||'INFO';
    var tag=getMsgTag(data.msg||'');
    var row=document.createElement('div');
    row.className='row'+(lvl==='WARNING'?' lw':'')+(lvl==='ERROR'?' le':'');
    row.dataset.lvl=lvl;
    var badgeHtml = tag ? '<span class="msg-tag tag-'+tag+'">'+tag+'</span>' : '';
    var lvlOk = curFilter==='ALL'||lvl===curFilter;
    var srchOk = !searchQ||(data.msg||'').toLowerCase().includes(searchQ);
    if(!lvlOk||!srchOk) row.style.display='none';
    row.innerHTML='<span class="rt">'+esc(data.t)+'</span>'
      +'<span class="rl '+esc(lvl)+'">'+esc(lvl)+'</span>'
      +badgeHtml
      +'<span class="rm">'+fmtMsg(data.msg||'')+'</span>';
    pane.appendChild(row);
    total++; cnt.textContent=total+' entries';
    if(aScroll.checked) pane.scrollTop=pane.scrollHeight;
    // toast for important actions
    if(tag==='SIGNUP')   showToast('💰 '+esc((data.msg||'').slice(0,55)),'SIGNUP');
    if(tag==='REFERRAL') showToast('⭐ '+esc((data.msg||'').slice(0,55)),'REFERRAL');
  }

  // ── Clear ─────────────────────────────────────────────────────────────────
  function clearLogs(){
    pane.innerHTML=''; pane.appendChild(empty);
    total=0; cnt.textContent='0 entries';
  }
  window.clearLogs=clearLogs;

  // ── Export logs ───────────────────────────────────────────────────────────
  function exportLogs(){
    var rows=document.querySelectorAll('#pane .row');
    var lines=Array.from(rows).map(function(r){
      var t=r.querySelector('.rt')?.textContent||'';
      var l=r.querySelector('.rl')?.textContent||'';
      var m=r.querySelector('.rm')?.textContent||'';
      return '['+t+'] '+l+' '+m;
    });
    var date=new Date().toISOString().slice(0,10);
    var blob=new Blob([lines.join('\\n')],{type:'text/plain'});
    var a=document.createElement('a');
    a.href=URL.createObjectURL(blob);
    a.download='vireon-logs-'+date+'.txt';
    a.click();
  }
  window.exportLogs=exportLogs;

  // ── Toast notifications ───────────────────────────────────────────────────
  function showToast(msg, type){
    var c=document.getElementById('toastZone');
    var t=document.createElement('div');
    t.className='toast toast-'+type;
    t.textContent=msg;
    c.appendChild(t);
    requestAnimationFrame(function(){ requestAnimationFrame(function(){ t.classList.add('show'); }); });
    setTimeout(function(){
      t.classList.remove('show');
      setTimeout(function(){ t.remove(); }, 300);
    }, 4500);
  }

  // ── SSE ───────────────────────────────────────────────────────────────────
  var es;
  function connectSSE(){
    if(es){ es.close(); sseReconnects++; reconnCnt.textContent='SSE reconnects: '+sseReconnects; hReconn.textContent=sseReconnects; }
    es=new EventSource('/api/logs');
    es.onmessage=function(e){try{addRow(JSON.parse(e.data));}catch(_){}};
    es.onopen=function(){ banner.style.display='none'; };
    es.onerror=function(){ banner.style.display='flex'; es.close(); setTimeout(connectSSE,5000); };
  }
  connectSSE();

  // ── Quick copy link ───────────────────────────────────────────────────────
  function copyLink(){
    navigator.clipboard.writeText(SIGNUP_URL).then(function(){
      var btn=document.getElementById('copyBtn');
      document.getElementById('copyIco').className='ph-fill ph-check-circle';
      document.getElementById('copyTxt').textContent='Copied!';
      btn.classList.add('copied');
      setTimeout(function(){
        btn.classList.remove('copied');
        document.getElementById('copyIco').className='ph-fill ph-link';
        document.getElementById('copyTxt').textContent='Copy Link';
      }, 2000);
    }).catch(function(){
      var ta=document.createElement('textarea');
      ta.value=SIGNUP_URL; document.body.appendChild(ta);
      ta.select(); document.execCommand('copy'); document.body.removeChild(ta);
    });
  }
  window.copyLink=copyLink;

  // ── PWA Install ───────────────────────────────────────────────────────────
  window.addEventListener('beforeinstallprompt',function(e){
    e.preventDefault(); deferredPrompt=e; installBtn.style.display='';
  });
  window.addEventListener('appinstalled',function(){
    installBtn.style.display='none'; deferredPrompt=null;
  });
  function installApp(){
    if(!deferredPrompt) return;
    deferredPrompt.prompt();
    deferredPrompt.userChoice.then(function(){ deferredPrompt=null; });
  }
  window.installApp=installApp;

  // ── Push notifications ────────────────────────────────────────────────────
  function setNotify(s){
    var ico=document.getElementById('nIco'), txt=document.getElementById('nTxt');
    if(s==='on'){ ico.className='ph-fill ph-bell-ringing'; txt.textContent='Alerts On'; notifyBtn.className='tbtn active'; }
    else if(s==='blocked'){ ico.className='ph-fill ph-bell-slash'; txt.textContent='Blocked'; notifyBtn.className='tbtn denied'; }
    else { ico.className='ph-fill ph-bell'; txt.textContent='Alerts'; notifyBtn.className='tbtn'; }
  }
  function b64(s){
    var pad='='.repeat((4-s.length%4)%4);
    var raw=window.atob((s+pad).replace(/-/g,'+').replace(/_/g,'/'));
    var arr=new Uint8Array(raw.length);
    for(var i=0;i<raw.length;i++) arr[i]=raw.charCodeAt(i);
    return arr;
  }
  async function setupPush(){
    if(!('serviceWorker' in navigator)||!('PushManager' in window)){
      alert('Push not supported. Use Chrome or Firefox on Android.'); return;
    }
    var p=await Notification.requestPermission();
    if(p!=='granted'){ setNotify('blocked'); return; }
    try{
      var kd=await (await fetch('/api/vapid-public-key')).json();
      var reg=await navigator.serviceWorker.ready;
      var opts={userVisibleOnly:true};
      if(kd.key) opts.applicationServerKey=b64(kd.key);
      var sub=await reg.pushManager.subscribe(opts);
      await fetch('/api/subscribe',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(sub.toJSON())});
      setNotify('on'); pollStatus();
    }catch(err){alert('Alert setup failed: '+err.message);}
  }
  window.setupPush=setupPush;

  if('serviceWorker' in navigator)
    navigator.serviceWorker.register('/sw.js').catch(function(e){console.warn('SW:',e);});
  if(typeof Notification!=='undefined'){
    if(Notification.permission==='granted') setNotify('on');
    else if(Notification.permission==='denied') setNotify('blocked');
  }
})();
</script>
</body>
</html>
"""


@app.get("/", response_class=HTMLResponse)
async def dashboard():
    return DASHBOARD_HTML


@app.get("/sw.js")
async def service_worker():
    return Response(content=SERVICE_WORKER_JS, media_type="application/javascript")


@app.get("/manifest.json")
async def manifest():
    return Response(content=MANIFEST_JSON, media_type="application/manifest+json")


@app.get("/icon.svg")
async def icon():
    return Response(content=ICON_SVG, media_type="image/svg+xml")


@app.get("/api/status")
async def api_status():
    uptime_secs = 0
    if bot_status.get("since"):
        start = datetime.fromisoformat(bot_status["since"])
        uptime_secs = int((datetime.now(timezone.utc) - start).total_seconds())
    pending_list = sorted(
        [{"chat_id": cid, **info} for cid, info in pending_review.items()],
        key=lambda x: x["time"],
        reverse=True,
    )
    return {
        **bot_status,
        "uptime_seconds": uptime_secs,
        "paused": bot_paused,
        "stats": stats,
        "pipeline": pipeline,
        "hourly": list(hourly_messages),
        "recent_actions": list(recent_actions),
        "pending_review": pending_list,
        "subscriptions": len(push_subscriptions),
        "known_chats": len(chat_states),
        "stats_date": stats_date,
        "daily_history": daily_history[-7:],
    }


@app.get("/api/vapid-public-key")
async def api_vapid_key():
    return {"key": VAPID_PUBLIC_KEY}


@app.post("/api/subscribe")
async def api_subscribe(request: Request):
    sub = await request.json()
    if sub not in push_subscriptions:
        push_subscriptions.append(sub)
        log.info(f"Push subscription added — total: {len(push_subscriptions)}")
    return {"ok": True}


@app.post("/api/dismiss/{chat_id}")
async def api_dismiss(chat_id: int):
    clear_pending(chat_id)
    log.info(f"Manually dismissed pending review for chat {chat_id}")
    return {"ok": True}


@app.post("/api/pause")
async def api_pause():
    global bot_paused
    bot_paused = True
    log.warning("⏸️ Bot PAUSED — all auto-replies suppressed")
    return {"paused": True}


@app.post("/api/resume")
async def api_resume():
    global bot_paused
    bot_paused = False
    log.info("▶️ Bot RESUMED — auto-replies active")
    return {"paused": False}


@app.get("/api/logs")
async def api_logs(request: Request):
    queue: asyncio.Queue = asyncio.Queue(maxsize=200)
    sse_subscribers.append(queue)

    async def generate():
        for entry in list(log_history):
            yield f"data: {entry}\n\n"
        try:
            while True:
                if await request.is_disconnected():
                    break
                try:
                    data = await asyncio.wait_for(queue.get(), timeout=25.0)
                    yield f"data: {data}\n\n"
                except asyncio.TimeoutError:
                    yield 'data: {"type":"ping"}\n\n'
        finally:
            try:
                sse_subscribers.remove(queue)
            except ValueError:
                pass

    return StreamingResponse(
        generate(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )

# ─── Main bot handler ─────────────────────────────────────────────────────────
#
# Order of checks matters — read top to bottom:
#   1. Pre-existing / owner-handling chat            -> permanent silence
#   2. You've personally replied in this chat        -> switch to silence
#   3. Scam-ish keywords                             -> flag, silence
#   4. Media message (photo/doc/etc.) once mid-flow  -> flag, silence
#   5. Already joined/registered                     -> flag, silence
#   6. Hesitation                                    -> flag, silence
#   7. Chit-chat with nothing actionable in it        -> flag (low priority), silence
#   8. Brand-new contact using the start prompt        -> send welcome message
#      Brand-new contact NOT using the start prompt    -> flag, silence
#   9. Referral program question                      -> answer directly
#  10. Clear "I'm ready / let's go / how do we continue" -> signup link
#  11. Specific product question                     -> send earning opportunities
#  12. Any reply right after the welcome              -> send earning opportunities
#  13. Unrecognised message at signup stage           -> resend signup link
#  14. Unrecognised text at explained stage           -> flag, silence
#  15. Anything else                                  -> silence, no chit-chat

async def handle_message(event, client):
    if not event.is_private:
        return

    sender = await event.get_sender()
    if not sender or getattr(sender, "bot", False):
        return

    chat_id  = event.chat_id
    raw_text = event.raw_text or ""
    text     = raw_text.strip()
    has_media = bool(event.media)

    sender_name = (
        f"@{sender.username}" if sender.username
        else (sender.first_name or str(chat_id))
    )
    username = sender.username
    is_test_user = bool(username) and username.lower() in TEST_USERNAMES

    stats["messages_today"] += 1
    hourly_messages[datetime.now(timezone.utc).hour] += 1
    log.info(f"[{sender_name}] {text[:80]!r}" + (" [media]" if has_media else ""))

    stage = get_stage(chat_id)

    # ── Test account — always gets a reply. "stats"/"status" pulls live stats;
    #    "reset" wipes this chat's saved progress so the next message replays
    #    the whole funnel from the welcome message instead of resuming where
    #    a previous test run left off. Ending ANY message with ">>" does both
    #    in one shot — wipes the saved progress AND immediately sends the
    #    welcome, so you can retest the whole flow from scratch without
    #    sending "reset" as a separate message first. Without ">>", messages
    #    fall through to the normal stage-aware funnel logic as usual ───────
    if is_test_user:
        cmd = text.lower().strip().lstrip("/")
        if cmd in ("stats", "status"):
            await send_reply(event, build_stats_reply())
            log.info(f"[{sender_name}] Test user requested stats")
            return
        if cmd == "reset":
            chat_states.pop(chat_id, None)
            clear_pending(chat_id)
            save_state()
            await send_reply(
                event,
                "🔄 Reset done — send any message to start the flow again from the welcome message.",
            )
            log.info(f"[{sender_name}] Test user reset their chat state")
            return
        if text.rstrip().endswith(">>"):
            chat_states.pop(chat_id, None)
            clear_pending(chat_id)
            await human_delay(event, client, 6.0, 11.0)
            await send_reply(event, random.choice(WELCOME_REPLIES))
            set_stage(chat_id, STAGE_WELCOMED, sender_name, username)
            stats["new_chats_today"] += 1
            pipeline["welcomed"] += 1
            _record_action(sender_name, "welcome")
            log.info(f"[{sender_name}] Test user restart trigger (>>) — reset and sent welcome")
            return
    else:
        # ── 0. Bot paused — master kill switch ─────────────────────────────────
        if bot_paused:
            log.info(f"[{sender_name}] Bot paused — reply suppressed")
            return

        # ── 1. Pre-existing / owner-handling contact — permanent silence ───────
        if stage == STAGE_OWNER:
            log.info(f"[{sender_name}] Owner-handled contact — silent")
            return

        # ── 2. You replied manually — hand the chat over for good ─────────────
        if await already_replied(client, chat_id):
            set_stage(chat_id, STAGE_OWNER, sender_name, username)
            clear_pending(chat_id)
            log.info(f"[{sender_name}] You've replied manually — bot silent from now on")
            return

    # ── 3. Scam-ish message — flag it, no auto-reply ──────────────────────────
    if text and is_scam_message(text):
        add_pending(chat_id, sender_name, username, "flagged", text)
        log.info(f"[{sender_name}] Flagged message — needs a reply")
        return

    # ── 4. Media message mid-flow — needs your eyes ────────────────────────────
    if has_media and stage != STAGE_NEW:
        add_pending(chat_id, sender_name, username, "photo", text or "[photo/attachment]")
        log.info(f"[{sender_name}] Sent a photo/file — needs a reply")
        return

    # ── 5. Says they've already registered/joined ─────────────────────────────
    if text and matches_already_joined(text):
        add_pending(chat_id, sender_name, username, "already_joined", text)
        log.info(f"[{sender_name}] Already joined — needs a reply")
        return

    # ── 6. Hesitation / reluctance ─────────────────────────────────────────────
    if text and matches_hesitation(text):
        add_pending(chat_id, sender_name, username, "hesitant", text)
        log.info(f"[{sender_name}] Hesitant — needs a reply")
        return

    # ── 7. Pure chit-chat once already in the flow — don't entertain it ───────
    if text and stage != STAGE_NEW and matches_chitchat(text):
        add_pending(chat_id, sender_name, username, "chitchat", text)
        log.info(f"[{sender_name}] Chit-chat — needs a reply")
        return

    # ── 8. Brand-new contact — only auto-welcome if they used the start prompt ─
    if stage == STAGE_NEW:
        if not (text and matches_start_prompt(text)):
            add_pending(chat_id, sender_name, username, "off_script", text or "[no text]")
            log.info(f"[{sender_name}] New contact didn't use the start prompt — needs a reply")
            return
        await human_delay(event, client, 6.0, 11.0)
        await send_reply(event, random.choice(WELCOME_REPLIES))
        set_stage(chat_id, STAGE_WELCOMED, sender_name, username)
        stats["new_chats_today"] += 1
        pipeline["welcomed"] += 1
        _record_action(sender_name, "welcome")
        log.info(f"[{sender_name}] Sent: welcome")
        return

    # ── 9. Referral program question — always answer ──────────────────────────
    if text and matches_referral_inquiry(text):
        await human_delay(event, client, 4.0, 8.0)
        await send_reply(event, REFERRAL_INFO_REPLY)
        stats["referral_inquiries"] += 1
        _record_action(sender_name, "referral")
        log.info(f"[{sender_name}] Sent: referral program info")
        return

    # ── 10. Clear join intent — signup link (or a short reminder) ─────────────
    if text and matches_join_intent(text):
        if stage == STAGE_SIGNUP:
            await human_delay(event, client, 3.0, 6.0)
            await send_reply(event, SIGNUP_LINK_REMINDER)
            _record_action(sender_name, "signup")
            log.info(f"[{sender_name}] Sent: signup link reminder")
            return
        name = get_name(chat_id)
        await human_delay(event, client, 5.0, 10.0)
        await send_reply(event, build_signup_message(name))
        set_stage(chat_id, STAGE_SIGNUP, sender_name, username)
        pipeline["signup_sent"] += 1
        _record_action(sender_name, "signup")
        log.info(f"[{sender_name}] Sent: signup link")
        return

    # ── 11. Specific product question — answer with the opportunities list ────
    if text and matches_info_request(text):
        name = get_name(chat_id)
        await human_delay(event, client, 5.0, 9.0)
        await send_reply_with_image(event, build_opportunities_message(name), ABOUT_IMAGE_URL)
        if stage in (STAGE_NEW, STAGE_WELCOMED):
            set_stage(chat_id, STAGE_EXPLAINED, sender_name, username)
            pipeline["info_sent"] += 1
        _record_action(sender_name, "info")
        log.info(f"[{sender_name}] Sent: earning opportunities (asked directly)")
        return

    # ── 12. Reply right after the welcome = their name -> opportunities list ──
    if stage == STAGE_WELCOMED:
        name = extract_name(text, fallback=sender.first_name or "")
        await human_delay(event, client, 5.0, 10.0)
        await send_reply_with_image(event, build_opportunities_message(name), ABOUT_IMAGE_URL)
        set_stage(chat_id, STAGE_EXPLAINED, sender_name, username, name=name)
        pipeline["info_sent"] += 1
        _record_action(sender_name, "info")
        log.info(f"[{sender_name}] Sent: earning opportunities (name: {name!r})")
        return

    # ── 13. Unrecognised message at signup stage — resend the link ────────────
    if stage == STAGE_SIGNUP:
        await human_delay(event, client, 3.0, 6.0)
        await send_reply(event, SIGNUP_LINK_REMINDER)
        _record_action(sender_name, "signup")
        log.info(f"[{sender_name}] Sent: signup link reminder (unrecognised msg at signup stage)")
        return

    # ── 14. Unrecognised text at explained stage — queue for human reply ──────
    if stage == STAGE_EXPLAINED and text:
        add_pending(chat_id, sender_name, username, "chitchat", text)
        log.info(f"[{sender_name}] Unrecognised msg in EXPLAINED stage — queued for reply")
        return

    # ── 15. Everything else — no unnecessary chit-chat, stay silent ───────────
    log.info(f"[{sender_name}] No matching rule — silent")


def build_opportunities_message(name: str = "") -> str:
    opener = f"Great to meet you, {name}! 🎉\n\n" if name else "Great to meet you! 🎉\n\n"
    return opener + random.choice(OPPORTUNITIES_BODIES)


def build_signup_message(name: str = "") -> str:
    who = name or "friend"
    opener = f"🟡 Perfect, {who}! You're just one step away from earning with Vireon Africa.\n\n"
    return opener + random.choice(SIGNUP_LINK_BODIES)


def build_stats_reply() -> str:
    """Plain-text stats summary sent to TEST_USERNAMES accounts on demand."""
    uptime_secs = 0
    if bot_status.get("since"):
        start = datetime.fromisoformat(bot_status["since"])
        uptime_secs = int((datetime.now(timezone.utc) - start).total_seconds())
    hours, rem = divmod(uptime_secs, 3600)
    minutes = rem // 60
    return (
        "📊 Vireon Africa Bot Stats\n\n"
        f"Status: {'🟢 Online' if bot_status.get('online') else '🔴 Offline'}"
        f"{' (paused)' if bot_paused else ''}\n"
        f"Uptime: {hours}h {minutes}m\n\n"
        f"Messages today: {stats['messages_today']}\n"
        f"New chats today: {stats['new_chats_today']}\n"
        f"Replies sent: {stats['replies_sent']}\n"
        f"Failed sends: {stats['failed_sends']}\n"
        f"Referral inquiries: {stats['referral_inquiries']}\n"
        f"Flags total: {stats['flags_total']}\n\n"
        f"Welcomed: {pipeline['welcomed']}\n"
        f"Info sent: {pipeline['info_sent']}\n"
        f"Signup links sent: {pipeline['signup_sent']}\n\n"
        f"Known chats: {len(chat_states)}\n"
        f"Needs your reply (pending): {len(pending_review)}\n"
        f"Push subscriptions: {len(push_subscriptions)}"
    )


# ─── Entry point ─────────────────────────────────────────────────────────────

async def _telegram_task(client):
    """Connect to Telegram and keep running. Starts after uvicorn is up."""
    # Give Railway's old container ~15 s to shut down before connecting.
    # Without this, rolling deploys overlap and both instances try to use the
    # same SESSION_STRING simultaneously, causing Telegram to revoke the session
    # with AUTH_KEY_DUPLICATED / "used under two different IP addresses".
    log.info("Waiting 15 s for previous container to shut down before connecting…")
    await asyncio.sleep(15)

    try:
        await client.start()
    except Exception as e:
        log.error(f"Telegram auth failed: {e}")
        if "two different IP" in str(e) or "AUTH_KEY_DUPLICATED" in str(e):
            log.error(
                "SESSION_STRING was used from two places at once and is now invalid. "
                "Remove SESSION_STRING from Railway env vars, redeploy to generate a "
                "fresh one, then set it again."
            )
        return

    if not SESSION_STR:
        print("\n" + "=" * 60)
        print("SESSION STRING (save as SESSION_STRING env var):")
        print(client.session.save())
        print("=" * 60 + "\n")

    # Mark online immediately after connecting — preload/catch-up happen in the
    # background so the dashboard doesn't show "Offline" during startup work.
    bot_status["online"] = True
    bot_status["since"]  = datetime.now(timezone.utc).isoformat()
    log.info(f"✅ Vireon Africa userbot connected to Telegram | Dashboard on port {PORT}")

    state_loaded = load_state()
    if not state_loaded:
        # First run (no state file) — mark pre-existing chats so the bot doesn't
        # auto-greet people you already know. On subsequent restarts we skip
        # this so the bot can continue mid-flow conversations without re-silencing them.
        await preload_existing_chats(client)
    else:
        log.info(f"State restored from disk — skipping preload ({len(chat_states)} chats already tracked)")

    # Welcome anyone who messaged today while the bot was offline
    await catch_up_unreplied(client)

    try:
        await client.run_until_disconnected()
    finally:
        bot_status["online"] = False
        log.warning("Bot disconnected from Telegram.")
        await send_push_notification(
            "⚠️ Vireon Africa Bot Offline",
            "The bot has disconnected from Telegram. Check Railway.",
        )


async def main():
    try:
        session = StringSession(SESSION_STR) if SESSION_STR else StringSession()
    except ValueError:
        log.error(
            "SESSION_STRING is set but isn't a valid Telethon session string "
            "(it must start with '1'). Generate one by running `python bot.py` "
            "locally with SESSION_STRING unset, completing the phone/code/2FA "
            "login prompts, and copying the exact string it prints — then set "
            "that as SESSION_STRING with no extra quotes or whitespace."
        )
        raise
    client = TelegramClient(session, API_ID, API_HASH)

    @client.on(events.NewMessage(incoming=True))
    async def dispatcher(event):
        try:
            await handle_message(event, client)
        except Exception as e:
            log.error(f"Handler error: {e}", exc_info=True)

    # Start HTTP server immediately so Railway's health check passes right away.
    # Telegram connection happens in the background concurrently.
    config = uvicorn.Config(app, host="0.0.0.0", port=PORT, log_level="warning")
    server = uvicorn.Server(config)
    log.info(f"🌐 Dashboard starting on port {PORT} — Telegram connecting in background…")

    await asyncio.gather(
        server.serve(),
        _telegram_task(client),
        daily_reset_task(),
    )


if __name__ == "__main__":
    asyncio.run(main())
