# AGENTS.md

Project-specific guidance for AI coding agents.

<!-- ASTRYX:START -->
Astryx v0.5.4 · 163 components
CLI: run every command as `npx astryx <cmd>` (shown below as `astryx ...`).

SETUP (once, in your app entry e.g. main.tsx) — without these, components render unstyled:
  import "@astryxdesign/core/reset.css";
  import "@astryxdesign/core/astryx.css";

WORKFLOW — discover, don't guess. Before writing UI:
1. `astryx build "<idea>"` — START HERE: returns a kit (closest [page] + [block]s + [component]s). No args = full playbook.
2. `astryx template <name> [--skeleton]` — scaffold the [page]/[block]s it named, or study their layout. Templates are reference code.
3. `astryx component <Name>` — props + examples for every component you use.

RULES:
- No <div> — components do all layout/spacing, page frame included.
- Frame first: read `astryx docs layout` before writing any page or screen — page frame, region widths, breakpoint behavior.
- Dense data = rows (Table, List/Item), never Card-wrapped list items; Card is for standalone widgets. Status = StatusDot/Token; Badge = counts only.
- Custom styling: component props first; else Tailwind utilities backed by tokens (bg-surface, text-primary, rounded-lg) via tailwind-theme.css. No raw hex/px.
- Tokens for every value (`astryx docs tokens`). Brand/accent belongs in the theme (`astryx theme list` / `theme add <slug>`, or `astryx theme template` for a custom one) — never override --color-* in :root.
- SELF-CHECK before you finish: re-read the file and replace any style={{…}}, raw <div>/<span> layout, imported .css/@apply, or hardcoded/arbitrary value (e.g. bg-[#fff], p-[13px]) with the component or a token-backed utility. If unsure a component/prop exists, run `astryx component <Name>` / `astryx search "<thing>"`; don't hand-roll CSS.

COMMON ASTRYX COMPONENT PROP SPECIFICATIONS (DO NOT GUESS):
- `HStack` / `VStack`:
  - `justify`: `'start' | 'center' | 'end' | 'between' | 'around' | 'evenly'` (WAJIB `'between'`, BUKAN `'space-between'`)
  - `align`: `'start' | 'center' | 'end' | 'stretch'` (BUKAN `'baseline'`)
  - `gap`: `0 | 0.5 | 1 | 1.5 | 2 | 3 | 4 | 5 | 6 | 8 | 10`
  - `padding`: `0 | 0.5 | 1 | 1.5 | 2 | 3 | 4 | 5 | 6 | 8 | 10`
  - `wrap`: `'nowrap' | 'wrap' | 'wrap-reverse'`
- `Grid`:
  - Gunakan `<Grid columns={{ minWidth: 200 }} gap={3}>` alih-alih CSS grid manual atau HStack wrap.
  - `columns`: `number | { minWidth: number, max?: number, repeat?: 'fill' | 'fit' }`
- `Text`:
  - `size`: `'4xs' | '3xs' | '2xs' | 'xsm' | 'sm' | 'base' | 'lg' | 'xl' | '2xl' | '3xl' | '4xl'` (WAJIB `'xsm'` atau `'sm'`, BUKAN `'xs'`)
  - `color`: `'primary' | 'secondary' | 'disabled' | 'placeholder' | 'accent' | 'inherit'` (BUKAN `'tertiary'` atau `'danger'`)
  - `weight`: `'normal' | 'medium' | 'semibold' | 'bold'`
- `Badge`:
  - `label`: Isi teks badge (WAJIB menggunakan prop `label`)
  - `variant`: `'neutral' | 'success' | 'warning' | 'error' | 'purple' | 'blue' | 'teal' | 'orange' | 'pink'` (BUKAN `'solid'` atau `'subtle'`)
- `StatusDot` & `Token`:
  - Untuk status indikator atau pill nilai kategori, gunakan `Token` (`color="green" | "red" | "default"`) atau `StatusDot` (`variant="success" | "error" | "warning"`), bukan `Badge`.
- `Card`:
  - Memiliki prop `padding` bawaan (misal `padding={4}`) dan `variant="default" | "muted" | "transparent"` serta `minHeight` / `width`. Jangan membungkus children dengan `<div style={{ padding: ... }}>`.

MORE CLI:
  search "<query>"   find any component / hook / doc / template / block
  component --list   163 components by category
  template --list    page + block recipes
  docs <topic>       browser-support, cli-integrations, color, elevation, getting-started, icons, illustrations, internationalization, layout, migration, motion, principles, shape, spacing, styling-libraries, styling, theme, tokens, typography, working-with-ai
  swizzle <Name>     eject component source for deep customization
  upgrade --apply    run after any @astryxdesign/core bump
<!-- ASTRYX:END -->
