# V-bot — Vireon Africa Telegram Sales Funnel Userbot

This is a Telegram **userbot** (it logs in as a real Telegram *user account*,
not a classic `@BotFather` bot) that runs an automated DM funnel for Vireon
Africa sign-ups, with a live web dashboard.

## Important: this automates a personal account's DMs, not a channel post feed

A Telegram *channel* only lets you broadcast posts — it has no concept of a
bot replying to individual members in DMs. What this bot actually does is log
into one of **your own Telegram accounts** (via the Telegram API, not the Bot
API) and auto-reply to people who message that account directly, walking them
through: welcome → earning opportunities → free signup link → hand off to you
personally for anything ambiguous (someone saying they've already joined,
hesitation, receipts/screenshots, etc.).

The typical setup: you post/promote in your channel, tell people to DM a
specific account (or use it as your channel's admin contact), and this bot
runs the DM conversation on that account's behalf.

## Flow

1. **WELCOME** — first message sends the Vireon Africa intro.
2. **OPPORTUNITIES** — the next reply (or a direct question) sends the
   `about.jpg` image with the full earning-opportunities list as its caption.
3. **SIGNUP** — once someone signals they're ready, the bot sends your free
   signup/referral link.
4. **HUMAN TAKEOVER** — anything that isn't a clean "next step" (already
   joined, hesitation, small talk, flagged messages, photos mid-flow) gets
   zero auto-reply. It's queued on the dashboard under "Needs Your Reply"
   (with a push notification) so you can jump in personally. The bot never
   improvises small talk.

State survives restarts: chat progress + the pending-reply queue are written
to `STATE_FILE` after every change, so a user who replies days later picks up
exactly where they left off.

Live dashboard at `/` — real-time logs, stats, a "Needs Your Reply" queue,
Web Push notifications, PWA-installable.

## Files

| File | Purpose |
|---|---|
| `bot.py` | The bot + dashboard (single file) |
| `requirements.txt` | Python dependencies |
| `Procfile` | Tells Railway/Heroku how to start it (`web: python bot.py`) |
| `runtime.txt` | Pins the Python version |
| `.gitignore` | Keeps secrets/session files out of git |

## Environment variables you need to set

Set these in your host's dashboard (e.g. Railway → your service → **Variables**).
Never commit real values to git — only set them as environment variables.

### 1. `API_ID` and `API_HASH` (required)

These identify the *application* making the Telegram API connection (separate
from your bot/user login itself).

1. Go to **https://my.telegram.org** and log in with the phone number of the
   Telegram account you want the bot to run as.
2. Click **API development tools**.
3. Fill in the short form (App title / Short name — anything works, e.g.
   "VireonBot" / "vireonbot"). Platform can be "Other".
4. Submit — you'll immediately see **App api_id** (a number) and
   **App api_hash** (a long hex string). Copy both.
5. Set:
   - `API_ID` = the numeric id
   - `API_HASH` = the hash string

### 2. `SESSION_STRING` (required after first run)

This is the login token that lets the bot act as your Telegram account
without scanning a QR code or entering an OTP every time it restarts.

1. Leave `SESSION_STRING` **unset** for the very first deploy.
2. Deploy the bot and watch the logs. Telethon will prompt for:
   - your phone number (international format, e.g. `+2348012345678`)
   - the login code Telegram sends you (via the Telegram app/SMS)
   - your 2FA password, if you have one enabled
   - Since most hosts (Railway included) don't give you an interactive
     terminal, do this step **locally first**: run `python bot.py` on your
     own machine once (with `API_ID`/`API_HASH` set), log in when prompted,
     and the script will print:
     ```
     ============================================================
     SESSION STRING (save as SESSION_STRING env var):
     AgAiA...(long string)...
     ============================================================
     ```
3. Copy that entire string and set it as `SESSION_STRING` in your host's
   environment variables.
4. Redeploy. From now on the bot logs in instantly using the string — no
   phone/code prompt needed.

**Security note:** the session string is equivalent to your account password —
anyone who has it can log in as you. Never share it, never commit it, and if
it ever leaks, terminate it from Telegram (Settings → Devices) and generate a
fresh one.

**Only run one instance at a time.** The bot already waits 15s on startup to
let a previous deploy shut down first — running the *same* session string
from two places simultaneously invalidates it (`AUTH_KEY_DUPLICATED`).

### 3. `VAPID_PRIVATE_KEY` / `VAPID_PUBLIC_KEY` (optional — enables push notifications)

These power the dashboard's "🔔 push notification when someone needs your
reply" feature. Skip them if you don't need mobile push alerts — the bot and
dashboard work fine without them, you'll just rely on checking the dashboard.

Generate a VAPID key pair locally:
```bash
pip install pywebpush
python -c "from py_vapid import Vapid01; v = Vapid01(); v.generate_keys(); print('PRIVATE:', v.private_pem()); print('PUBLIC:', v.public_key())"
```
(Or use an online VAPID key generator / the `web-push generate-vapid-keys` Node CLI.)
Set the resulting private/public values as `VAPID_PRIVATE_KEY` and
`VAPID_PUBLIC_KEY`.

