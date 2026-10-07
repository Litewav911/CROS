# CROS - Current Development State

## Project

CROS is a Python retirement-planning application maintained in Git at:

C:\cloud\CROS

The planning horizon is 2027–2040, with retirement beginning in 2027. The application is intended to use actual household financial data to model spending, income, investments, withdrawals, Roth conversions, taxes, Social Security, IRMAA, and year-by-year retirement outcomes.

## Established User Interface Decision

CROS will use a local dashboard with Overview, Transactions & Spending, Accounts, Retirement Plan, Social Security, and Taxes & Roth Conversions sections. The Overview will show annual spending, account balances, projected withdrawals, taxes, and the year-by-year plan. Users will edit assumptions in the relevant sections and view the updated projection. `src/app.py` implements the Streamlit navigation shell, Overview, Retirement Plan form, Accounts view, Transactions & Spending workflow, and Social Security inputs. Social Security inputs feed a calculated annual schedule into the Overview and Accounts projection. Taxes & Roth Conversions remains a placeholder. `src/main.py` remains the original console placeholder.

## Current Git State

- Branch: `master`
- Check `git status -sb` and `git log` for the current commit, remote, and working-tree state.

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

The retirement engine passes Social Security benefits into federal Roth-conversion and tax-deferred-withdrawal calculations. The former $100,000 taxable-income proxy is removed. The Retirement Plan form accepts annual employment salary with each person's last work date, recurring taxable interest, total ordinary dividends, their qualified-dividend subset, estimated net long-term capital gains, an annual investment-income growth assumption, and annual rental expenses and depreciation. CROS derives yearly employment cash flow, net rental cash flow, ordinary income, total income, federal and NC taxable income, baseline federal and NC income tax, and employee payroll taxes. Baseline income taxes are included in the portfolio cash need; employee payroll taxes reduce modeled take-home employment income. Qualified dividends and positive net long-term capital gains use the currently modeled 2026 MFJ federal preferential-rate thresholds; ordinary interest and nonqualified dividends use progressive ordinary brackets. North Carolina taxable income includes all modeled income under the flat-rate approximation. Qualified dividends cannot exceed total ordinary dividends and are counted within that total, not added a second time. Interest, dividends, and gains are treated as reinvested within the portfolio return rather than additional spending cash. Employment wages are prorated through the final work date. Taxable investment inputs are recurring estimates rather than fixed yearly taxable-income inputs. Tax-deferred withdrawals and Roth conversions add ordinary taxable income and are taxed incrementally; taxable, Roth, and HSA withdrawals keep their existing account-specific treatment. Transaction inflows remain excluded. Tax-exempt interest is $0 per the user's confirmed assumption. Social Security provisional income includes modeled ordinary income and long-term gains plus taxable withdrawals/conversions. Employee payroll taxes apply 2026 FICA rates throughout the 2027–2040 projection: 6.2% Social Security up to $184,500 per person, 1.45% Medicare on all wages, and 0.9% Additional Medicare Tax on joint wages above $250,000. Employer payroll taxes, self-employment income, noncovered wages, and future-year changes to rates and limits are not modeled. Rental tax losses carry forward and can offset later rental income, so they do not reduce modeled nonpassive income. This is a conservative passive-loss approximation: the active-participation special allowance, other passive income, basis and at-risk limits, real-estate-professional rules, and disposition treatment are not modeled. Rental cashflow remains a separate spending source, and suspended losses are displayed in the annual income schedule. Short-term gains and capital losses remain unsupported. Income assumptions are saved in the local SQLite `cros_settings` table and loaded into Streamlit session state for the running session; legacy settings without the new investment inputs load those fields as zero.

## Current Test Coverage

`src/test_real_tax_engine.py` contains pytest coverage for progressive and flat tax, deductions, federal brackets, incremental tax, federal and North Carolina taxes, Roth conversion tax, validation, decimal string inputs, and a retirement tax scenario.

The retirement engine tests include regression coverage for separate provisional-income inputs in conversion and withdrawal taxation. The retirement engine, report, real retirement scenario, annual withdrawal, Social Security tax, and withdrawal engine also have pytest coverage under `src/`.

