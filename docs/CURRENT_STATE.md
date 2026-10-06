# CROS - Current Development State

## Project

CROS is a Python retirement-planning application maintained in Git at:

C:\cloud\CROS

The planning horizon is 2027–2040, with retirement beginning in 2027. The application is intended to use actual household financial data to model spending, income, investments, withdrawals, Roth conversions, taxes, Social Security, IRMAA, and year-by-year retirement outcomes.

## Established User Interface Decision

CROS will use a local dashboard with Overview, Transactions & Spending, Accounts, Retirement Plan, Social Security, and Taxes & Roth Conversions sections. The Overview will show annual spending, account balances, projected withdrawals, taxes, and the year-by-year plan. Users will edit assumptions in the relevant sections and view the updated projection. `src/app.py` implements the Streamlit navigation shell, Overview, Retirement Plan form, Accounts view, and Transactions & Spending workflow. The form changes monthly spending, annual return, and Roth conversion target for the projection without mutating global plan defaults. The Accounts view uses real scenario output to show opening and ending balances, annual balances, and withdrawals by account. Transactions & Spending displays month/year totals, category breakdowns, inflows, and transaction details using effective categories with manual overrides. It supports read-only CSV preview, per-row category review, explicit account metadata for new accounts, duplicate-file rejection, and manual category correction using overrides that preserve automatic categories and original source records. Social Security and Taxes & Roth Conversions remain placeholders. `src/main.py` remains the original console placeholder.

## Current Git State

- Branch: `master`
- Latest commit: `84162c2` - Add transaction spending dashboard
- Remote: `origin/master`
- `master` is synchronized with `origin/master` at `84162c2` before the current importer and category-correction work.
- Current uncommitted changes implement reviewed CSV import, explicit account metadata, and manual category correction in `src/app.py`, `src/import_csv.py`, `src/categorization.py`, and `src/transaction_service.py`, with coverage in `src/test_import_csv.py` and status documentation in `README.md` and this file.

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

The retirement engine passes Social Security benefits into federal Roth-conversion and tax-deferred-withdrawal calculations. Federal tax is calculated on ordinary taxable income plus taxable Social Security, with conversions and tax-deferred withdrawals increasing taxable income. `RetirementPlan` currently accepts annual overrides for non-Social-Security income, Social Security benefits, and tax-exempt interest. The non-Social-Security income override falls back to the $100,000 base taxable-income proxy; benefits and tax-exempt interest default to zero. These are temporary model inputs, not amounts Chris is expected to provide: taxable income should ultimately be calculated from modeled income and account withdrawals, and Social Security benefits should be estimated from answers the app collects. North Carolina conversion and withdrawal tax remains calculated using its current flat-rate model.

## Current Test Coverage

`src/test_real_tax_engine.py` contains pytest coverage for progressive and flat tax, deductions, federal brackets, incremental tax, federal and North Carolina taxes, Roth conversion tax, validation, decimal string inputs, and a retirement tax scenario.

The retirement engine tests include regression coverage for separate provisional-income inputs in conversion and withdrawal taxation. The retirement engine, report, real retirement scenario, annual withdrawal, Social Security tax, and withdrawal engine also have pytest coverage under `src/`.

The dashboard uses Streamlit 1.65.0 and pandas. Its Overview reads the tested 2027–2040 real retirement scenario through `build_retirement_report`, displaying portfolio totals, yearly spending, outside income, withdrawals, taxes, Roth conversions, account withdrawal sources, market-decline flags, and final account balances. A visible note explains that taxable income and Social Security inputs still use temporary assumptions. The Retirement Plan form accepts monthly spending, annual return, and annual Roth conversion target, then feeds those saved session values into the scenario builder. The Accounts view uses engine results and account metadata to show account owners and tax treatments, starting and projected yearly balances, and annual withdrawal allocations using applied plan assumptions. Transactions & Spending reads the local SQLite database and supports month/year summaries, category breakdowns, reviewed statement CSV import, and category correction. The import preview validates required columns and values, suggests categories from active rules, lets the user review categories, and requires selecting an active account or entering real new-account metadata before an explicit import action. Imported source rows and hashes are preserved, duplicate files are rejected, and confirmed category differences are stored as manual overrides. Category corrections on existing records are also stored as overrides, preserving original source data and automatic categories. The page warns users to validate local records and never feeds transaction inflows into retirement-income assumptions. The income proxy and Social Security defaults remain unchanged. Social Security and Taxes & Roth Conversions remain placeholders. `start_dashboard.ps1` launches the app hidden from `.venv`, waits for `/_stcore/health`, and reports the URL once the service is ready. It binds only to `127.0.0.1` and leaves browser opening to the user.

Dashboard and importer tests cover established navigation, the real retirement projection, transaction rollups, category override behavior, CSV validation and source preservation, explicit account metadata, duplicate-import rejection, and manual category updates. The full pytest suite collected 83 tests and completed with 83 passed and 0 failed using Python 3.14.8 and pytest 9.1.1. The virtual-environment launcher emits a warning that it cannot find the real location of the configured global Python executable, while pytest runs under the environment's Python 3.14.8. The PowerShell dashboard launcher also parses successfully.

## Recommended Next Development Step

Build the Social Security section around the established requirement to ask for claiming and benefit inputs, then calculate annual benefits for the projection. Do not turn annual benefit amounts into fixed yearly user inputs or incorporate imported transaction inflows as modeled retirement income.

## Deferred Data Issue

Chris confirmed tax-exempt interest is $0. Keep that assumption. Do not ask Chris to provide non-Social-Security taxable income as a yearly input; CROS must derive it from modeled income and withdrawals, accounting for each account's tax treatment. Social Security benefits also should not be requested as fixed yearly values. The app should ask for the necessary claiming and benefit inputs, then calculate the annual schedule. Until those models are implemented, the $100,000 taxable-income proxy and zero Social Security defaults remain. The repository's imported income transaction is test data and must not be used as a real assumption.

## Development Workflow

Follow `AGENTS.md`. Work one step at a time, inspect the current repository state and relevant source/tests before changes, preserve existing work, and avoid unrelated edits. Run relevant pytest tests after code changes and the full pytest suite for significant changes. Review the diff before committing.

This document is a state snapshot, not a substitute for inspecting the repository, source code, tests, Git history, or current working tree.
