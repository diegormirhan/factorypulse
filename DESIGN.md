---
name: FactoryPulse
description: An inspectable machine-health console shaped like a warm enamel railway interlocking desk.
colors:
  paper: "#e9e7df"
  panel: "#f4f2eb"
  ink: "#171916"
  muted: "#5e625c"
  line: "#9b9c93"
  track: "#30332f"
  green: "#146b46"
  amber: "#b86408"
  red: "#b82d2a"
  blue: "#245f7b"
  focus: "#006c91"
typography:
  display:
    fontFamily: '"Barlow Condensed", sans-serif'
    fontSize: "clamp(3.2rem, 6.7vw, 6rem)"
    fontWeight: 600
    lineHeight: 0.92
    letterSpacing: "-0.025em"
  headline:
    fontFamily: '"Barlow Condensed", sans-serif'
    fontSize: "clamp(2rem, 3vw, 3rem)"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "-0.015em"
  title:
    fontFamily: '"Barlow Condensed", sans-serif'
    fontSize: "1.2rem"
    fontWeight: 600
    lineHeight: 1
    letterSpacing: "normal"
  body:
    fontFamily: '"IBM Plex Sans", "Segoe UI", sans-serif'
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "normal"
  label:
    fontFamily: '"IBM Plex Sans", "Segoe UI", sans-serif'
    fontSize: "0.74rem"
    fontWeight: 400
    lineHeight: 1.5
    letterSpacing: "0.1em"
rounded:
  square: "0"
  lamp: "50%"
spacing:
  xs: "0.5rem"
  sm: "0.75rem"
  md: "1rem"
  lg: "1.5rem"
  xl: "2.5rem"
  page-gutter: "4vw"
  panel: "clamp(2rem, 4vw, 4rem)"
  section: "clamp(4rem, 8vw, 8rem)"
components:
  button-primary:
    backgroundColor: "{colors.ink}"
    textColor: "#ffffff"
    typography: "{typography.body}"
    rounded: "{rounded.square}"
    padding: "0 1.25rem"
    height: "58px"
  button-primary-hover:
    backgroundColor: "#30342e"
    textColor: "#ffffff"
  input:
    backgroundColor: "#fbfaf5"
    textColor: "{colors.ink}"
    typography: "{typography.body}"
    rounded: "{rounded.square}"
    padding: "0.8rem"
    height: "50px"
  scenario-selected:
    backgroundColor: "{colors.ink}"
    textColor: "#ffffff"
    rounded: "{rounded.square}"
    padding: "0.55rem 0.8rem"
  decision-badge:
    backgroundColor: "transparent"
    textColor: "{colors.muted}"
    typography: "{typography.label}"
    rounded: "{rounded.square}"
    padding: "0.35rem 0.65rem"
---

# Design System: FactoryPulse

## Overview

**Creative North Star: "The Enamel Interlocking Desk"**

FactoryPulse treats machine health as a physical route of inspectable signals. The visual world borrows the discipline of a railway interlocking desk: a warm enamel ground, near-black route rules, square controls, condensed operational headings, and status lamps that feel mounted rather than illustrated.

The system is direct, evidence-led, and intentionally unlike a generic dark AI dashboard or a grid of floating metric cards. It keeps the working surface dense but orderly, reserves dimensional effects for live signal hardware, and pairs every green, amber, or red state with explicit language.

**Key Characteristics:**

- Warm, low-glare enamel surfaces with near-black operational rules.
- Condensed uppercase headings paired with highly legible sans-serif working text.
- Square controls and bordered sections arranged as one continuous workstation.
- Signal color used for machine state, always reinforced by text.
- Flat evidence surfaces with depth reserved for physical lamps and housings.

## Colors

The palette reads as an industrial control surface: restrained warm neutrals carry the interface while saturated signal colors communicate operational state.

### Primary

- **Rail Ink** (`ink`): Primary text, selected controls, and the full-width assessment action.
- **Track Graphite** (`track`): Route lines, heavy evidence rules, and physical signal housings.

