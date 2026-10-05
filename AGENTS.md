# CROS - Codex Operating Instructions

## Project Mode

CROS mode is persistent while working in this repository.

Treat these instructions as mandatory project instructions, not optional preferences.

## Development Workflow

1. Work one step at a time.
2. Do not guess the current project state.
3. Inspect the repository and relevant files before making changes.
4. Make only the changes required for the current task.
5. Do not modify unrelated files.
6. Preserve existing working behavior unless the requested change explicitly requires changing it.
7. Run the relevant tests after every code change.
8. Run the full pytest suite before declaring a significant change complete.
9. Review the resulting git diff before committing.
10. Never declare a task complete when tests are failing unless the failure is explicitly understood and reported.

## Code Changes

Unless Chris explicitly requests a patch or partial modification:

- Provide complete known-good file replacements when presenting code changes.
- Do not instruct Chris to manually patch an individual function.
- Preserve the existing coding style and architecture.
- Do not rewrite unrelated portions of a file merely for stylistic reasons.
- Do not introduce speculative features or refactoring.

## PowerShell

When giving Chris a PowerShell command to execute:

- Provide only the command itself.
- Do not include the PowerShell prompt.
- Do not include explanatory text around the command.
- Do not wrap the command in a Markdown code fence.

## Testing

The project's automated tests are authoritative regression protection.

Use pytest for the test suite.

When a test fails:

1. Identify the actual failure.
2. Inspect the relevant implementation and test.
3. Determine whether the implementation or test is incorrect.
4. Make the smallest appropriate complete-file change.
5. Re-run the relevant test.
6. Re-run the full test suite before declaring success.

Never silently weaken or remove a test merely to make the suite pass.

## Git

Keep the working tree and commit history understandable.

Before making a significant change:

- Inspect git status.
- Inspect relevant existing changes.
- Do not discard uncommitted work without explicit authorization.

Before committing:

- Run the appropriate tests.
- Review git diff.
- Confirm only intended files are changed.

Never use destructive git commands to discard Chris's work unless Chris explicitly requests that action.

## Project Continuity

Established architectural decisions and project requirements must be preserved.

When beginning work in a new session:

1. Read this file.
2. Read README.md if present.
3. Read docs/CURRENT_STATE.md if present.
4. Inspect git status.
5. Inspect recent git history.
6. Inspect relevant source and tests before making changes.

Do not assume that a new conversation means the project has no prior state.

## Communication

Keep work focused on CROS.

When Chris asks for the next development step, provide the next exact action needed based on the verified repository state.

Do not repeatedly ask Chris to restate project rules that are already documented in this file or the repository.

## Current CROS Development Rules

The following rules originated from the established CROS workflow:

- CROS format is persistent.
- Work one step at a time.
- PowerShell is command-only.
- Code changes are complete-file replacements unless explicitly requested otherwise.
- Do not guess project state.
- Preserve existing project behavior.
- Test every change.
- Treat the repository and its tests as the source of truth.
