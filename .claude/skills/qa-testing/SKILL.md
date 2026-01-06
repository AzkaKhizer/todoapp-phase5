---
name: "qa-testing"
description: "Generate test cases and verify Phase I Todo app features. Use when validating Add, View, Update, Delete, and Mark Complete functionality."
version: "1.0.0"
---

# QA & Testing Skill

## When to Use This Skill
- User asks to "test Todo app features"
- User wants verification of console behavior
- User needs acceptance criteria validation

## Procedure
1. **Read spec and backend modules**
2. **Define test cases** for each feature
   - Inputs, expected outputs, success/failure
3. **Verify deterministic behavior**
4. **Check edge cases** (empty title, invalid ID)
5. **Produce test report** in Markdown

## Output Format
- Markdown table with:
  - Feature
  - Input
  - Expected Output
  - Actual Output
  - Pass/Fail

## Quality Criteria
- Covers all features
- Detects failures or misbehaviors
- Clear, structured, reusable tests

## Example
**Input**: "Test Add Task feature"
**Output**:
| Feature  | Input              | Expected Output                         | Actual Output | Pass/Fail |
|----------|------------------|----------------------------------------|---------------|-----------|
| Add Task | title="Buy milk"  | Task created with unique ID, status=incomplete | same          | Pass      |
