# CROS Retirement Planning Application

Personal retirement spending and planning application.

## Purpose

The application will:

- Import checking account transactions
- Import credit card transactions
- Analyze actual household spending
- Track retirement income
- Track investment accounts
- Calculate retirement withdrawals
- Model Roth conversions
- Estimate federal taxes
- Estimate North Carolina taxes
- Track IRMAA considerations
- Model Social Security
- Track account balances
- Apply retirement spending guardrails
- Produce year-by-year retirement reports

## Planning Horizon

2027–2040

## Primary Retirement Plan

Retirement begins in 2027.

The application will use actual financial data wherever available rather than relying on generic spending assumptions.

## User Interface Direction

CROS will use a local dashboard interface. Its main sections will be:

- Overview
- Transactions & Spending
- Accounts
- Retirement Plan
- Social Security
- Taxes & Roth Conversions

The Overview will show annual spending, account balances, projected withdrawals, taxes, and the year-by-year retirement plan. Users will edit assumptions in the relevant sections and view the updated projection. `src/app.py` now provides the local Streamlit dashboard, a working Overview, and Retirement Plan controls for monthly spending, annual return, and Roth conversion target. Transactions & Spending, Accounts, Social Security, and Taxes & Roth Conversions remain to be built.

## Start the Local Dashboard

.\start_dashboard.ps1

The launcher starts Streamlit in the project virtual environment, waits for its health endpoint, and then reports the dashboard URL. It does not open a browser; open the URL after the launcher reports that the dashboard is ready.
