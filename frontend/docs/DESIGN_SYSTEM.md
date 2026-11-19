# CiteVerify AI — Design System Specification

## 1. Brand Color Palette (Immutable)

| Token | CSS Variable | Hex | Description |
|---|---|---|---|
| Background | `--bg` | `#FFF8E8` | Warm cream primary canvas background |
| Card | `--card` | `#FFFFFF` | Elevated cards, tables, inputs, modals |
| Primary | `--primary` | `#F4B860` | Warm golden amber for buttons, progress, active indicators |
| Secondary | `--secondary` | `#FFDCA8` | Soft pastel amber for active nav, secondary actions |
| Highlight | `--highlight` | `#FFF0D6` | Sidebar, callouts, light tinted surfaces |
| Heading | `--heading` | `#8D6E63` | Warm brown for titles and prominent headings |
| Border | `--border` | `#F0E4D2` | Card borders and structural dividers |

---

## 2. Derived Supporting Tokens

| Token | CSS Variable | Hex | Description |
|---|---|---|---|
| Ink | `--ink` | `#3E2F27` | Primary text and button text |
| Muted Ink | `--ink-muted` | `#7A685D` | Secondary text, captions, metadata |
| Border Input | `--border-input` | `#A08B78` | Form control outlines and ghost borders |
| Focus Ring | `--focus` | `#8D6E63` | Keyboard focus ring |

---

## 3. Semantic Verification Palette

| Verdict | Icon / Border | Pale Background | Badge Text |
|---|---|---|---|
| **Supported** | `#39765B` | `#E4F1EA` | `#1F5A42` |
| **Partially Supported** | `#B68A42` | `#F7EBCF` | `#7A5A14` |
| **Unsupported** | `#B94D4D` | `#F6E1E1` | `#8F2E2E` |
| **Contradictory** | `#74518C` | `#EDE3F3` | `#54346B` |
| **Potentially Outdated** | `#B77B35` | `#F8E7D2` | `#8A5214` |
| **Needs Human Review** | `#766F68` | `#ECE8E4` | `#4F4943` |

### Citation Mapping Palette:
- **Matched:** Supported palette (`#39765B` / `#E4F1EA` / `#1F5A42`)
- **Partially Matched:** Partially Supported palette (`#B68A42` / `#F7EBCF` / `#7A5A14`)
- **Unmatched:** Unsupported palette (`#B94D4D` / `#F6E1E1` / `#8F2E2E`)
- **Missing Reference:** Needs Human Review palette (`#766F68` / `#ECE8E4` / `#4F4943`)

*Rule:* Every status and verdict badge must pair an SVG icon with an explicit text label. Color is never the sole information channel.

---

## 4. Dark Mode Palette

| Token | Hex Value |
|---|---|
| Background | `#1E1814` |
| Card | `#2A221C` |
| Highlight | `#33291F` |
| Secondary | `#4A3A28` |
| Border | `#3D322A` |
| Ink | `#F3E9DD` |
| Muted Ink | `#B8A898` |
| Heading | `#D7B8A8` |
| Border Input | `#8C7A6A` |
| Primary | `#F4B860` |

---

## 5. Typography

- **Headings:** Manrope, font-weight 600, 700, 800. Line-height 1.2.
- **Body & Controls:** Inter, font-weight 400, 500, 600. Line-height 1.5.
- **Technical & Citations:** IBM Plex Mono / monospace for DOIs, IDs, hashes, and character spans.
- **Scale:** 12px, 14px, 16px, 18px, 20px, 24px, 30px, 36px. Tabular figures enabled for numeric data.

---

## 6. Button Specifications (Fixed)

- **Primary Button:**
  - Background: `#F4B860`
  - Text: `#3E2F27`
  - Border radius: `10px`
  - No gradient. No white text.
- **Secondary Button:**
  - Background: `#FFDCA8`
  - Text: `#3E2F27`
  - Border radius: `10px`
  - No gradient.
- **Ghost / Outline Button:**
  - Background: Transparent or white
  - Border: `1px solid #A08B78`
  - Text: `#3E2F27`
  - Border radius: `10px`
- **Standard Heights:**
  - Compact: `36px`
  - Standard: `40px`
  - Mobile touch target: `44px`

---

## 7. Spacing, Elevation & Shadows

- 4px baseline grid (`4px`, `8px`, `12px`, `16px`, `24px`, `32px`, `48px`).
- Card radius: `12px` – `16px`.
- Restrained shadow: `0 1px 2px rgba(62,47,39,.06), 0 4px 12px rgba(62,47,39,.05)`.
- Respects `prefers-reduced-motion` media query.

---

## 8. Responsive Breakpoints

- `1440px+` (Desktop wide): Full 250px sidebar, 4-column metrics, side-by-side evidence comparison.
- `1024px – 1439px` (Tablet landscape): Collapsible 72px icon rail, 2-column metrics.
- `768px – 1023px` (Tablet portrait): Drawer navigation, stacked comparison panels.
- `390px – 767px` (Mobile): Full-width controls, 44px touch targets, sticky bottom progress bar.
