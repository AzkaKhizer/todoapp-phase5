# Skill: Master UI System

## Purpose
Provide a complete, modern, responsive, and accessible UI system for web apps.  
Covers buttons, cards, inputs, navbar, responsiveness, animations, and glassmorphism.

---

## Principles
- Minimal and modern
- Glassmorphism where appropriate
- Accessible and keyboard-friendly
- Mobile-first, responsive design
- Subtle animations
- Reusable components
- Do not break existing layout

---

## Buttons (Glassmorphism)
- Semi-transparent background, backdrop blur
- Rounded corners, soft shadow
- Hover: lift + glow
- Tap: scale down
- Variants: primary, secondary, outline, icon, disabled
- Accessible: minimum 44px touch, aria-label if icon-only

---

## Cards
- Rounded edges, soft elevation
- Optional glass effect
- Hover: lift, subtle shadow or glow
- Responsive layout: grid/flex
- Types: content, feature, profile, stats
- Reusable component

---

## Inputs / Forms
- Clean, soft borders
- Glass effect optional
- Height: 44–48px
- Focus: border glow
- Error: soft shake animation
- Accessible: proper labels, aria-invalid

---

## Navbar
- Logo left, links center/right
- Optional CTA button
- Desktop: horizontal menu, hover underline
- Mobile: hamburger, slide-down menu
- Optional glass background
- Sticky top optional
- Smooth open/close animation
- Keyboard navigable, aria-label for menu button

---

## Responsiveness
- Desktop: keep original layout
- Tablet: adjust spacing, 2-column layouts
- Mobile: stack elements vertically, full-width buttons, avoid horizontal scroll
- Responsive typography and images
- Respect reduced-motion preference
- Accessible: focus-visible, no hidden interactive elements

---

## Animations (Framer Motion)
- Subtle, fast, smooth
- Button hover: lift + scale
- Button tap: scale down
- Card entry: fade + slide up
- Input error: small shake
- Page/section: fade + slide + optional stagger
- Reduced motion respected
- Do not use bounce or infinite animations

---

## Typography
- Responsive font sizes
- Maintain readability
- Headings scale down on mobile
- Line height consistent

---

## Colors & Visuals
- Use modern palette
- Ensure high contrast for accessibility
- Glassmorphism: rgba + backdrop blur
- Shadows: soft and minimal

---

## Accessibility
- Keyboard navigable
- Focus-visible indicators
- Proper ARIA roles
- Avoid motion that can trigger discomfort

---

## Output Expectations
- Reusable and composable components
- Mobile-first but desktop layout untouched
- Match project’s existing design stack
- Minimal animations, subtle effects
- Do not break current layout
- Maintain clean, modern look

---

