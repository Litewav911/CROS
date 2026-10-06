# CROS - Current Development State

## Project

CROS is a Python retirement-planning application maintained in Git at:

C:\cloud\CROS

The planning horizon is 2027–2040, with retirement beginning in 2027. The application is intended to use actual household financial data to model spending, income, investments, withdrawals, Roth conversions, taxes, Social Security, IRMAA, and year-by-year retirement outcomes.

## Current Git State

- Branch: `master`
- Latest commit: `a4a3f17` - Wire provisional income into retirement scenarios
- Remote: `origin/master`
- `master` was synchronized with `origin/master` at `a4a3f17` before the current local changes.
- Current uncommitted changes are in `docs/CURRENT_STATE.md`, `src/real_retirement_scenario.py`, `src/retirement_plan.py`, `src/retirement_report.py`, and `src/test_real_retirement_scenario.py`.

Run `git status -sb` and `git log` before relying on this snapshot; repository state may have changed since it was written.

## Codex Migration

The migration to Codex is complete. The repository contains `AGENTS.md` with the mandatory CROS workflow and project rules. The migration documentation was committed in `469002a`.

## Implemented Tax Engine Work

The tax engine currently supports:

- Federal Married Filing Jointly progressive tax calculations using the 2026 brackets.
- North Carolina tax calculations.
- Incremental federal and North Carolina taxes.
- Roth conversion tax calculations.
- Tax-deferred retirement withdrawal tax calculations.
- Social Security taxable-benefit calculations for Married Filing Jointly.

`calculate_conversion_tax_mfj_2026(base_taxable_income, conversion_amount)` returns a `TaxResult` with `taxable_income` and `tax` fields.

`calculate_withdrawal_tax_mfj_2026(base_taxable_income, conversion_amount=Decimal("0"), withdrawal_amount=None)` returns a `Decimal`. For backward compatibility, a two-argument call treats the second argument as the withdrawal amount. Its incremental tax calculation includes the base taxable income and Roth conversion before the withdrawal.

## Social Security Tax

The Social Security calculation uses these MFJ thresholds and rates:

- First threshold: $32,000.
- Second threshold: $44,000.
- First-tier taxable rate: 50%.
- Second-tier taxable rate: 85%.
- Maximum taxable benefit: 85% of benefits.

The public function is `calculate_social_security_taxable_benefit_mfj(social_security_benefits, other_income)`. Tests are in `src/test_social_security_tax.py`.

The taxable-benefit calculation now caps the 50% tier at the interval between the thresholds and at 50% of benefits. Above the second threshold, it applies the 85% rate to the excess and caps total taxable benefits at 85% of benefits.

The Social Security tests cover below-threshold income, partial taxation, the 50% tier, the 85% tier before the benefit cap, the maximum taxable benefit, zero benefits, and negative-input validation.

The retirement engine passes Social Security benefits into federal Roth-conversion and tax-deferred-withdrawal calculations. Federal tax is calculated on ordinary taxable income plus taxable Social Security, while a separate `social_security_other_income_by_year` input supplies the non-Social-Security income component used for provisional income. Conversions and withdrawals are added to both ordinary taxable income and this provisional-income component. If the separate input is omitted, the engine preserves compatibility by using base taxable income for provisional income. `RetirementPlan` now accepts per-year Social Security benefits and tax-exempt interest. Both real-scenario builders pass those schedules to the engine; unspecified benefits and interest default to zero. The provisional-income builder adds tax-exempt interest to the existing $100,000 annual base taxable-income proxy. Actual non-Social-Security income and benefit values have not been supplied, so these defaults and the proxy remain in effect. Gross Social Security remains included in outside cash income when a benefit amount is supplied. North Carolina conversion and withdrawal tax remains calculated using its current flat-rate model.

## Current Test Coverage

`src/test_real_tax_engine.py` contains pytest coverage for progressive and flat tax, deductions, federal brackets, incremental tax, federal and North Carolina taxes, Roth conversion tax, validation, decimal string inputs, and a retirement tax scenario.

The retirement engine tests include regression coverage for separate provisional-income inputs in conversion and withdrawal taxation. The retirement engine, report, real retirement scenario, annual withdrawal, Social Security tax, and withdrawal engine also have pytest coverage under `src/`.

The latest full test run collected 68 tests and completed with 68 passed and 0 failed using Python 3.14.8 and pytest 9.1.1.

## Recommended Next Development Step

Continue retirement-planning development from the verified repository state.

## Deferred Data Issue

For now, keep using the $100,000 annual base taxable-income assumption as the real scenario's Social Security provisional-income proxy, with tax-exempt interest and Social Security benefits defaulting to zero. Revisit this when actual annual inputs are available: non-Social-Security income before deductions, tax-exempt interest, and Social Security benefits. The repository's imported income transaction is test data and must not be used as a real assumption.

## Development Workflow

Follow `AGENTS.md`. Work one step at a time, inspect the current repository state and relevant source/tests before changes, preserve existing work, and avoid unrelated edits. Run relevant pytest tests after code changes and the full pytest suite for significant changes. Review the diff before committing.

This document is a state snapshot, not a substitute for inspecting the repository, source code, tests, Git history, or current working tree.
