# Krosz sarcastic Reel series – production runbook

Series: 2 Reels/day (post 12:00 and 19:00 IST) for Instagram @krosz_visa via Metricool (blogId 7867174, tz Asia/Calcutta).
Each episode = ONE new real visa-rejection reason played as sarcasm. Never repeat a reason (see episodes.md).

## Characters (assets/*.png, fixed)
- Max (boy, orange hoodie): c1 neutral, d3 "manifesting", d1 sad/teary. Procrastinator, overconfident.
- Tia (girl, glasses, lavender hoodie): c2 sarcastic, d2 holding phone "Told you so". The sensible friend.
- Officer Deadpan (c3): deadpan airport officer, stamps rejections.
- Captain Passport (c4): talking passport mascot, British voice, closes the episode with a funny line + krosz.com CTA.
Voices: Max am_adam, Tia af_heart, Officer am_michael, Captain bm_george (Kokoro, local).

## Fixed episode structure (16 shots, ~45s)
hook(cp1) → tia1 → max1 → tia2 → max2 → freeze → title card → off1 → max3 → off2 → panic(max4) → stamp(off3) → sad(max5) → tia3 → cp2 → end card.
Line ids and speakers are FIXED: cp1 cp, tia1 tia, max1 max, tia2 tia, max2 max, off1 off, max3 max, off2 off, max4 max, off3 off, max5 max, tia3 tia, cp2 cp.
Each line = [id, who, spoken_text, shown_caption]. Spoken text: write numbers/₹/URLs as words ("krosz dot com", "eight hundred forty-seven rupees"). Keep each line short (<= 12 words), punchy, sarcastic, young-audience humour; max ~45s total.
Captain Passport (cp2) must end with a NEW funny closing line each episode (never "I am telling you" twice; ep3 used "I'm a passport, not a therapist!") and must mention krosz dot com.
Spec fields: see specs/ep3_photo.json (ann = small pill texts per line id; hook = [label1, big1, label2, big2]; ticker; title = 2 short lines max ~9 chars each; title_sub; freeze; stamp = 2 short lines; teaser = "Next: ... (Max again.)"; caption = Instagram caption).
Fit limits: hook big text <= 12 chars (hook_size 150; use 120 if longer), stamp lines <= 10 chars, freeze pill <= 32 chars.

## Brand / legal rules
Krosz blue #2e7af4 / navy #0b141f, logo already burned into video.py. No yellow. INR only. No approval or timeline guarantees, no fake testimonials, never say a third party submits. Always keep the end-card disclaimer ("Visa rules vary by country. AI-generated animation."). Reason must be a REAL common rejection reason; if mentioning country rules, verify with the Krosz_app MCP (query_canonicalvisadatav2) or avoid specifics.

## Commands
python3 make.py specs/<name>.json /tmp/<name>   # needs: pip install kokoro-onnx soundfile numpy scipy pillow boto3 --break-system-packages ; ffmpeg; Poppins font at /usr/share/fonts/truetype/google-fonts/Poppins-Bold.ttf (video.py FP) 
python3 r2up.py /tmp/<name>/final.mp4 <name>.mp4  # env R2_ACCOUNT R2_KEY R2_SECRET -> prints public URL
Takes ~6 min to render on 2 CPUs.

## Posting (Metricool createScheduledPost)
blogId 7867174; providers [{"network":"instagram"}]; instagramData {"type":"REEL","showReelOnFeed":true,"isAiGenerated":true}; media [public R2 url]; publicationDate {dateTime:"YYYY-MM-DDTHH:MM:00",timezone:"Asia/Calcutta"}; date ISO with +05:30; autoPublish true. Caption = spec caption.
After posting, append a line to episodes.md (date, slot, reason, R2 key, Metricool plannerUrl) and git push.
