# Skill: UI Responsiveness

## Purpose
Ensure all UI components adapt cleanly to different screen sizes without breaking layout or design.

## Core Principle
Desktop layout must remain unchanged.
Only adjust styles for smaller screens.

## Breakpoints
- Mobile: max-width 640px
- Tablet: 641px – 1024px
- Desktop: 1025px+

## Mobile Rules
- Stack elements vertically
- Increase tap area (minimum 44px)
- Reduce padding and gaps
- Avoid horizontal scrolling

## Tablet Rules
- Use 2-column layouts where possible
- Maintain comfortable spacing
- Do not shrink text too much

## Desktop Rules
- Keep original layout
- Do not center elements unless designed
- Maintain full spacing and animations

## Text & Typography
- Use responsive font sizes
- Headings scale down on mobile
- Line-height must remain readable

## Images & Media
- Use max-width: 100%
- Prevent overflow
- Maintain aspect ratio

## Navigation
- Desktop: horizontal menu
- Mobile: hamburger menu
- Close menu on item click

## Forms & Buttons
- Full-width buttons on mobile
- Inputs must be easy to tap
- Keep labels visible

## Animations
- Reduce motion on mobile
- Respect prefers-reduced-motion

## Accessibility
- Keyboard navigable on all devices
- No hidden interactive elements
- Clear focus states

## Do Not
- Do not change layout structure
- Do not hide important content
- Do not add unnecessary breakpoints
