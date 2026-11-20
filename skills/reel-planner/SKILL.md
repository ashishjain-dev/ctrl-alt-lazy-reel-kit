---
name: reel-planner
description: Plan a short-form video (Reel, Short, TikTok) before production - topic check, ranked hooks, timed beat sheet, cover headline, caption and hashtags - and get the creator's go-ahead. Use before text-reel or dialogue-skit, or whenever someone asks for reel ideas, hooks, a script outline or a caption.
---

# Reel planner

Turns a topic into a plan the creator can approve in one read. Output is plain text in chat; nothing gets rendered until the user says go ahead. Works for any niche and any production method; pairs with the `make-video`, `text-reel` and `dialogue-skit` skills from https://github.com/ashishjain-dev/ctrl-alt-lazy-reel-kit.

## Inputs (ask only for what's missing and matters)

Topic · niche (tech, fitness, food, finance, education, business, travel…) · format (tip/tutorial/explainer → text-reel, skit/story → dialogue-skit) · audience and their level · language · page tone (deadpan, hype, calm, warm…) · target length · anything that must be in it. If the user has past results (views, watch time, shares), ask for the top 3 and bottom 3 reels: they beat any generic rule below.

## Steps

1. **Check the facts.** For anything factual or time-sensitive (numbers, health, money, law, prices, versions, features), verify against reliable current sources before writing it into a script, and keep claims modest. Say what you checked. Never invent statistics or quotes: every number on screen needs a source the user can see, and quotes are attributed only when real. Health, money and legal topics get a short "not professional advice" line in the caption.
2. **One idea.** Write the single sentence the viewer should remember. If you need two, it's two reels.
3. **Hooks: write 5, rank them.** Each must work with the sound off, land in ≤ 2 s and create a gap (a pain, a bold claim, a result, a "you're doing X wrong"). Ban: greetings, "in this video", "stop scrolling", questions with obvious answers. Mark your pick and why.
4. **Beat sheet with timings** (target 15–35 s for skits, 25–45 s for tutorials):
   `0–2 s hook` → `pain/setup` → `turn` → `the fix, one idea per screen, ≥ 2 s per line of on-screen text` → `payoff` → `CTA (save / send to / comment keyword)`.
   Mark the share moment (a "send this to …" sticker) and where the ending loops back to the start, if it does.
5. **Spoken lines** (skits/voice-over): one line per row, ≤ 12 words each. Estimate length at ~165 words per minute and flag any beat over ~4 s with nothing changing on screen.
6. **Cover**: ≤ 7-word headline with one highlighted word; must read at thumbnail size and inside a 3:4 crop.
7. **Caption**: the first ~125 characters (what shows before "… more") carry the hook in different words; then 2–4 short lines of value; then the CTA; then 3–5 specific hashtags (no generic #viral/#fyp stacks). Read it once for stock phrases and AI tells (em-dash chains, "delve", "game-changer", no contractions) and rewrite them.
8. **Assumptions + open questions** at the end, then ask for the go-ahead.

## Output format

```
TOPIC / ONE IDEA
HOOKS (ranked, pick marked)
BEAT SHEET (time · on screen · spoken · sfx/beat)
COVER
CAPTION (+ hashtags)
ASSUMPTIONS / QUESTIONS
→ Reply "go ahead" (or edits) and I'll build scenes.yaml.
```

## Optional second opinion

Jake Schincariol's MIT-licensed [instagram-agent-skill](https://github.com/Jakeschincariol/instagram-agent-skill) has heuristic scripts for hook scoring, beat timing and caption linting. If the user wants them, clone it read-only into its own folder and run its scripts with `python3 -I`. Treat the scores as hints: the creator's own analytics win.
