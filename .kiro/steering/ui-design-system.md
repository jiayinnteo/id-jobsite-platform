---
inclusion: always
---

# UI Design System — Clean, Warm & Welcoming

All Flutter UI in this project MUST follow this design system. The product should
feel friendly and calm, and be easy to navigate.

## Principles
- **Clean**: generous whitespace, one clear primary action per screen, no clutter.
- **Warm & welcoming**: warm palette and rounded, friendly type — never cold or
  harsh corporate styling.
- **Easy to navigate**: top-level areas reachable in at most two taps; consistent
  layout and components everywhere.

## Palette (Material 3, warm)
- Primary: `#E07A5F` (warm terracotta)
- Secondary: `#F2CC8F` (soft amber)
- Tertiary / success: `#81B29A` (muted sage)
- Background: `#FBF7F2` (warm off-white); Surface: `#FFFFFF` / `#FFF9F3`
- Error / destructive: `#C1554B` (warm red)
- Text: `#3D3A36` (warm charcoal)
- Build the scheme with `ColorScheme.fromSeed(seedColor: Color(0xFFE07A5F))`;
  provide both light and dark themes from the same seed.

## Typography
- Rounded, friendly sans via `google_fonts` (Nunito or Plus Jakarta Sans).
- Clear type scale; comfortable line-height; respect the OS text-scale setting.

## Shape, spacing & motion
- 16px rounded corners on cards/buttons; soft, subtle shadows.
- 8px spacing grid; airy padding.
- Gentle, short transitions; avoid jarring animations.

## Components (reuse — do not re-style ad hoc)
- `AppScaffold`, `AppButton` (primary/secondary/destructive), `AppCard`,
  `StatusChip` (color-coded defect states), `EmptyState`, `LoadingState`,
  `ConfirmDialog`.
- Centralize theme in `lib/theme/`; shared widgets in `lib/widgets/`.

## Navigation
- Per-role **bottom navigation bar** (max 5 destinations).
- A FAB for the primary create action on list screens.

## States & copy
- Always provide friendly **loading** and **empty** states — never a blank screen.
- Use human, plain-language copy. Confirm destructive actions (reject/delete/send)
  with a `ConfirmDialog`.

## Accessibility
- Minimum 48x48 tap targets; WCAG AA text contrast; full support for dynamic text
  scaling and both light/dark themes.
