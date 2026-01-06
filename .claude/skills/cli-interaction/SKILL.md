---
name: "cli-interaction"
description: "Design and implement console menu and user interaction for Phase I Todo app. Use when creating CLI menus, prompts, and loops."
version: "1.0.0"
---

# CLI Interaction Skill

## When to Use This Skill
- User asks to "create menu for Todo app"
- User wants console prompts and input validation
- User needs loop until exit

## Procedure
1. **Read spec & backend modules**
2. **Design menu structure**:
   - Add Task
   - View Tasks
   - Update Task
   - Delete Task
   - Mark Complete/Incomplete
   - Exit
3. **Implement input prompts** for each menu option
4. **Validate user input** and handle invalid input gracefully
5. **Loop menu** until user chooses Exit

## Output Format
- Python code using `input()`
- Modular menu functions
- Clear visual indicators for task status

## Quality Criteria
- All menu options mapped to backend functions
- Input validation prevents crashes
- Menu loops until exit

## Example
**Input**: "Generate CLI menu"
**Output**:
- Displays numbered menu
- Accepts option selection
- Calls backend feature
- Handles invalid options with prompt