The dashboard uses Streamlit 1.65.0 and pandas. Its Overview reads the 2027–2040 real retirement scenario through `build_retirement_report`, displaying portfolio totals, yearly spending, outside income net of estimated payroll tax, payroll tax, baseline income tax, withdrawals, withdrawal and conversion taxes, account withdrawal sources, market-decline flags, and final account balances. The Retirement Plan section accepts core plan settings and modeled employment, taxable investment, and rental tax inputs, saves validated income assumptions to the local SQLite settings table, loads them when needed, and previews the annual source-derived income schedule including employee payroll taxes, net employment income, taxable rental income, and suspended rental-loss carryforward balances. The Social Security section accepts per-person claiming and benefit inputs, previews the annual household schedule, and feeds those assumptions into the projection. Its Streamlit form key is separate from the session-state key that stores submitted assumptions, avoiding a widget-state collision on submit. A visible note identifies fixed 2026 payroll-tax rules and remaining income and tax limitations, including the rental special allowance and other rental limits not modeled. The Accounts view uses engine results and account metadata to show account owners and tax treatments, starting and projected yearly balances, and annual withdrawal allocations. Transactions & Spending reads the local SQLite database and supports month/year summaries, currency-formatted category charts, reviewed statement CSV import, category creation during import review, and category correction. The import preview validates required columns and values, suggests categories from active rules, lets the user add and assign categories before importing, and requires selecting an active account or entering real new-account metadata before an explicit import action. A newly added category is saved with imported transactions and becomes available in later reviews. Imported source rows and hashes are preserved, duplicate files are rejected, and confirmed category differences are stored as manual overrides. Category corrections on existing records are also stored as overrides, preserving original source data and automatic categories. The page warns users to validate local records and never feeds transaction inflows into retirement-income assumptions. Taxes & Roth Conversions remains a placeholder. `start_dashboard.ps1` launches the app hidden from `.venv`, waits for `/_stcore/health`, and reports the URL once the service is ready. It binds only to `127.0.0.1` and leaves browser opening to the user.

Dashboard, income schedule, persisted settings, Social Security, and importer tests cover modeled source schedules and salary proration, rental cash flow and taxable income including passive-loss carryforward, ordinary and preferential investment income, payroll tax rates and per-person wage bases, baseline and incremental income taxes, payroll-tax effects on net employment cash flow, legacy settings compatibility, settings defaults and persistence (including Decimal/date round-tripping and updates), provisional income, account-specific withdrawal taxes, claimant-age schedule start, COLA growth, transaction rollups, category override behavior, CSV validation and source preservation, explicit account metadata, duplicate-import rejection, manual category updates, and adding categories during import review. Required CSV header matching trims whitespace and ignores capitalization while preserving original header names in source data. The focused dashboard and CSV importer tests passed 17 tests with 0 failures. The full suite passed 107 tests with 0 failures using project `.venv` Python 3.14.8 and pytest 9.1.1. The standalone global Python cannot import Streamlit. The PowerShell dashboard launcher emits a warning that it cannot find the real location of the configured global Python executable. With no employment wages in the default scenario, the projected ending portfolio remains $327,985.32.

## Recommended Next Development Step

Next: model the active-participation rental-loss special allowance using modified AGI that includes conversions and withdrawals. The current implementation conservatively carries passive rental losses forward against later rental income and does not model the allowance. The investment extension models qualified dividends as a subset of total ordinary dividends and positive net long-term realized gains as recurring estimates, with simplified federal 2026 MFJ preferential rates. It does not model short-term gains, capital losses/carryovers, special gain categories, net investment income tax, or individual-lot realization behavior. Payroll taxes use fixed published 2026 rules throughout the projection.

## Deferred Data Issue

Chris confirmed tax-exempt interest is $0. Keep that assumption. Do not ask Chris to provide non-Social-Security taxable income as a yearly input; derive it from modeled income and withdrawals, accounting for each account's tax treatment. Do not request Social Security benefits as fixed yearly values; use claimant inputs to calculate the annual schedule. Validated employment and investment source assumptions, including qualified dividends and long-term gains, and rental adjustments are persisted in local SQLite settings. Rental loss carryforward is modeled conservatively against later rental income; the active-participation special allowance, other passive income, basis and at-risk limits, real-estate-professional rules, and disposition treatment remain unmodeled. Capital losses/carryovers, short-term gains, and further Schedule E details also remain unmodeled. The repository's imported income transaction is test data and must not be used as a real assumption.

## Development Workflow

Follow `AGENTS.md`. Work one step at a time, inspect the current repository state and relevant source/tests before changes, preserve existing work, and avoid unrelated edits. Run relevant pytest tests after code changes and the full pytest suite for significant changes. Review the diff before committing.

This document is a state snapshot, not a substitute for inspecting the repository, source code, tests, Git history, or current working tree.