### Secondary

- **Gauge Blue** (`blue`): The probability fill on the threshold comparison track.
- **Focus Blue** (`focus`): A dedicated, high-contrast keyboard focus outline rather than a decorative accent.

### Tertiary

- **Proceed Green** (`green`): Ready, completed-route, and nominal decision states.
- **Watch Amber** (`amber`): Checking, awaiting-decision, and watch states.
- **Stop Red** (`red`): Model errors, form errors, and inspection-required states.

### Neutral

- **Warm Enamel** (`paper`): The page ground and unfilled route nodes.
- **Control Panel** (`panel`): The assessment form surface.
- **Secondary Copy** (`muted`): Explanatory text, labels, units, and inactive controls.
- **Hairline Metal** (`line`): Section boundaries, switch housings, badges, and table-like dividers.

### Named Rules

**The Signal-plus-Text Rule.** Green, amber, and red never carry meaning alone; each state also changes a visible badge, status label, or decision sentence.

**The Enamel Majority Rule.** Warm neutrals occupy most of the screen. Signal hues are reserved for status, focus, and measured progress.

## Typography

**Display Font:** Barlow Condensed (with sans-serif fallback)  
**Body Font:** IBM Plex Sans (with Segoe UI and sans-serif fallbacks)  
**Label Font:** IBM Plex Sans (with Segoe UI and sans-serif fallbacks)

**Character:** Barlow Condensed gives the console its terse, industrial voice; IBM Plex Sans keeps measurements, explanations, controls, and evidence calm and readable. Both fonts are shipped locally, so the interface does not depend on a network request.

### Hierarchy

- **Display** (semibold, fluid oversized scale, tight leading): The failure-path thesis; uppercase and balanced across lines.
- **Headline** (semibold, fluid large scale, solid leading): Major work-surface and evidence headings.
- **Title** (semibold, compact scale): Route stops and driver-section headings.
- **Body** (regular, base scale, 1.5 line-height): Instructions, descriptions, and decision explanations; supporting paragraphs stay near 47–58 characters wide where the layout permits.
- **Label** (regular, compact scale, wide tracking, uppercase): Legends, signal labels, and other operational metadata.

### Named Rules

**The Two-Voice Rule.** Use condensed uppercase type for commands and hierarchy; use IBM Plex Sans for reading, data entry, and explanation.

**The Tabular Measurement Rule.** Probabilities, metrics, measurements, and impacts use tabular numerals so changing values remain visually stable.

## Layout

The interface is a centered workstation capped at 1440px, with a shared 4vw horizontal gutter. Its first route section uses an asymmetrical two-column introduction followed by a four-stop horizontal signal path. The main workspace is a continuous two-column surface: the assessment form takes roughly two thirds and the decision panel one third, separated by a single rule rather than card gaps. The primary assessment action spans the full form width.

Spacing is generous between narrative regions and deliberately tighter inside operational groups. Form fields use three columns at wide widths, evidence metrics use four, and section padding scales with the viewport. At 900px, the route introduction, evidence heading, and workspace become single-column; form fields and metrics move to two columns. At 580px, fields and metrics become single-column and the signal route turns into a vertical track. Mobile gutters become a fixed 1.25rem.

**The Continuous Work-Surface Rule.** Related controls and results share bordered surfaces; do not break the assessment into a collection of floating cards.

## Elevation & Depth

The system is flat by default. Hierarchy comes from tonal surfaces, strong track rules, and shared borders—not ambient card shadows. Shadows appear only where the interface depicts a physical signal lamp or housing, giving live state a localized glow and weight.

### Shadow Vocabulary

- **Housing Weight** (`0 9px 20px rgba(30, 33, 29, 0.25)`): Grounds the dark signal housing against the decision panel.
- **Status Lamp Glow** (`0 3px 16px` with the active state color): Communicates that a nominal, watch, or critical lamp is energized.
- **System Lamp Glow** (`0 2px 7px` with the ready or checking color): A smaller glow reserved for the topbar model-status indicator.

