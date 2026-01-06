# UI Components Specification

**Parent Spec**: @specs/002-todo-fullstack-web/spec.md
**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05

---

## Overview

This document specifies the React components for the Todo Full-Stack Web Application frontend. Components are built with Next.js, TypeScript, and Tailwind CSS.

---

## Component Architecture

```
components/
├── ui/                    # Reusable UI primitives
│   ├── Button.tsx
│   ├── Input.tsx
│   ├── Checkbox.tsx
│   ├── Modal.tsx
│   ├── Alert.tsx
│   └── LoadingSpinner.tsx
├── forms/                 # Form components
│   ├── LoginForm.tsx
│   ├── RegisterForm.tsx
│   └── TaskForm.tsx
├── tasks/                 # Task-specific components
│   ├── TaskList.tsx
│   ├── TaskCard.tsx
│   ├── TaskEditModal.tsx
│   └── EmptyState.tsx
└── layout/                # Layout components
    ├── Header.tsx
    ├── Navbar.tsx
    └── Container.tsx
```

---

## UI Primitives

### Button

**Purpose**: Primary interactive element for actions.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| variant | 'primary' \| 'secondary' \| 'danger' \| 'ghost' | No | 'primary' | Visual style |
| size | 'sm' \| 'md' \| 'lg' | No | 'md' | Button size |
| disabled | boolean | No | false | Disabled state |
| loading | boolean | No | false | Shows spinner, disables button |
| onClick | () => void | No | - | Click handler |
| type | 'button' \| 'submit' \| 'reset' | No | 'button' | HTML button type |
| children | ReactNode | Yes | - | Button content |

**Visual States**:
- Default: Solid background
- Hover: Slightly darker background
- Active: Pressed appearance
- Disabled: Reduced opacity, cursor not-allowed
- Loading: Spinner icon, disabled

**Variants**:
- Primary: Blue background, white text
- Secondary: Gray background, dark text
- Danger: Red background, white text
- Ghost: Transparent background, text color

---

### Input

**Purpose**: Text input field for forms.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| type | 'text' \| 'email' \| 'password' | No | 'text' | Input type |
| label | string | No | - | Label text |
| placeholder | string | No | - | Placeholder text |
| value | string | Yes | - | Controlled value |
| onChange | (value: string) => void | Yes | - | Change handler |
| error | string | No | - | Error message |
| disabled | boolean | No | false | Disabled state |
| required | boolean | No | false | Required indicator |

**Visual States**:
- Default: Gray border
- Focus: Blue border, ring
- Error: Red border, error message below
- Disabled: Gray background, reduced opacity

---

### Checkbox

**Purpose**: Boolean toggle for task completion.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| checked | boolean | Yes | - | Checked state |
| onChange | (checked: boolean) => void | Yes | - | Change handler |
| disabled | boolean | No | false | Disabled state |
| label | string | No | - | Optional label |

**Visual States**:
- Unchecked: Empty box
- Checked: Box with checkmark
- Disabled: Reduced opacity

---

### Modal

**Purpose**: Dialog overlay for confirmations and editing.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| open | boolean | Yes | - | Visibility state |
| onClose | () => void | Yes | - | Close handler |
| title | string | No | - | Modal title |
| children | ReactNode | Yes | - | Modal content |
| size | 'sm' \| 'md' \| 'lg' | No | 'md' | Modal width |

**Behavior**:
- Click outside closes modal
- Escape key closes modal
- Scroll lock on body when open
- Focus trap inside modal

---

### Alert

**Purpose**: Display success, error, or info messages.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| type | 'success' \| 'error' \| 'warning' \| 'info' | Yes | - | Alert type |
| message | string | Yes | - | Alert message |
| onClose | () => void | No | - | Close handler |
| dismissible | boolean | No | true | Show close button |

**Colors**:
- Success: Green
- Error: Red
- Warning: Yellow
- Info: Blue

---

### LoadingSpinner

**Purpose**: Visual loading indicator.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| size | 'sm' \| 'md' \| 'lg' | No | 'md' | Spinner size |
| className | string | No | - | Additional classes |

---

## Form Components

### LoginForm

**Purpose**: User authentication form.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| onSubmit | (data: LoginData) => Promise<void> | Yes | - | Submit handler |
| error | string | No | - | Form-level error |
| loading | boolean | No | false | Loading state |

**Fields**:
| Field | Type | Validation |
|-------|------|------------|
| email | email | Required, valid email format |
| password | password | Required |

**Behavior**:
- Validates on submit
- Shows field-level errors
- Shows form-level error (from API)
- Submit button disabled when loading
- Link to registration page

---

### RegisterForm

**Purpose**: New user registration form.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| onSubmit | (data: RegisterData) => Promise<void> | Yes | - | Submit handler |
| error | string | No | - | Form-level error |
| loading | boolean | No | false | Loading state |

**Fields**:
| Field | Type | Validation |
|-------|------|------------|
| email | email | Required, valid email format |
| password | password | Required, min 8 characters |
| confirmPassword | password | Required, must match password |

