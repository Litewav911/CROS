# CROS - Current Development State

## Project

CROS is a retirement-planning software project being developed as a Python application.

The repository is:

C:\cloud\CROS

The project is maintained with Git.

## Current Git State

Current branch:

master

Last committed baseline at the beginning of the Codex migration:

8ff013c - Integrate tax engine with retirement withdrawals

The working tree contains uncommitted CROS development work. That work must be preserved and must not be discarded during the migration to Codex.

## Current Uncommitted Files

The following files were modified or added when the Codex migration began:

- src/tax_engine.py
- src/test_real_tax_engine.py
- src/test_social_security_tax.py
- CROSFormatForGPT.txt

## Current Tax Engine Work

The current development work is extending the tax engine to support:

- Federal MFJ progressive tax calculations.
- North Carolina tax calculations.
- Incremental federal tax.
- Incremental North Carolina tax.
- Roth conversion tax calculations.
- Tax-deferred retirement withdrawal tax calculations.
- Social Security taxable-benefit calculations for Married Filing Jointly.

## Social Security Tax Work

The tax engine currently contains:

- SOCIAL_SECURITY_MFJ_FIRST_THRESHOLD = $32,000
- SOCIAL_SECURITY_MFJ_SECOND_THRESHOLD = $44,000
- First-tier taxable rate = 50%
- Second-tier taxable rate = 85%
- Maximum taxable Social Security = 85% of benefits.

The current public function is:

calculate_social_security_taxable_benefit_mfj(
    social_security_benefits,
    other_income
)

The current Social Security tests are in:

src/test_social_security_tax.py

These tests cover:

- Benefits below the MFJ threshold.
- Partial taxation after crossing the first threshold.
- Higher provisional income.
- The 85% maximum taxable-benefit limit.
- Zero Social Security.
- Negative Social Security validation.
- Negative other-income validation.

## Withdrawal Tax Work

The current withdrawal-tax interface is:

calculate_withdrawal_tax_mfj_2026(
    base_taxable_income,
    conversion_amount=Decimal("0"),
    withdrawal_amount=None
)

The function supports backward compatibility when called with two arguments by treating the second argument as withdrawal amount.

The intended calculation is:

Tax(base taxable income + Roth conversion + withdrawal)
minus
Tax(base taxable income + Roth conversion)

for the incremental federal component, with the corresponding incremental North Carolina tax.

## Roth Conversion Tax Work

The current conversion-tax interface is:

calculate_conversion_tax_mfj_2026(
    base_taxable_income,
    conversion_amount
)

It returns a TaxResult containing:

- taxable_income
- tax

The tax combines incremental federal and North Carolina tax caused by the Roth conversion.

## Current Test Work

src/test_real_tax_engine.py has been expanded from a manually executed script into pytest tests.

The tests currently cover:

- Progressive tax.
- Flat tax.
- Standard deductions.
- Federal MFJ tax brackets.
- Incremental tax.
- Federal incremental tax.
- North Carolina incremental tax.
- Roth conversion tax.
- Zero conversion tax.
- Negative-input validation.
- A real retirement tax scenario.
- Decimal string inputs.
- Progressive conversion taxation.

## Important Working Rules

CROS development uses these rules:

1. Work one step at a time.
2. Do not guess project state.
3. Preserve uncommitted work.
4. Make only changes required for the current task.
5. Do not modify unrelated files.
6. Code changes should normally be complete known-good file replacements.
7. Run relevant tests after code changes.
8. Run the full pytest suite before declaring significant work complete.
9. Review git diff before committing.
10. Never discard existing work without explicit authorization.

The complete Codex operating rules are stored in:

AGENTS.md

## Migration to Codex

The migration is currently in progress.

Completed:

- Repository identified as C:\cloud\CROS.
- Existing Git state inspected.
- Existing uncommitted development work identified.
- AGENTS.md created and verified.

Next migration tasks:

1. Complete CURRENT_STATE.md.
2. Review the migration documentation.
3. Verify the repository contents.
4. Commit the migration documentation without discarding current development work.
5. Open C:\cloud\CROS in Codex.
6. Have Codex inspect the repository before making changes.
7. Have Codex run the existing pytest suite.
8. Confirm Codex understands the project instructions and current state.
9. Resume CROS development under Codex.

## Important

Do not treat this document as a substitute for inspecting the actual source code, tests, Git history, or current working tree.

This document describes the known state at the beginning of the Codex migration. The repository itself remains the authoritative source of truth.
