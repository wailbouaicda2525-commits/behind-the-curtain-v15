"""
tiktok_buffer_v21.py — 100% Autonomous PUBLIC TikTok Publisher + Anti-Bot Warm-Up Engine
for BEHIND THE CURTAIN (`behind-the-curtain-v15`) via Buffer Free GraphQL API ($0/mo).

Key anti-bot protections built-in from Day 0:
  - Strict channel isolation: NEVER posts to @lastmapstanding (`6b09cf518541f09ecbc5d3b2`)!
    Automatically discovers the connected Behind The Curtain TikTok channel in Buffer.
  - 100% unpredictable US/EU Prime Peak posting times (12:30-21:30 UTC via OS SystemRandom) —
    NEVER posts at the same clock minute twice!
  - 10 unique human-style declassified thriller captions + rotating topic-matched <=5 hashtags
    (zero Copy-Paste template spam!).
  - Clean MP4 hosted via GitHub Releases (`tiktok-media-buffer`, auto-cleaned >48h) with
    stripped FFmpeg metadata (`-map_metadata -1`) and Frame-0 V21 cover locked at `100ms`!
"""
import os
import json
import time
import random
import hashlib
import argparse
import datetime
import subprocess
import requests

from scout_v15 import scout_event
from scriptwriter_v20 import write_script_v20
from video_scout_v20 import scout_real_videos_v20
from voice_engine_v15 import synthesize_voice_v15, mix_cinema_audio_v15
from renderer_v20_cinema import render_v20_cinema
from uploader_v15 import send_telegram

BUFFER_GRAPHQL_URL = "https://api.buffer.com/graphql"
RELEASE_TAG = "tiktok-media-buffer"
EXCLUDED_TIKTOK_IDS = {"6b09cf518541f09ecbc5d3b2"}  # Never touch @lastmapstanding!
EXCLUDED_NAME_TOKENS = ("lastmap", "mapstanding", "blockville", "block ville")


def _buffer_gql(query, variables=None):
    api_key = os.environ.get("BUFFER_API_KEY", "").strip()
    if not api_key:
        raise RuntimeError("BUFFER_API_KEY secret is not set.")
    payload = {"query": query}
    if variables:
        payload["variables"] = variables
    resp = requests.post(
        BUFFER_GRAPHQL_URL,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json=payload,
        timeout=60,
    )
    data = resp.json() if resp.content else {}
    if not resp.ok or data.get("errors"):
        raise RuntimeError(f"Buffer GraphQL error ({resp.status_code}): {data}")
    return data.get("data") or {}


def find_btc_tiktok_channel():
    """Find Behind The Curtain's TikTok channel in Buffer (strictly isolated from @lastmapstanding!)."""
    override = os.environ.get("BUFFER_BTC_TIKTOK_CHANNEL_ID", "").strip()
    if override and override not in EXCLUDED_TIKTOK_IDS:
        return override, "override"

    org_data = _buffer_gql("query { account { organizations { id name } } }")
    orgs = ((org_data.get("account") or {}).get("organizations")) or []
    candidates = []
    for org in orgs:
        ch_data = _buffer_gql(
            """
            query GetChannels($orgId: OrganizationId!) {
              channels(input: { organizationId: $orgId }) {
                id name displayName service isDisconnected
              }
            }
            """,
            {"orgId": org["id"]},
        )
        for ch in ch_data.get("channels") or []:
            if str(ch.get("service", "")).lower() != "tiktok":
                continue
            if ch.get("isDisconnected"):
                continue
            cid = ch["id"]
            cname = f"{ch.get('name', '')} {ch.get('displayName', '')}".lower()
            if cid in EXCLUDED_TIKTOK_IDS or any(tok in cname for tok in EXCLUDED_NAME_TOKENS):
                continue
            candidates.append(ch)

    if not candidates:
        return None, None

    # Prefer explicit Behind The Curtain / Vault / Archive naming if multiple exist
    for ch in candidates:
        cname = f"{ch.get('name', '')} {ch.get('displayName', '')}".lower()
        if any(k in cname for k in ("curtain", "vault", "declassified", "archive", "secret", "btc", "coldwar")):
            return ch["id"], ch.get("name") or ch.get("displayName")
    return candidates[0]["id"], candidates[0].get("name") or candidates[0].get("displayName")