### 4. `PORT` (optional — Railway sets this automatically)

The dashboard's HTTP port. Railway injects this itself; only set it manually
if you're running elsewhere (e.g. locally: `PORT=8080`).

### 5. `STATE_FILE` (optional)

Path where chat progress + the reply queue are persisted as JSON, so a
restart doesn't lose anyone's place in the conversation. Defaults to
`bot_state.json` next to `bot.py`. If your host wipes the filesystem on
redeploy (Railway's default), point this at a **mounted Volume** path instead,
e.g. `/data/bot_state.json`, so state survives deploys.

### 6. `SIGNUP_URL` (optional — recommended)

Your real Vireon Africa signup/referral link. Every reply that quotes a
signup link (`SIGNUP_LINK_BODIES`, `SIGNUP_LINK_REMINDER`, `REFERRAL_INFO_REPLY`)
reads from this one variable, so changing it here updates every reply
instantly — no code edit or redeploy of `bot.py` needed, just update the env
var and restart the service.

If unset, it falls back to a placeholder
(`https://vireonwebsite.com.ng/register`) — set this to your real
signup/referral link before going live.

### 7. `ABOUT_IMAGE_URL` (optional)

The image sent alongside the earning-opportunities message. Defaults to
`https://vireonwebsite.com.ng/assets/images/about.jpg`. This step is always
one image with the opportunities list as its caption (Telegram caps photo
captions at 1024 characters as a safety net — if the caption is too long, the
overflow automatically moves into a follow-up message instead of being cut
off).

### 8. `TEST_USERNAMES` (optional — recommended for testing)

Comma-separated Telegram `@usernames` (with or without the `@`) that always
get a live reply from the bot, e.g.:
```
TEST_USERNAMES=clintdoesdev,myseconddaccount
```
Messages from these accounts:
- **Bypass the master pause switch** and the owner-silence / manual-takeover
  rules, so you can run the full funnel end-to-end at any time, even while
  the dashboard's pause toggle is on or the account has chat history.
- Still go through the normal funnel logic otherwise (scam filter, earning
  opportunities, signup link, etc.) — so it behaves like a real lead for
  testing purposes.
- Can send **`stats`** or **`/stats`** (or **`status`** / **`/status`**) to
  get an instant text summary of today's numbers — messages, new chats,
  replies sent, flags, pipeline counts, known chats, and pending "needs your
  reply" count — without opening the dashboard.
- Can send **`reset`** or **`/reset`** to wipe that chat's saved progress.
  Without this, once you've walked through the funnel once your test chat is
  saved mid-flow (e.g. at the signup step) and every message after just
  continues from there — the same as it would for a real lead. `reset` clears
  it so the very next message you send gets the welcome message again, letting
  you replay the whole funnel from scratch as many times as you want.

To test: message your bot's account from a second Telegram account whose
username is listed in `TEST_USERNAMES`. Send `reset` any time you want to
restart the flow from the beginning.

## Content you still need to fill in / may want to customize in `bot.py`

Everything a contact sees is defined at the very top of `bot.py`, in the
"PROMPTS CONFIG" block — it's already written for Vireon Africa (the welcome
message, the full earning-opportunities list, and a free-signup CTA), but
check these before going live:

- `SIGNUP_URL` — set via the **`SIGNUP_URL` env var** (see above); currently
  falls back to a placeholder if unset. No code edit needed to change it.
- `WELCOME_REPLIES` — first-contact greeting
- `OPPORTUNITIES_BODIES` — the full Vireon earning-opportunities list (sent
  as the caption on `ABOUT_IMAGE_URL`)
- `SIGNUP_LINK_BODIES` / `SIGNUP_LINK_REMINDER` — signup instructions
- `REFERRAL_INFO_REPLY` — sent when someone specifically asks about the
  referral program
- The keyword lists further down (`SCAM_KEYWORDS`, `JOIN_KEYWORDS`,
  `INFO_TRIGGERS`, `REFERRAL_TRIGGERS`, `ALREADY_JOINED_PHRASES`,
  `HESITATION_PHRASES`, etc.) drive intent detection — add phrases your own
  audience actually uses (including local slang) for reliable matching.

Also update the VAPID contact email in `_push_sync()`
(`vapid_claims={"sub": "mailto:support@vireonwebsite.com.ng"}`) to a real
inbox you control — it's only used as a contact address if a push provider
needs to reach you, but it should be a real address, not a placeholder.

## Deploying on Railway

1. Push this repo to GitHub (done) and create a new Railway project from it.
2. Add the environment variables above.
3. Deploy — Railway reads `Procfile` and runs `python bot.py`.
4. Visit the deployed URL to see the live dashboard.
5. Generate your `SESSION_STRING` locally first (step 2 above) and set it
   before your first real deploy, so Railway doesn't need an interactive
   login prompt it can't give you.

## Running locally

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
export API_ID=your_api_id
export API_HASH=your_api_hash
python bot.py
```
