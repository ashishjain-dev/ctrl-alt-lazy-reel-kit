# Style guides

One guide per art style, in plain words. Claude follows these when it writes custom art at runtime
(a character, a story picture, a whole scene; see [custom-art.md](custom-art.md)), so anything drawn for
any video matches the style. The first five also exist as built-in code in `engines/pillow/reelkit/art/`:
read that file as the reference implementation, and reuse its colours and helpers.

Every guide has the same parts: **surface** (background), **palette**, **line**, **fill**, **figures**
(people, animals, faces), **motion**, **impact** (the big moment), **text**, **frame** (border), **avoid**.

---

## Fish-Scale Folk (built in: `fish-scale-folk`, `art/folk.py`)
Inspired by Mithila folk painting.
- **Surface:** handmade cream paper (241, 227, 196) with faint fibres: `paper_texture(..., fibres=400)`.
- **Palette:** vermilion (205, 52, 34), turmeric (232, 166, 28), leaf green (62, 132, 70), indigo (44, 60, 128), soft pink (222, 118, 136), ink (34, 24, 20). Flat colour only, no gradients or shading.
- **Line:** a double outline on every shape: a thick ink line with a thin paper-coloured line inside it (`dbl()` in folk.py).
- **Fill:** every larger shape gets a pattern inside: fish scales, dots, hatching or cross-hatch (`fill_pattern` + `tile`). Neighbouring shapes use different patterns.
- **Figures:** big almond "fish" eyes with a dot pupil, faces frontal, simple stacked shapes for bodies; clothes patterned; jewellery as rows of coloured dots.
- **Motion:** smooth 30–60 fps, gentle sway.
- **Impact:** a layered red / yellow / paper star burst with double outlines.
- **Text:** heavy display font, vermilion fill with an ink + paper double stroke.
- **Frame:** red border with yellow triangles pointing inward, plus a double ink rule inside it.
- **Avoid:** gradients, soft shadows, realistic shading, thin single outlines, empty unpatterned areas.

## Rice Paper (built in: `rice-paper`, `art/ricepaper.py`)
Inspired by East Asian ink-wash painting.
- **Surface:** warm off-white rice paper (236, 231, 218) with many fibres.
- **Palette:** black ink only, used at many strengths; the single colour is vermilion (196, 48, 36) for a sun, a seal or one accent.
- **Line:** brush strokes that taper; a few confident strokes instead of full outlines (`soft_poly(..., width=)` with slight blur).
- **Fill:** translucent grey washes (`soft_poly` with alpha 0.15–0.6 and blur) that darken where they overlap; distant things lighter and blurrier (mist).
- **Figures:** suggested, not outlined: a few strokes for a body, dots for eyes.
- **Motion:** smooth, slow; things drift.
- **Impact:** an ink splatter (blobs flung outward) plus one fast brush arc.
- **Text:** dark ink, no box, appearing softly.
- **Frame:** none; a small red seal in a corner.
- **Avoid:** bright colours, hard flat fills, borders, patterns.

## Mud Wall (built in: `mud-wall`, `art/mudwall.py`)
Inspired by Warli wall painting.
- **Surface:** red-brown mud (146, 70, 46) with grainy texture.
- **Palette:** one colour, rice-paste white (246, 238, 224), on the mud.
- **Line:** thin white lines with a slight hand wobble.
- **Fill:** solid white small shapes, or outlines only; no other colours.
- **Figures:** people are two triangles meeting at the waist, a circle head and stick limbs (`MudWall.person()`); animals and birds from triangles and line-fans; huts from triangles and squares.
- **Motion:** stepped at **8 fps** with a 2 px wobble each step (`fps = 8`, `jitter`), like being redrawn by hand.
- **Impact:** rings of white dots expanding out.
- **Text:** white, slightly wobbling.
- **Frame:** a chain of white triangles around the edge.
- **Avoid:** any colour other than white, gradients, realistic proportions, thick outlines.

