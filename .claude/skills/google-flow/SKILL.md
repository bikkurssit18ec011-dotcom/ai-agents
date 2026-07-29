---
name: google-flow
description: "Use when working with Google Flow or Veo 3.1 for AI video — writing video prompts, getting consistent characters, building a video pipeline, or integrating Flow with Midjourney, Kling, or CapCut."
---

# Google Flow: Complete Skill Guide for Advanced AI Creators

**Google Flow** is Google's consolidated AI filmmaking platform at labs.google/fx/tools/flow, powered by **Veo 3.1** from DeepMind. It is the first major AI video tool to generate synchronized dialogue, SFX, ambient audio, and music natively alongside video. The platform absorbed Google Whisk and ImageFX in a February 2026 redesign, making it a unified image → video → scene workspace.

**Access**: Public (149+ countries), web-only (Chrome recommended), 18+, no mobile app.  
**Status as of March 2026**: Generally available, actively being updated. Scene Builder and some audio features still show instability.

---

## Platform Architecture

Three DeepMind models power Flow in one interface:
- **Veo 3.1** — video generation (T2V, F2V, Ingredients)
- **Nano Banana Pro** (Imagen variant) — built-in image generation (free in Flow)
- **Gemini** — natural language interpretation and prompt assistance

Projects contain: asset library, generation interface with multiple modes, and Scene Builder timeline.

---

## Core Video Generation Modes

### Text to Video (T2V)
- Write a prompt → generate a cinematic clip
- Output: **4, 6, or 8 seconds** at **720p, 24 FPS**
- Native audio (dialogue, SFX, ambient, music) generated alongside video
- Cost: ~**10 credits** per generation

### Frames to Video (F2V)
- Upload start and/or end frame images → animate the transition
- Includes dedicated camera control presets (pan, tilt, dolly, crane)
- Most precise visual control mode
- Cost: ~**100 credits** per generation

### Ingredients to Video
- Upload up to **3 reference images** (characters, objects, backgrounds) + prompt
- Best character consistency in Flow's toolkit
- Google recommends subjects on plain/segmented backgrounds
- Cost: ~100 credits; use plain-background references; maintain consistent visual style across all 3 images

---

## Video Editing & Refinement Tools

| Tool | Function |
|---|---|
| **Extend** | Continue a clip from its last frame; up to ~60s total (coherence degrades after 16–24s) |
| **Insert Object** | Add new elements to existing scenes via text prompt + drag-box placement |
| **Remove Object** | AI video inpainting — remove unwanted elements |
| **Camera Controls** | Post-generation camera redirection: pan, tilt, zoom, dolly, tracking, crane |
| **Drawing Instructions** | Draw directly on reference images to indicate desired movement direction |

---

## Scene Builder (Timeline Editor)

Drag-and-drop timeline for multi-clip sequencing. Key features:
- **Jump To**: Gemini analyzes how the previous clip ended, generates a new shot preserving character context in a different setting
- **Extend**: Seamlessly continue action from the last frame
- Save any video frame as a reusable image asset

**Known limitations (as of March 2026)**:
- Timeline state **resets on project exit** — clips save individually but must be reassembled
- One scene per project
- Jump To and Extend **only work with Veo 2** (no audio on extended sequences)
- Audio frequently **strips on Scene Builder export** — workaround: download clips individually, stitch in CapCut/Premiere/DaVinci

---

## Audio Generation: Flow's Killer Advantage

Veo 3/3.1 natively generates synchronized audio — this is Flow's primary competitive differentiator vs. all other AI video tools.

**Audio types generated**:
- Dialogue with lip-sync (~80% accuracy single character, ~40% multi-character)
- Ambient environmental sound (wind, traffic, crowd)
- Sound effects (footsteps, doors, impacts)
- Background music (genre/mood/instrument-directed)

**Prompting audio effectively**:
- Put audio instructions in the **first half** of the prompt
- Use quotation marks for dialogue: `She says, "We need to leave now."`
- Prefix SFX: `SFX: sneakers squeaking on hardwood floor`
- Describe music: `Upbeat Chicago footwork beat, 808 bass, high-hat patterns`
- Select **"Highest Quality"** mode — Preview/Draft mode does NOT generate audio
- Keep dialogue short enough to fit the 8-second clip window

---

## Gemini Image Integration (Native)

Nano Banana Pro is built directly into Flow — the most seamless image-to-video pipeline available.