### Named Rules

**The Hardware-Only Depth Rule.** Surfaces remain flat; only signal hardware receives shadow or glow.

## Shapes

Controls, panels, badges, inputs, and switches are square-cornered. Borders are thin and structural, while the heavy route line creates a rail-like horizontal datum. Circles are reserved for lamps and route nodes, and the tall rectangular signal housing makes the decision state feel like physical equipment. There are no ornamental pills or softly rounded cards.

**The Circle Means Signal Rule.** Circular geometry identifies a live lamp or route node; it is not a general-purpose decoration.

## Components

### Buttons

- **Shape:** Full-width, square-cornered command bar with a 58px minimum height.
- **Primary:** Rail Ink with white text, a left-aligned command, and a right-facing inline arrow.
- **Hover / Focus:** Hover shifts to a slightly lighter near-black; keyboard focus uses the global 3px Focus Blue outline with a 3px offset.
- **Disabled:** Keeps the command legible, changes to muted gray, and uses a wait cursor while scoring.

### Chips

- **Style:** The scenario selector is a square segmented control inside a one-pixel Hairline Metal frame on Warm Enamel.
- **State:** The selected scenario inverts to Rail Ink and white text; `aria-pressed` mirrors the visible state.

### Cards / Containers

- **Corner Style:** Square throughout.
- **Background:** Warm Enamel for the page, Control Panel for the form, and a darker enamel tone for the decision surface.
- **Shadow Strategy:** Flat except for signal hardware, as defined in Elevation & Depth.
- **Border:** One-pixel structural dividers; the evidence board begins with a three-pixel Track Graphite rule.
- **Internal Padding:** Fluid panel padding; metric cells use compact directional padding to maintain table-like alignment.

### Inputs / Fields

- **Style:** Warm-white fill, one-pixel gray stroke, square corners, and a 50px minimum height. Units are positioned inside the right edge; numeric text uses tabular figures.
- **Focus:** The global Focus Blue outline sits outside the field; hover darkens the border to Rail Ink.
- **Error / Disabled:** Submission errors appear as persistent Stop Red text under the command bar. Native required, min, max, and step constraints remain intact.

### Navigation

The 72px topbar uses a three-part grid: a condensed uppercase wordmark with an inline rail glyph, a text-labeled model-status lamp, and an underlined API documentation link. At tablet widths the status row moves below the two outer items rather than disappearing.

### Signal Route

A track rule joins four labeled circular nodes: Sense, Calibrate, Decide, and Inspect. Completed nodes use Proceed Green; the active decision begins in Watch Amber and changes to state color after scoring. On narrow screens the route rotates into a vertical line while keeping labels left-aligned.

### Decision Signal

The decision surface combines a physical lamp housing, an oversized tabular probability, a text badge, an explanatory sentence, and a threshold track. Nominal, watch, and critical variants update all of these channels together. The probability fill animates over 500ms with an ease-out curve and collapses to effectively instant motion when reduced motion is requested.

## Do's and Don'ts

### Do:

- **Do** build new operational regions as parts of the same bordered workstation.
- **Do** pair every state color with a visible status word or sentence.
- **Do** reserve condensed uppercase type for hierarchy, routes, and commands.
- **Do** keep model evidence visibly connected to the decision and use tabular numerals for changing values.
- **Do** preserve the 900px and 580px layout transitions when adding content to this surface.

### Don't:

- **Don't** turn the console into a dark AI dashboard or a grid of isolated metric cards.
- **Don't** add rounded cards, pill-shaped controls, gradients, glass effects, or decorative glow.
- **Don't** use green, amber, or red as an unlabeled status channel.
- **Don't** add shadows to ordinary panels, forms, or evidence containers.
- **Don't** fabricate production claims, customer evidence, savings, or safety certification in interface copy.
