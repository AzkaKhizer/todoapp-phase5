# Skill: Framer Motion Animations

## Purpose
Use Framer Motion to add smooth, modern animations to UI components like buttons, cards, and inputs.

## General Rules
- Animations must be subtle and professional
- Do not change layout structure
- Keep animations fast and smooth

## Button Animations
- Hover: slight lift and scale
- Tap: slight press down

Example:
whileHover={{ y: -2, scale: 1.02 }}
whileTap={{ scale: 0.97 }}

## Card Animations
- Fade in on load
- Slide up slightly

Example:
initial={{ opacity: 0, y: 10 }}
animate={{ opacity: 1, y: 0 }}

## Input Animations
- Soft glow on focus
- Small shake on error

Example (error):
animate={{ x: [0, -4, 4, -2, 2, 0] }}

## Page Animations
- Fade + slide up
- Optional stagger

## Accessibility
- Respect prefers-reduced-motion
- No heavy or flashy effects

## Do Not
- No bounce animations
- No infinite animations
- No distracting motion