**Recommended two-stage workflow**:
1. Generate start frame in Nano Banana Pro ("Medium shot of a dancer in streetwear, plain studio background")
2. Generate end frame ("Low-angle tracking shot, dancer landing pose, dramatic lighting")
3. Feed both into Frames to Video with camera movement and audio prompt

**Ingredients workflow**:
1. Generate character/object/background references in Nano Banana Pro
2. Combine up to 3 in Ingredients to Video
3. @ symbol in prompt box references assets by name

**External images**: Flow accepts uploads from any source — Midjourney, Photoshop, photography. Drag into workspace or use Add button.

---

## Cross-Platform Integrations

### Midjourney → Flow
- Generate images in Midjourney → download PNG/JPEG → upload as Ingredients
- Best practice: Midjourney for distinctive hero aesthetics, Nano Banana Pro for ecosystem consistency
- Do not mix style types (anime + photorealistic causes subject drift)
- Place the most identity-defining image first in Ingredients order

### Flow → CapCut
- Export as MP4 or MOV (H.264) → import directly into CapCut
- CapCut now natively integrates Veo 3.1 internally for mid-workflow generation
- CapCut workflow: assemble timeline → AI auto-captions (syncs to Flow's native audio) → color correct across clips from different AI generators → add music/effects → publish to TikTok/YouTube/Instagram
- **Critical**: color correct across generators to normalize visual style before publishing

### Ideal Multi-Platform Pipeline
```
1. Gemini          → Script, prompt brainstorming, storyboard outlines
2. Midjourney      → Hero character images, distinctive aesthetic frames
   Nano Banana Pro → Supporting references, ecosystem-consistent images
3. Flow/Veo 3.1    → Dialogue-heavy scenes, audio-native narrative content
4. Kling AI        → Fast B-roll, native 4K close-ups, motion-heavy dance/action
5. Pika Labs       → Viral effects (explode, melt, inflate), stylized social content
6. CapCut          → Final assembly, color normalization, captions, publishing
```

**Estimated cost**: $77–356/month depending on tier mix.

---

## Head-to-Head Comparisons

### Flow vs. Kling AI
| | Flow/Veo 3.1 | Kling 3.0 |
|---|---|---|
| Audio | ✅ Native dialogue + SFX + music | ❌ Audio synthesis less mature |
| Resolution | Upscaled 4K (Ultra) | ✅ True native 4K |
| Motion quality | 24 FPS cinematic | ✅ 30 FPS, superior motion tracking |
| Clip length | 8s base, ~60s chained | 15s standard (5 min avatar) |
| Character consistency | Ingredients-dependent | ✅ AI Director system |
| Price (Pro) | $19.99/month | ~$37/month |
| **Best for** | Dialogue, audio-native content | Dance, fast B-roll, high-volume |

### Flow vs. Runway Gen-4.5
- Runway leads on character consistency and editing tools (30+ tools, 60 FPS, $12–28/month)
- Flow leads on native audio and Google ecosystem integration
- For independent creators: Runway Pro ($28/month) often better value
- For Google enterprise teams: Flow + Vertex AI makes more strategic sense

### Flow vs. Pika Labs
- Pika: $10/month, viral Pikaffects (explode/melt/crush), social-first, beginner-friendly
- Flow: Professional, audio-native, cinematic, higher cost
- They complement each other — use Pika for viral effects, Flow for narrative

---

## Prompt Engineering

### The Official Five-Part Formula
```
[Cinematography] + [Subject] + [Action] + [Context] + [Style & Ambiance]
```

**Example**:
> "Medium tracking shot of a dancer in streetwear performing explosive hip-hop footwork on a gritty urban sidewalk at dusk. Camera follows low, emphasizing rapid foot movements. Neon signs reflect off wet pavement. Cinematic, shallow depth of field. Heavy bass beat and sneaker scuffs on concrete."

### Camera Terms Veo Understands
**Movement**: dolly in/out, tracking shot, crane shot, aerial view, slow pan left/right, tilt up/down, POV shot, static shot, arc shot  
**Composition**: wide shot, close-up, extreme close-up, low angle, two-shot, over-the-shoulder, medium shot  
**Lens**: shallow depth of field, wide-angle lens, soft focus, macro lens, rack focus, 35mm lens look

### High-Impact Style Modifiers
- `cinematic` — #1 quality trigger (professional lighting, color grading, composition)
- `film grain` — analog texture
- `golden hour` — warm flattering light
- `neon-lit` — urban/cyberpunk
- `warm orange-teal grade` — popular cinematic color grading
- `35mm lens look` — classic street photography aesthetic
- `wet pavement` — dramatically improves urban scene quality (reflections are a model strength)

### Timestamp Multi-Shot Prompting
```
[00:00-00:02] Medium shot from behind a young explorer approaching a glowing cave entrance...
[00:02-00:04] Reverse shot of the explorer's face, eyes widening with wonder...
[00:04-00:06] Tracking shot following the explorer into the cave...
[00:06-00:08] Wide, high-angle crane shot revealing the vast crystal cavern...
```

### What to Avoid
- Excessively detailed prompts — Veo can't follow too many simultaneous instructions
- Negative language ("no walls") — describe inclusions, not exclusions
- Forgetting `No subtitles. No text overlays.` when you don't want on-screen text
- Dialogue that doesn't fit in 8 seconds
- Budget 2–3 generations per scene — expect iteration

### Content-Specific Prompt Guidance

**Dance/Footwork**:
- "dynamic camera following the footwork" as direction
- Name the dance style explicitly (hip-hop, breaking, popping, street style)
- Describe clothing/fabric movement for visual interest
- One move sequence per 8-second clip
- Save key frames as Ingredients for consistency across clips
- Consider Kling for complex choreography (superior motion tracking)

**Fashion Showcases**:
- Describe fabric texture, materials, colors with precision
- Use slow camera movements (slow tracking, dolly) to showcase garments
- Specify: `silk swirling`, `linen draping`, `leather catching light`
- High-key lighting for editorial; dramatic backlighting for high fashion
- 9:16 portrait mode supported natively

**Urban Street Scenes**:
- `35mm lens look` + `wet pavement` + `neon-lit` = reliable urban aesthetic
- Golden hour and nighttime neon produce best atmosphere
- Include ambient audio: `SFX: traffic, distant sirens, crowd murmur`
- Narrow alleys and corner stores read more authentic than generic "city streets"

**Cinematic Hip-Hop Visuals**:
- Flow is the best current tool for this use case
- Audio-native generation means beats, dialogue, and visuals created as one
- Describe music explicitly: genre, tempo, instruments
- Pair Midjourney (distinctive artist frames) + Flow (animated narrative)
- Finish in CapCut with captions and color normalization

---

## Known Limitations (as of March 2026)

| Limitation | Severity | Workaround |
|---|---|---|
| Character consistency | High | Ingredients to Video + verbatim character descriptions in every prompt |
| Human emotions (robotic expressions) | Medium | Lean into style over realism; use close-ups sparingly |
| 8-second clip ceiling | High | Chain + Extend; budget coherence for ~3–4 extensions max |
| Scene Builder resets on exit | High | Download clips immediately; reassemble in CapCut |
| Audio strips on Scene Builder export | High | Download individual clips; stitch externally |
| Unexpected cuts mid-generation | Medium | Regenerate; adjust pacing in prompt |
| Unwanted text/captions in output | Medium | Add "No subtitles. No text overlays." to every prompt |
| Jump To / Extend only on Veo 2 (no audio) | Medium | Accept silent extended sequences; add audio in CapCut |
| Interface bugs (stuck at 99%, slow load) | Medium | Refresh; retry; avoid peak hours |

---

## Pricing

| Tier | Price | Credits | Resolution | Watermark |
|---|---|---|---|---|
| Free | $0 | 100 + 50 daily | 720p | Visible + SynthID |
| Google AI Pro | $19.99/month | 1,000/month | 1080p upscale | Visible + SynthID |
| Google AI Ultra | $249.99/month | 25,000/month | 4K upscale | **SynthID only** |

**Credit costs**: T2V ~10 credits, F2V ~100 credits, Extend ~10 credits  
**Pro breakdown**: 1,000 credits ≈ 100 T2V generations/month ≈ 3/day  
**Commercial use**: GA features allow commercial use; Veo 3 Pre-GA features are explicitly prohibited from commercial use regardless of payment tier — verify current GA/Pre-GA status directly with Google before any commercial deployment.

All outputs carry invisible **SynthID** watermarks regardless of tier.

---

## Quick Reference: When to Use Flow vs. Alternatives

| Use Case | Best Tool |
|---|---|
| Dialogue-driven narrative content | **Flow** |
| Audio-native cinematic scenes | **Flow** |
| Complex choreography / dance | **Kling AI** |
| High-volume social B-roll | **Kling AI** |
| Character-consistent multi-scene | **Runway Gen-4.5** |
| Viral transformation effects | **Pika Labs** |
| Distinctive aesthetic hero images | **Midjourney** |
| Ecosystem reference image generation | **Nano Banana Pro (in Flow)** |
| Final assembly + publishing | **CapCut** |
