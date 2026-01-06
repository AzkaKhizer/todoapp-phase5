# UI Pages Specification

**Parent Spec**: @specs/002-todo-fullstack-web/spec.md
**Feature Branch**: `002-todo-fullstack-web`
**Created**: 2026-01-05

---

## Overview

This document specifies the page layouts and navigation flow for the Todo Full-Stack Web Application frontend using Next.js App Router.

---

## Route Structure

```
app/
├── (auth)/                    # Auth layout group
│   ├── login/
│   │   └── page.tsx          # /login
│   └── register/
│       └── page.tsx          # /register
├── (dashboard)/               # Protected layout group
│   └── dashboard/
│       └── page.tsx          # /dashboard
├── layout.tsx                 # Root layout
├── page.tsx                   # / (landing)
└── not-found.tsx             # 404 page
```

---

## Navigation Flow

```
                    ┌─────────────┐
                    │   Landing   │
                    │     (/)     │
                    └──────┬──────┘
                           │
           ┌───────────────┼───────────────┐
           │               │               │
           ▼               ▼               ▼
    ┌─────────────┐ ┌─────────────┐ ┌─────────────┐
    │   Login     │ │  Register   │ │  Dashboard  │
    │  (/login)   │ │ (/register) │ │ (/dashboard)│
    └──────┬──────┘ └──────┬──────┘ └─────────────┘
           │               │               ▲
           │               │               │
           └───────────────┴───────────────┘
                    (after auth success)
```

---

## Page: Landing (/)

**Purpose**: Marketing/welcome page for visitors.

**Access**: Public

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App                        [Login] [Register] │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                    Welcome to Todo App                     │
│                                                            │
│         Organize your tasks, boost your productivity       │
│                                                            │
│                   [Get Started - Free]                     │
│                                                            │
├────────────────────────────────────────────────────────────┤
│  Feature 1       Feature 2        Feature 3               │
│  [icon]          [icon]           [icon]                   │
│  Simple          Secure           Everywhere               │
│  Easy to use     Your data is     Access from              │
│  interface       protected        any device               │
└────────────────────────────────────────────────────────────┘
```

**Behavior**:
- If user is authenticated, redirect to /dashboard
- "Get Started" button links to /register
- Login/Register links in header

**Components Used**:
- Navbar
- Container
- Button

---

## Page: Login (/login)

**Purpose**: User authentication form.

**Access**: Public (redirects to dashboard if already authenticated)

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                      ┌──────────────────┐                  │
│                      │                  │                  │
│                      │   Welcome Back   │                  │
│                      │                  │                  │
│                      │   [Error Alert]  │                  │
│                      │                  │                  │
│                      │   Email          │                  │
│                      │   [___________]  │                  │
│                      │                  │                  │
│                      │   Password       │                  │
│                      │   [___________]  │                  │
│                      │                  │                  │
│                      │   [  Log In  ]   │                  │
│                      │                  │                  │
│                      │   Don't have an  │                  │
│                      │   account?       │                  │
│                      │   Register here  │                  │
│                      │                  │                  │
│                      └──────────────────┘                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Behavior**:
- Validate email format on blur
- Show loading spinner on submit
- Display API errors (e.g., "Invalid email or password")
- Redirect to /dashboard on success
- Link to /register for new users

**Components Used**:
- Container (size: sm)
- LoginForm
- Alert (for errors)
- Button

**States**:
- Default: Empty form
- Loading: Button shows spinner, inputs disabled
- Error: Alert shown above form

---

## Page: Register (/register)

**Purpose**: New user registration form.

**Access**: Public (redirects to dashboard if already authenticated)

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                      ┌──────────────────┐                  │
│                      │                  │                  │
│                      │   Create Account │                  │
│                      │                  │                  │
│                      │   [Error Alert]  │                  │
│                      │                  │                  │
│                      │   Email          │                  │
│                      │   [___________]  │                  │
│                      │                  │                  │
│                      │   Password       │                  │
│                      │   [___________]  │                  │
│                      │   Min 8 chars    │                  │
│                      │                  │                  │
│                      │   Confirm Pass   │                  │
│                      │   [___________]  │                  │
│                      │                  │                  │
│                      │   [  Sign Up  ]  │                  │
│                      │                  │                  │
│                      │   Already have   │                  │
│                      │   an account?    │                  │
│                      │   Log in here    │                  │
│                      │                  │                  │
│                      └──────────────────┘                  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Behavior**:
- Real-time validation on blur
- Password strength indicator (optional)
- Confirm password must match
- Show loading on submit
- Display API errors
- Redirect to /dashboard on success
- Link to /login for existing users

**Components Used**:
- Container (size: sm)
- RegisterForm
- Alert (for errors)
- Button

---

## Page: Dashboard (/dashboard)

**Purpose**: Main task management interface.

**Access**: Protected (redirects to /login if not authenticated)

**Layout**:
```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App            user@example.com  [Logout]     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │   My Tasks                          [+ Add Task]     │  │
│  │                                                      │  │
│  │   ┌────────────────────────────────────────────────┐ │  │
│  │   │  New Task                                      │ │  │
│  │   │  [Title________________] [Description_____]    │ │  │
│  │   │                                    [Add]       │ │  │
│  │   └────────────────────────────────────────────────┘ │  │
│  │                                                      │  │
│  │   ┌────────────────────────────────────────────────┐ │  │
│  │   │ [ ] Buy groceries              [Edit] [Delete] │ │  │
│  │   │     Get milk and bread                         │ │  │
│  │   └────────────────────────────────────────────────┘ │  │
│  │                                                      │  │
│  │   ┌────────────────────────────────────────────────┐ │  │
│  │   │ [✓] Call mom                   [Edit] [Delete] │ │  │
│  │   │     Wish happy birthday                        │ │  │
│  │   └────────────────────────────────────────────────┘ │  │
│  │                                                      │  │
│  │   ┌────────────────────────────────────────────────┐ │  │
│  │   │ [ ] Finish report              [Edit] [Delete] │ │  │
│  │   │                                                │ │  │
│  │   └────────────────────────────────────────────────┘ │  │
│  │                                                      │  │
│  │   Showing 3 tasks (1 complete)                      │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Layout (Empty State)**:
```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App            user@example.com  [Logout]     │
├────────────────────────────────────────────────────────────┤
│                                                            │
│  ┌──────────────────────────────────────────────────────┐  │
│  │                                                      │  │
│  │   My Tasks                                           │  │
│  │                                                      │  │
│  │                      [icon]                          │  │
│  │                                                      │  │
│  │                No tasks yet                          │  │
│  │          Create your first task to get started!     │  │
│  │                                                      │  │
│  │                   [+ Add Task]                       │  │
│  │                                                      │  │
│  └──────────────────────────────────────────────────────┘  │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

**Behavior**:
- Fetch tasks on page load
- Show loading spinner while fetching
- Show empty state if no tasks
- Inline task creation form
- Task actions: toggle, edit, delete
- Edit opens modal
- Delete shows confirmation
- Logout clears session and redirects

**Components Used**:
- Header
- Container (size: lg)
- TaskForm (create mode)
- TaskList
- TaskCard
- TaskEditModal
- EmptyState
- LoadingSpinner
- Alert

**States**:
- Loading: Spinner in main area
- Empty: EmptyState component
- Populated: TaskList with TaskCards
- Editing: TaskEditModal open
- Deleting: Confirmation modal

---

## Mobile Layouts

### Dashboard Mobile (< 768px)

```
┌──────────────────────────┐
│ [≡] Todo     [Logout]    │
├──────────────────────────┤
│                          │
│  My Tasks                │
│                          │
│  ┌────────────────────┐  │
│  │ Title              │  │
│  │ [______________]   │  │
│  │                    │  │
│  │ Description        │  │
│  │ [______________]   │  │
│  │                    │  │
│  │ [  Add Task  ]     │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │ [ ] Buy groceries  │  │
│  │     Get milk...    │  │
│  │ [Edit] [Delete]    │  │
│  └────────────────────┘  │
│                          │
│  ┌────────────────────┐  │
│  │ [✓] Call mom       │  │
│  │     Wish happy...  │  │
│  │ [Edit] [Delete]    │  │
│  └────────────────────┘  │
│                          │
└──────────────────────────┘
```

**Mobile Adaptations**:
- Form fields stacked vertically
- Action buttons always visible
- Touch-friendly tap targets
- Modal becomes full-screen sheet
- Simplified header

---

## Error Pages

### 404 Not Found

```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                         404                                │
│                                                            │
│                   Page Not Found                           │
│                                                            │
│        The page you're looking for doesn't exist.          │
│                                                            │
│                    [Go to Home]                            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Error Boundary

