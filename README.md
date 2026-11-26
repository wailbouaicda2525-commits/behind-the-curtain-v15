# BEHIND THE CURTAIN — V15 BEAST 100% Zero-Touch YouTube Autopilot ($0/month)

Autonomous **Tier-1 US / Anglosphere** Cold War, CIA/KGB, Nuclear Close Calls & Secret History YouTube factory powered by **V15 BEAST MODE** (`en-GB-RyanNeural`, Esri Dark 3D Cartography, Real Archival Photography, Oscilloscope + 16-Band Spectrum, Auto High-CTR Thumbnails).

## Publishing Cadence (Fully Automatic)
- **4× Daily V15 BEAST Shorts (`9:16`, 1080×1920 @ 30fps):**
  `daily_shorts_4x.yml` → `0 12,16,20,0 * * *` (07:00, 11:00, 15:00, 19:00 US EST) — powered by a 110+ unique declassified dossier catalog.
- **1× Massive Adaptive Deep Single-Topic Documentary EVERY 2 DAYS (`16:9`, 1920×1080 @ 24fps + Auto High-CTR Thumbnail):**
  `longform_doc_every_2days.yml` → `0 18 1-31/2 * *` (Odd calendar days at 18:00 UTC / 1:00 PM US EST).
  - **Natural Adaptive Runtime (12 to 30 minutes!):** Automatically scales from **7 chapters (~12–15 min)** for focused dossiers up to **15 chapters (~25–30 min)** for epic subjects — zero artificial 15-min ceiling and zero fluff padding!
  - **Parallel Multi-Core Rendering:** Renders chapters concurrently across GitHub Actions' 4-vCPU runner (~18–24 min even for a 28–30 min 1080p film!).

## Required GitHub Secrets (`Settings → Secrets and variables → Actions`)
| Secret | Required | Description |
|---|---|---|
| `YOUTUBE_CLIENT_ID` | **Yes** | Google Cloud OAuth Desktop Client ID (**dedicated free GCP Project #1 for Behind The Curtain**) |
| `YOUTUBE_CLIENT_SECRET` | **Yes** | Google Cloud OAuth Desktop Client Secret |
| `YOUTUBE_REFRESH_TOKEN` | **Yes** | Refresh token generated via `python3 get_refresh_token.py` (authorized on `@behindthecurtainworld`) |
| `GEMINI_API_KEY` | Recommended | Free key from `aistudio.google.com` (100% unique investigative scripts) |
| `GROQ_API_KEY` | Optional | Free backup key from `console.groq.com` (`llama-3.3-70b-versatile`) |
| `TELEGRAM_BOT_TOKEN` | Optional | Telegram bot alerts when each Short / Documentary goes live |
| `TELEGRAM_CHAT_ID` | Optional | Your Telegram chat ID |

## Important Quota & Free Minutes Setup
1. **Separate Free Google Cloud Project ($0):** Peak day uses `4 × 1,600 + 1,650 = 8,050 / 10,000` free YouTube Data API v3 units. Always keep **Behind The Curtain** and **The Daily Archive** on **2 separate FREE Google Cloud Projects** so each channel gets its own full `10,000 units/day`!
2. **Unlimited Free GitHub Actions Minutes:** Keep this repo **Public** to receive **UNLIMITED free GitHub Actions minutes** (GitHub Secrets remain 100% encrypted and hidden; `.gitignore` blocks all credentials). On Private repos, parallel rendering keeps combined 2-channel usage around `~1,250–1,450 / 2,000` free minutes/month.
3. **Important Windows Upload Note:** Push this repo via `git push` (not web drag-and-drop), because GitHub's web uploader silently skips hidden `.github/workflows/` folders.
4. **Phone Verification:** Verify the channel once at `youtube.com/verify` so custom thumbnails (`thumbnails.set`) and videos >15 minutes publish automatically without HTTP 403 errors.