**Behavior**:
- Real-time validation on blur
- Password match validation
- Shows all validation errors
- Link to login page

---

### TaskForm

**Purpose**: Create or edit a task.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| mode | 'create' \| 'edit' | No | 'create' | Form mode |
| initialData | TaskFormData | No | - | Edit mode initial values |
| onSubmit | (data: TaskFormData) => Promise<void> | Yes | - | Submit handler |
| onCancel | () => void | No | - | Cancel handler (edit mode) |
| loading | boolean | No | false | Loading state |

**Fields**:
| Field | Type | Validation | Max Length |
|-------|------|------------|------------|
| title | text | Required, non-empty | 200 |
| description | textarea | Optional | 2000 |

**Behavior**:
- Create mode: Inline form, clears on submit
- Edit mode: In modal, cancel reverts changes
- Character count display for description
- Submit disabled while loading

---

## Task Components

### TaskList

**Purpose**: Container for rendering list of tasks.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| tasks | Task[] | Yes | - | Array of tasks |
| onToggle | (id: string) => void | Yes | - | Toggle handler |
| onEdit | (task: Task) => void | Yes | - | Edit handler |
| onDelete | (id: string) => void | Yes | - | Delete handler |
| loading | boolean | No | false | Loading state |

**Behavior**:
- Shows EmptyState if no tasks
- Shows LoadingSpinner if loading
- Renders TaskCard for each task
- Handles optimistic updates

---

### TaskCard

**Purpose**: Display a single task with actions.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| task | Task | Yes | - | Task data |
| onToggle | () => void | Yes | - | Toggle handler |
| onEdit | () => void | Yes | - | Edit handler |
| onDelete | () => void | Yes | - | Delete handler |

**Layout**:
```
┌──────────────────────────────────────────────┐
│ [✓] Task Title                    [Edit] [×] │
│     Task description here...                 │
│     Created: Jan 5, 2026                     │
└──────────────────────────────────────────────┘
```

**Visual States**:
- Incomplete: Normal text
- Complete: Checkmark, optional strikethrough
- Hover: Show action buttons
- Optimistic update: Slightly faded during API call

---

### TaskEditModal

**Purpose**: Modal containing TaskForm for editing.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| task | Task | Yes | - | Task to edit |
| open | boolean | Yes | - | Modal open state |
| onClose | () => void | Yes | - | Close handler |
| onSave | (data: TaskFormData) => Promise<void> | Yes | - | Save handler |

**Behavior**:
- Populates form with task data
- Validates before save
- Shows loading during save
- Closes on successful save

---

### EmptyState

**Purpose**: Display when user has no tasks.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| onCreateClick | () => void | No | - | Create button handler |

**Content**:
- Illustration or icon
- Message: "No tasks yet"
- Subtext: "Create your first task to get started!"
- Optional "Add Task" button

---

## Layout Components

### Header

**Purpose**: Top navigation bar.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| user | User \| null | No | - | Current user |
| onLogout | () => void | No | - | Logout handler |

**Content** (authenticated):
- Logo/App name (left)
- User email (right)
- Logout button (right)

**Content** (unauthenticated):
- Logo/App name (left)
- Login/Register links (right)

---

### Navbar

**Purpose**: Navigation for unauthenticated pages.

**Props**: None

**Content**:
- Logo/App name
- Login link
- Register link

---

### Container

**Purpose**: Centered content wrapper with max width.

**Props**:
| Prop | Type | Required | Default | Description |
|------|------|----------|---------|-------------|
| children | ReactNode | Yes | - | Content |
| size | 'sm' \| 'md' \| 'lg' | No | 'md' | Max width |

**Sizes**:
- sm: max-w-md (448px)
- md: max-w-2xl (672px)
- lg: max-w-4xl (896px)

---

## Responsive Design

### Breakpoints

| Breakpoint | Min Width | Usage |
|------------|-----------|-------|
| sm | 640px | Small tablets |
| md | 768px | Tablets |
| lg | 1024px | Laptops |
| xl | 1280px | Desktops |

### Mobile Considerations

- Task actions shown inline (not on hover)
- Full-width forms
- Stack navigation vertically
- Touch-friendly tap targets (44px minimum)
- Modal is full-screen on mobile

---

## Accessibility Requirements

### Keyboard Navigation

- All interactive elements focusable
- Tab order follows visual order
- Enter/Space activates buttons
- Escape closes modals
- Arrow keys navigate checkboxes

### Screen Readers

- All images have alt text
- Form inputs have labels
- Errors announced via aria-live
- Modal has aria-modal and role="dialog"
- Loading states announced

### Color Contrast

- Minimum 4.5:1 for normal text
- Minimum 3:1 for large text
- Don't rely on color alone for status

---

## Related Documents

- @specs/002-todo-fullstack-web/ui/pages.md - Page layouts using these components
- @specs/002-todo-fullstack-web/features/task-crud.md - Task behavior requirements
- @specs/002-todo-fullstack-web/features/authentication.md - Auth form requirements
