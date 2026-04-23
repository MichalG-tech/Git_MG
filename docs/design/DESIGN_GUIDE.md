# Design Guide

Visual design standards for Power BI reports in this PoC.

---

## Design Files

```
design/
├── color-palette.json              — Full color token system with usage notes
├── backgrounds/
│   ├── sales-analytics-bg.svg     — Full-page background for Sales Analytics
│   ├── finance-reporting-bg.svg   — Full-page background for Finance Reporting
│   ├── kpi-card-bg.svg            — Reusable KPI card background (240×140)
│   └── powerbi-theme.json         — Power BI theme file (apply via Options)
```

---

## Color System

The color palette is defined in [`design/color-palette.json`](../../design/color-palette.json). All hex values below reference that file.

### Brand Colors

| Token | Hex | Usage |
|-------|-----|-------|
| Navy | `#1A2B4A` | Headers, primary dark backgrounds |
| Steel | `#2D4B7C` | Secondary headers, hover states |
| Sky | `#4A90D9` | Accent, interactive highlights (Sales Analytics) |
| Teal | `#1DB5BE` | Accent — Finance Reporting model |

**Why two accent colors?** Sky blue (`#4A90D9`) identifies Sales Analytics. Teal (`#1DB5BE`) identifies Finance Reporting. This makes it immediately clear which model a report belongs to without reading the title.

### Data Visualization Series

Use in this order for multi-series charts:

| Order | Name | Hex | Typical use |
|-------|------|-----|-------------|
| 1st | Blue | `#2E86AB` | Total Sales, Actuals |
| 2nd | Teal | `#1DB5BE` | Budget, Prior Year |
| 3rd | Orange | `#F76C2F` | Returns, Variance |
| 4th | Green | `#27AE60` | Gross Profit, Positive delta |
| 5th | Purple | `#7B5EA7` | Forecast |
| 6th | Amber | `#F4A825` | Targets, Thresholds |

These colors are colorblind-safe (verified for deuteranopia and protanopia). Do not substitute ad hoc colors — use the palette.

### Semantic Colors

Use for conditional formatting and KPI status indicators:

| State | Hex | Light background |
|-------|-----|-----------------|
| Positive / Good | `#27AE60` | `#D5F0E1` |
| Negative / Alert | `#E53E3E` | `#FDE8E8` |
| Warning / At Risk | `#F4A825` | `#FEF3CD` |
| Neutral | `#718096` | `#EDF2F7` |

---

## Typography

**Font family:** Segoe UI throughout (matches Power BI Desktop default).

| Element | Size | Weight | Color |
|---------|------|--------|-------|
| Report title (header) | 18pt | Semibold | `#FFFFFF` (on navy) |
| Section title | 14pt | Semibold | `#1A2B4A` |
| KPI value (callout) | 28pt | Semibold | `#1A2B4A` |
| KPI label | 10pt | Regular, ALL CAPS | `#718096` |
| Body text | 11pt | Regular | `#1A2B4A` |
| Caption / axis label | 9–10pt | Regular | `#718096` |

---

## Page Layout

### Standard 1280×720 layout

```
┌──────────────────────────────────────────────────────────┐
│  HEADER (72px, navy)  — title, breadcrumb, version       │
│  ▬▬▬ accent line (3px, Sky or Teal)                      │
├───────────┬──────────────────────────────────────────────┤
│           │  KPI Card Row (110px, white 70% opacity)     │
│  NAV      │  ┌──────┬──────┬──────┬──────┐             │
│  PANEL    │  │ KPI  │ KPI  │ KPI  │ KPI  │             │
│  (220px)  │  └──────┴──────┴──────┴──────┘             │
│           │                                               │
│  Nav      │  ┌──────────────────┐  ┌───────────┐       │
│  items    │  │  Primary Chart   │  │  Sidebar  │       │
│           │  │  (680px wide)    │  │  (332px)  │       │
│  Filters  │  │                  │  │           │       │
│           │  └──────────────────┘  └───────────┘       │
├───────────┴──────────────────────────────────────────────┤
│  FOOTER (20px)  — data refresh note, version             │
└──────────────────────────────────────────────────────────┘
```

### Applying the background

1. Open the SVG file in a browser to verify it renders correctly
2. In Power BI Desktop: **Format pane → Page → Page background → Browse**
3. Select the SVG file (Power BI accepts SVG directly)
4. Set transparency to **0%** so the background shows fully
5. Set **Image fit** to **Fit** (not Tile or Fill)

### Content placement grid

With the 220px nav panel and 72px header, the content canvas starts at:
- Left edge: x=236 (220px nav + 16px padding)
- Top edge: y=88 (72px header + 16px padding)
- Width available: 1028px
- Height available: 596px (to y=684, leaving 20px footer + 16px padding)

Use these coordinates as snap guides when placing visuals.

---

## Applying the Power BI Theme

The theme file (`design/backgrounds/powerbi-theme.json`) sets colors, fonts, and default visual styles consistently across all reports.

**Apply in Power BI Desktop:**
1. **View → Themes → Browse for themes**
2. Select `design/backgrounds/powerbi-theme.json`
3. Click **Apply** — the theme applies to all visuals immediately

The theme sets:
- Data series colors (the 6-color visualization palette)
- Default font family (Segoe UI) and size (11pt)
- Table header background (navy) and font (white)
- Matrix header background (steel blue)
- Card and slicer background (white)

---

## KPI Card Standards

Every KPI card should follow this pattern:

```
┌─ 4px accent line (Sky for Sales, Teal for Finance) ──────┐
│                                              ○ Icon       │
│  METRIC LABEL (10pt, ALL CAPS, muted gray)               │
│                                                           │
│  $12.4M                                                   │
│  (28pt, Semibold, navy)                                   │
│                                                           │
│  ▲ 8.3% vs prior year    |    FY2024 YTD                 │
│  (semantic color)              (10pt, muted)              │
│  ─────────────────────────────────────────────           │
│  [spark line]                                             │
└───────────────────────────────────────────────────────────┘
```

Conditional formatting rules for the trend indicator:
- Growth > 0: Green (`#27AE60`) with up arrow ▲
- Growth < 0: Red (`#E53E3E`) with down arrow ▼
- Growth = 0: Neutral gray (`#718096`) with dash —

---

## DAX Conditional Formatting

Use these DAX measures as conditional formatting color rules:

```dax
// KPI color based on YoY growth
KPI Color =
VAR Growth = [YoY Sales Growth %]
RETURN
SWITCH(
    TRUE(),
    Growth > 0.05,  "#27AE60",   -- Good (>5% growth)
    Growth >= 0,    "#F4A825",   -- Neutral (0-5% growth)
    "#E53E3E"                    -- Negative
)
```

```dax
// Target attainment color
Target Color =
VAR Pct = [Target Attainment %]
RETURN
SWITCH(
    TRUE(),
    Pct >= 1.0, "#27AE60",    -- On or above target
    Pct >= 0.9, "#F4A825",    -- Within 10% of target
    "#E53E3E"                  -- Below 90% of target
)
```

---

## What's Not in This PoC

**Figma mockups** — the `design/figma/` folder is a placeholder. For full Figma integration in a client engagement:
1. Design report layouts in Figma using the color tokens above
2. Export page backgrounds as PNG (1280×720, 144 DPI)
3. Export individual card backgrounds as PNG
4. Import into Power BI Desktop as page/visual backgrounds

The color palette and layout standards in this guide provide everything a Figma designer needs to create assets that are compatible with the Power BI theme.
