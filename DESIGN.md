---
name: Coco Neo
description: Product page for Coco Neo cold pressed coconut oil, made in Kerala.
colors:
  ground: "#ffffff"
  surface: "#efeeeb"
  ink: "#1f0f07"
  muted: "#5a4a3e"
  accent: "#2f6b1f"
  accent-press: "#255617"
  palm: "#1e3a1a"
  gold: "#e9d57a"
  gold-ink: "#3a2c05"
  star: "#c48a12"
  on-dark: "#f3f3f0"
typography:
  display:
    fontFamily: "Rokkitt, Roboto Slab, Rockwell, Georgia, serif"
    fontSize: "clamp(4.5rem, 15vw, 15rem)"
    fontWeight: 800
    lineHeight: 0.8
    letterSpacing: "-0.02em"
  head:
    fontFamily: "Rokkitt, Roboto Slab, Rockwell, Georgia, serif"
    fontSize: "clamp(2rem, 1.2rem + 2.2vw, 3.5rem)"
    fontWeight: 800
    lineHeight: 0.92
    letterSpacing: "-0.01em"
  lead:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "clamp(1.25rem, 1.1rem + 0.5vw, 1.5rem)"
    fontWeight: 400
    lineHeight: 1.45
  body:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "1.125rem"
    fontWeight: 400
    lineHeight: 1.6
  small:
    fontFamily: "Literata, Georgia, serif"
    fontSize: "0.875rem"
    fontWeight: 400
    lineHeight: 1.6
rounded:
  none: "0px"
  pill: "999px"
spacing:
  gutter: "clamp(16px, 2.5vw, 32px)"
  inside: "24px"
  section-phone: "112px"
  section: "160px"
components:
  button-primary:
    backgroundColor: "{colors.accent}"
    textColor: "{colors.ground}"
    rounded: "{rounded.pill}"
    height: "56px"
    padding: "0 28px"
  button-primary-hover:
    backgroundColor: "{colors.accent-press}"
  button-ink:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-dark}"
    rounded: "{rounded.pill}"
    height: "56px"
  button-tone:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.pill}"
    height: "56px"
  pack-option:
    backgroundColor: "{colors.surface}"
    textColor: "{colors.ink}"
    rounded: "{rounded.none}"
    padding: "16px"
  pack-option-selected:
    backgroundColor: "{colors.ink}"
    textColor: "{colors.on-dark}"
  chip:
    backgroundColor: "{colors.surface}"
    rounded: "{rounded.pill}"
    height: "44px"
---

# Coco Neo design system

## Overview

The clean category standard, chosen by the owner: a premium FMCG product page in the class of Tata Simply Better. White ground, the product photograph leads, crisp slab type that echoes the "NEO" on the bottle label, and almost no decoration. The page is a split stage: on desktop the bottle stays fixed on the left (and changes picture as each section of the reading column arrives), while the facts scroll on the right. Below the split the page runs full width in bands of flat colour.

## Colors

Taken from the bottle label. **Ink** (espresso) is the wordmark brown and all running text. **Accent** (seal green) is reserved for the main buying action and small confirmations. **Gold** is the oil itself, used as one full band (the 24°C test), the footer name and the cart count. **Palm** is the one dark green band (the comparison table). **Surface** is a single tone step from the white ground and separates panels; there are no borders or shadows at rest.

## Typography

Two faces. **Rokkitt 800** for display and headings, in capitals only for the product title. **Literata** for everything read. Five sizes: display (footer name only), head, lead, body (18px), small (14px). Headlines stay within two lines at every width. No eyebrow labels, no tracked small capitals, no monospace.

## Layout

Equal outer gutters (`spacing.gutter`). Desktop: 47% fixed stage, reading column max 640px. Sections 160px apart (112px on phones). Below 1000px the stage becomes a 52svh picture above the reading column. Long reference content (label, process) is set as real tables with dotted leaders; questions are run-in paragraphs in two columns, never an accordion.

## Elevation & Depth

Flat. Surfaces are separated by tone. Only things that truly float carry a shadow: the cart drawer when open, the review dialog, the toast, the phone buy bar and the open phone menu.

## Shapes

Two shapes only: square corners for photographs, panels and pack options; full pills for every button and chip. The process slip has a regular zigzag bottom edge, like a printed receipt.

## Components

Pill buttons in three fills (accent, ink, tone). Pack options are filled squares that invert to ink when chosen. Stars are drawn SVG, partially filled for averages. Review cards have no boxes: rating, title, text, optional photo, name, verified mark.

## Do's and Don'ts

- Do keep the buy box (title, price, pack size, add to cart) in the first screen.
- Do show proof from the label: certifications, nutrition, the 24°C purity test.
- Do keep reviews flagged as placeholders until real, verified reviews replace them.
- Don't add eyebrows, emoji, numbered steps, gradients, hairline dividers or resting shadows.
- Don't add a third typeface or a sixth type size.
- Don't invent claims: prices, reviews, counts, awards or health benefits must be real.

Motion: one entrance per section (parts rise 24px and fade in, 70ms apart), a slow drift on the fixed stage photo, a crossfade when the stage changes picture, and the footer name settling from 92% to full size as it scrolls in. All of it is off under reduced motion.