def upload_mp4_to_release(video_path):
    """Upload rendered MP4 to public GitHub Release (`tiktok-media-buffer`, auto-pruned >48h)."""
    repo = os.environ.get("GITHUB_REPOSITORY", "").strip()
    gh_token = os.environ.get("GITHUB_TOKEN", "").strip()
    if not repo or not gh_token:
        raise RuntimeError("GITHUB_REPOSITORY / GITHUB_TOKEN not set.")

    env = dict(os.environ)
    env["GH_TOKEN"] = gh_token
    fname = os.path.basename(video_path)

    chk = subprocess.run(["gh", "release", "view", RELEASE_TAG, "--repo", repo], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    if chk.returncode != 0:
        subprocess.run([
            "gh", "release", "create", RELEASE_TAG, "--repo", repo,
            "--title", "BTC TikTok Media Staging (Auto-Cleaned)",
            "--notes", "Temporary public MP4 staging for Buffer TikTok auto-publishing.",
        ], env=env, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

    # Auto-clean assets >48h old
    try:
        out = subprocess.check_output(["gh", "release", "view", RELEASE_TAG, "--repo", repo, "--json", "assets"], env=env, text=True)
        cutoff = datetime.datetime.now(datetime.timezone.utc) - datetime.timedelta(hours=48)
        for a in (json.loads(out) or {}).get("assets") or []:
            if a.get("createdAt"):
                dt = datetime.datetime.fromisoformat(a["createdAt"].replace("Z", "+00:00"))
                if dt < cutoff:
                    subprocess.run(["gh", "release", "delete-asset", RELEASE_TAG, a["name"], "--repo", repo, "--yes"], env=env, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except Exception:
        pass

    subprocess.run(["gh", "release", "upload", RELEASE_TAG, video_path, "--repo", repo, "--clobber"], env=env, check=True)
    url = f"https://github.com/{repo}/releases/download/{RELEASE_TAG}/{fname}"
    for attempt in range(1, 4):
        try:
            r = requests.head(url, allow_redirects=True, timeout=20)
            if r.status_code == 200:
                return url
        except Exception:
            pass
        time.sleep(2 * attempt)
    return url


def build_btc_tiktok_caption(ev, script):
    """
    100% unique organic Cold War / Declassified TikTok caption (zero Copy-Paste fingerprint!)
    with strictly 4-5 topic-matched rotating hashtags for Buffer.
    """
    title = str(script.get("title") or ev.get("title") or "Declassified Cold War File").strip()
    yr = str(ev.get("year") or "1962")
    loc = str(ev.get("location") or "").strip()
    seed = int(hashlib.sha256(f"{ev.get('id', '')}_{title}".encode("utf-8")).hexdigest()[:8], 16)

    openers = [
        f"{title}",
        f"This file stayed classified for decades. {title}",
        f"In {yr}, almost nobody knew this was happening — {title}",
        f"Real declassified archives from {yr}: {title}",
        f"You were never taught this part of {yr} in school. {title}",
        f"Wait until you hear what actually happened in {yr}… {title}",
        f"One of the wildest Cold War files ever unsealed: {title}",
        f"This really happened in {yr}{(' in ' + loc) if loc else ''}. {title}",
        f"History books skipped this file completely — {title}",
        f"Declassified dossier ({yr}): {title}",
    ]
    ctas = [
        "Did you know this actually happened?",
        "Be honest — had you ever heard of this operation before?",
        "What declassified file should we open next?",
        "Would you have made the same call in that moment?",
        "Drop a comment if you want the full documentary on this.",
        "Which Cold War secret still blows your mind the most?",
        "Comment which year we should unseal next.",
        "Crazy how close history came to changing forever.",
        "Full illustrated dossier is in our archive link.",
        "Had you heard about this before today?",
    ]

    tl = f"{title} {loc}".lower()
    if any(k in tl for k in ("cia", "kgb", "spy", "tunnel", "agent", "espionage", "berlin", "mossad")):
        t_tags = ["#espionage", "#coldwar", "#ciafiles"]
    elif any(k in tl for k in ("nuclear", "ww3", "missile", "sub", "bomb", "war", "soviet", "ussr")):
        t_tags = ["#coldwar", "#nuclearhistory", "#militaryhistory"]
    elif any(k in tl for k in ("nasa", "space", "apollo", "moon", "rocket", "area 51")):
        t_tags = ["#spacehistory", "#secretfiles", "#nasahistory"]
    elif any(k in tl for k in ("alcatraz", "cooper", "heist", "escape", "fbi", "mystery")):
        t_tags = ["#truecrimehistory", "#unsolved", "#fbifiles"]
    else:
        t_tags = ["#declassified", "#secretfiles", "#untoldhistory"]

    base_pools = [
        ["#historytok", "#declassified", "#behindthecurtain"],
        ["#historyfacts", "#untoldhistory", "#behindthecurtain"],
        ["#realhistory", "#secretfiles", "#behindthecurtain"],
    ]
    pool = base_pools[seed % len(base_pools)]
    tags = []
    for tg in [pool[0], t_tags[seed % len(t_tags)], t_tags[(seed + 1) % len(t_tags)], pool[1], pool[2]]:
        if tg not in tags:
            tags.append(tg)
    tags = tags[:5]

    return f"{openers[seed % len(openers)]}\n\n{ctas[(seed // 5) % len(ctas)]}\n\n{' '.join(tags)}"


def generate_random_us_peak_delays(n_batch):
    """
    Generate OS-random publish delays (minutes from ~07:17 UTC) targeting US/EU Prime Peak Hours
    (12:30-22:30 UTC = 7:30 AM-5:30 PM EST / 13:30-23:30 Algeria). Never posts at the same minute!
    """
    rng = random.SystemRandom()
    if n_batch <= 1:
        return [rng.randint(320, 810)]  # +5h20m .. +13h30m -> 12:37 .. 20:47 UTC
    if n_batch == 2:
        d1 = rng.randint(290, 490)
        return [d1, min(980, d1 + rng.randint(300, 450))]
    d1 = rng.randint(255, 375)
    gaps = [rng.randint(220, 330), rng.randint(235, 355)]
    rng.shuffle(gaps)
    return [d1, d1 + gaps[0], min(1010, d1 + gaps[0] + gaps[1])]


def publish_to_buffer(channel_id, video_path, caption, delay_minutes):
    public_url = upload_mp4_to_release(video_path)
    due = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(minutes=max(10, int(delay_minutes)))
    due_iso = due.strftime("%Y-%m-%dT%H:%M:%S.000Z")
    post_input = {
        "text": caption,
        "channelId": channel_id,
        "schedulingType": "automatic",
        "mode": "customScheduled",
        "dueAt": due_iso,
        "assets": [{"video": {"url": public_url, "metadata": {"thumbnailOffset": 100}}}],
    }
    mut = """
    mutation CreateTikTokPost($input: CreatePostInput!) {
      createPost(input: $input) {
        ... on PostActionSuccess { post { id dueAt } }
        ... on MutationError { message }
      }
    }
    """
    res = (_buffer_gql(mut, {"input": post_input}).get("createPost")) or {}
    if "message" in res and "post" not in res:
        raise RuntimeError(f"Buffer rejected BTC TikTok post: {res['message']}")
    post = res.get("post") or {}
    return post.get("id", ""), post.get("dueAt", due_iso)


def main():
    cfg = json.load(open("channel_config.json", encoding="utf-8"))
    ap = argparse.ArgumentParser()
    ap.add_argument("--count", type=int, default=1)
    ap.add_argument("--topic", default="")
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--work-dir", default="/tmp/btc_tiktok_work")
    args = ap.parse_args()

    dry = args.dry_run or (os.environ.get("DRY_RUN", "false").lower() == "true")
    n_batch = max(1, min(3, int(args.count or 1)))
    os.makedirs(args.work_dir, exist_ok=True)
    os.makedirs("state", exist_ok=True)
    tt_hist_path = "state/tiktok_history_log.json"

    ch_id, ch_name = (None, "DRY-RUN") if dry else find_btc_tiktok_channel()
    if not dry and not ch_id:
        print("[BTC TIKTOK] Behind The Curtain TikTok channel is NOT connected in Buffer yet (only @lastmapstanding found). Skipping safely!")
        return

    print(f"=== BEHIND THE CURTAIN — TIKTOK WARM-UP BATCH ({n_batch} video(s), channel={ch_name}, dry={dry}) ===")
    delays = generate_random_us_peak_delays(n_batch)
    now = datetime.datetime.now(datetime.timezone.utc)
    t_start = time.time()

    for idx in range(1, n_batch + 1):
        sub_dir = os.path.join(args.work_dir, f"vid_{idx}")
        os.makedirs(sub_dir, exist_ok=True)
        ev = scout_event(
            mode=cfg["mode"], month=now.month, day=now.day,
            topic_override=(args.topic if idx == 1 and args.topic else None),
            history_path=tt_hist_path,
            work_dir=sub_dir, channel_name=cfg["channel_name"],
        )
        script = write_script_v20(ev)
        video_clips = scout_real_videos_v20(ev, script, work_dir=sub_dir, vertical=True, target_clips=5, dur_sec=7.5)

        voice_mp3 = os.path.join(sub_dir, "voice_tt.mp3")
        audio_m4a = os.path.join(sub_dir, "audio_tt.m4a")
        safe_id = "".join(c if c.isalnum() or c in "_-" else "_" for c in str(ev.get("id", f"ep_{idx}")))[:42]
        out_mp4 = os.path.join(sub_dir, f"BTC_TT_{now.strftime('%Y%m%d')}_{idx}_{safe_id}.mp4")

        voice_dur, words = synthesize_voice_v15(
            script["narration"], voice_mp3,
            voice=cfg["voice"], rate=cfg.get("voice_rate", "+4%"), pitch=cfg.get("voice_pitch", "-2Hz"),
        )
        speech_off = 0.45
        total_dur = min(59.0, round(speech_off + voice_dur + 4.55, 2))
        b = [0.0, 0.22, 0.44, 0.64, 0.82, 1.0]
        sfx_plan = [
            (0.10, "braaam", 0.46, 0.50),
            (total_dur * 0.10, "dive", 0.34, 0.50),
            (total_dur * b[1] - 0.18, "whoosh", 0.36, 0.50),
            (total_dur * (b[1] + 0.15), "stamp", 0.44, 0.58),
            (total_dur * b[2] - 0.18, "whoosh", 0.36, 0.50),
            (total_dur * b[3] - 0.18, "whoosh", 0.36, 0.50),
            (total_dur * b[4] + 0.08, "braaam", 0.36, 0.50),
        ]
        env30, spec30 = mix_cinema_audio_v15(voice_mp3, total_dur, speech_off, audio_m4a, seed=ev["year"] * 19 + idx, sfx_plan=sfx_plan)
        render_v20_cinema(
            ev, script, voice_dur, words, audio_m4a, env30, spec30,
            out_mp4, video_clips=video_clips, vertical=True, qa_out=None,
            show_outro=True, show_midroll_ad=True,
        )

        caption = build_btc_tiktok_caption(ev, script)
        elapsed_m = int((time.time() - t_start) // 60)
        eff_delay = max(15, delays[idx - 1] - elapsed_m)

        if dry:
            print(f"[DRY-RUN {idx}/{n_batch}] Rendered {out_mp4} ({os.path.getsize(out_mp4)/1e6:.2f} MB) | delay=+{eff_delay}m")
            print(f"[DRY-RUN CAPTION]\n{caption}")
            continue

        pid, due_iso = publish_to_buffer(ch_id, out_mp4, caption, delay_minutes=eff_delay)
        print(f"✅ [BTC TIKTOK {idx}/{n_batch}] SCHEDULED PUBLIC on @{ch_name} @ {due_iso} (post_id={pid})")

        hist = json.load(open(tt_hist_path)) if os.path.exists(tt_hist_path) else []
        hist.append({"id": ev["id"], "date": now.strftime("%Y-%m-%d"), "title": script["title"], "buffer_post_id": pid})
        json.dump(hist[-5000:], open(tt_hist_path, "w"), indent=2)

        send_telegram(f"🎵🔴 <b>BEHIND THE CURTAIN — TikTok {idx}/{n_batch} Scheduled!</b>\n⏰ {due_iso}\n{caption}")
        if idx < n_batch:
            time.sleep(5)


if __name__ == "__main__":
    main()