## Cyan Plan (built in: `cyan-plan`, `art/cyanplan.py`)
Inspired by engineering blueprints.
- **Surface:** cyanotype blue (22, 66, 140) with a fine grid every 30 px and a stronger line every 150 px.
- **Palette:** white line-work (232, 242, 255), pale blue for construction lines, one warm yellow (255, 214, 120) for alerts.
- **Line:** thin, even white lines; dashed lines for paths and hidden parts (`dashed`).
- **Fill:** none, or section hatching on solid parts.
- **Figures:** drawn as technical outlines with centre lines; label parts with callouts (a leader line plus mono text).
- **Motion:** smooth; add a reticle that tracks the target and labels that type in.
- **Impact:** concentric rings with tick marks and an "IMPACT" or "T+2.00s" label in yellow.
- **Text:** monospace, uppercase, like drawing notes; dimension lines with values.
- **Frame:** a single border line and a title block (project, sheet, scale, revision).
- **Avoid:** fills, colours other than white and one yellow, rounded cartoon shapes without labels.

## Cut Card (built in: `cut-card`, `art/cutcard.py`)
Inspired by layered paper cut-out animation.
- **Surface:** wavy strips of coloured paper for the sky (cool at the top, warm near the ground) and stacked white cloud strips.
- **Palette:** bright card colours: tomato (232, 74, 60), sunflower (255, 196, 64), sky blue, lilac, mint, peach.
- **Line:** no ink lines; a thin white "cut edge" (2–3 px) around every piece.
- **Fill:** flat card colour with a soft drop shadow under every piece (`shadow_poly`), deeper pieces having bigger shadows.
- **Figures:** built from a few flat card pieces layered on top of each other.
- **Motion:** stop motion at **12 fps** with a tiny jitter (`fps = 12`, `jitter = 1.6`).
- **Impact:** a layered paper starburst.
- **Text:** bold display font with a white edge and a soft shadow.
- **Frame:** none.
- **Avoid:** ink outlines, gradients inside pieces, smooth 60 fps motion.

---
The five styles below are not built in yet. Write them as custom art from these guides, or add them as
built-in `Painter` subclasses (see `skills/style-drop/SKILL.md`).

## Lamp Leather
Inspired by shadow-puppet theatre.
- **Surface:** a warm cotton screen lit from behind by an oil lamp: a soft yellow-orange glow in the centre that flickers, darker at the edges.
- **Palette:** translucent dyed-leather colours (deep red, ochre, green, indigo) that glow where the light passes through.
- **Line:** carved dark outlines; rows of small punched holes that let light through.
- **Fill:** semi-transparent colour over the glow.
- **Figures:** flat profiles with jointed limbs; thin control rods running off the bottom of the frame.
- **Motion:** smooth with a slight puppet bob; the glow flickers.
- **Impact:** the lamp flares bright, then settles.
- **Avoid:** fully opaque colours, frontal faces, missing rods.

## Temple Glass
Inspired by stained glass.
- **Surface:** an arched window with iron bars; light glowing through from behind.
- **Palette:** jewel colours (ruby, sapphire, emerald, amber), glowing.
- **Line:** thick dark lead lines between every piece of glass.
- **Fill:** every shape is broken into a mosaic of glass pieces with slight colour variation.
- **Motion:** smooth; light shimmers across the glass.
- **Impact:** a white-gold glass star and a flare.
- **Avoid:** thin lines, large single-colour areas.

## Cel Burst
Inspired by TV-anime cel shading.
- **Surface:** a saturated gradient sky with huge cumulus clouds.
- **Palette:** bright, high contrast.
- **Line:** bold ink outlines.
- **Fill:** two-tone cel shading with a hard shadow edge.
- **Motion:** speed lines on fast moves.
- **Impact:** a 3-frame black/white impact flash, then one red frame, then a lens flare.
- **Avoid:** soft gradients on figures, thin lines.

## Wave Block
Inspired by woodblock prints.
- **Surface:** a deep blue gradient sky, a red sun, horizontal mist bands, wood grain over everything.
- **Palette:** flat, muted (Prussian blue, rust, cream, grey-green).
- **Line:** black key-block lines of even weight.
- **Fill:** flat areas; water and clouds as stylised curling foam.
- **Text:** a vertical cartouche with a small red seal.
- **Avoid:** bright saturated colours, soft shading.

## Gold Court
Inspired by court miniature painting.
- **Surface:** a lapis sky band with gold scroll clouds, a pale wash below, rolling green hills with round dotted trees and a river.
- **Palette:** jewel-flat colours and burnished gold, pearl-white dots.
- **Line:** hairline outlines.
- **Figures:** elegant profiles, large eyes, fine patterned clothing.
- **Impact:** gold rays.
- **Frame:** a red border with a gold vine.
- **Avoid:** thick outlines, dark backgrounds.