```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                   Something went wrong                     │
│                                                            │
│        We're sorry, an unexpected error occurred.          │
│                                                            │
│                   [Try Again] [Go Home]                    │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

---

## Loading States

### Full Page Loading

```
┌────────────────────────────────────────────────────────────┐
│  [Logo] Todo App                                           │
├────────────────────────────────────────────────────────────┤
│                                                            │
│                                                            │
│                                                            │
│                         [Spinner]                          │
│                         Loading...                         │
│                                                            │
│                                                            │
│                                                            │
└────────────────────────────────────────────────────────────┘
```

### Inline Loading (Tasks)

```
┌──────────────────────────────────────────────────────────┐
│                                                          │
│   My Tasks                                               │
│                                                          │
│                       [Spinner]                          │
│                    Loading tasks...                      │
│                                                          │
└──────────────────────────────────────────────────────────┘
```

---

## Page Metadata

| Route | Title | Description |
|-------|-------|-------------|
| / | Todo App - Organize Your Tasks | Simple and secure task management |
| /login | Login - Todo App | Log in to your account |
| /register | Register - Todo App | Create a new account |
| /dashboard | Dashboard - Todo App | Manage your tasks |
| 404 | Page Not Found - Todo App | - |

---

## Authentication Guards

### Protected Route Guard

```
Check for auth token
├── Token exists
│   └── Verify token (GET /api/auth/me)
│       ├── Valid → Show page
│       └── Invalid → Redirect to /login
└── No token
    └── Redirect to /login
```

### Guest Route Guard (Login/Register)

```
Check for auth token
├── Token exists
│   └── Redirect to /dashboard
└── No token
    └── Show page
```

---

## Related Documents

- @specs/002-todo-fullstack-web/ui/components.md - Component specifications
- @specs/002-todo-fullstack-web/features/authentication.md - Auth flows
- @specs/002-todo-fullstack-web/features/task-crud.md - Task operations
