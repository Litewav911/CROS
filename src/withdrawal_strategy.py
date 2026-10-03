from dataclasses import dataclass
from decimal import Decimal


@dataclass
class WithdrawalSource:
    name: str
    priority: int
    enabled: bool
    rule_of_55_eligible: bool
    tax_treatment: str
    notes: str


WITHDRAWAL_SOURCES = [

    WithdrawalSource(
        name="Chris 401(k)",
        priority=1,
        enabled=True,
        rule_of_55_eligible=True,
        tax_treatment="tax_deferred",
        notes=(
            "Primary early-retirement source. "
            "Rule of 55 eligible under current plan."
        ),
    ),

    WithdrawalSource(
        name="Cash Reserve",
        priority=2,
        enabled=True,
        rule_of_55_eligible=False,
        tax_treatment="taxable",
        notes=(
            "Use primarily during market declines "
            "or when intentionally preserving investments."
        ),
    ),

    WithdrawalSource(
        name="Brokerage",
        priority=3,
        enabled=True,
        rule_of_55_eligible=False,
        tax_treatment="taxable",
        notes=(
            "Taxable investment account available "
            "for retirement spending."
        ),
    ),

    WithdrawalSource(
        name="Roth IRA",
        priority=4,
        enabled=True,
        rule_of_55_eligible=False,
        tax_treatment="tax_free",
        notes=(
            "Preserve when possible because of "
            "tax-free growth and flexibility."
        ),
    ),

    WithdrawalSource(
        name="Stephanie 401(k)",
        priority=5,
        enabled=True,
        rule_of_55_eligible=False,
        tax_treatment="tax_deferred",
        notes=(
            "Preserve while Stephanie remains employed "
            "and continue planned Roth conversions later."
        ),
    ),
]


@dataclass
class WithdrawalDecision:
    amount: Decimal
    source: str
    reason: str


def select_withdrawal_source(
    amount: Decimal,
    market_decline: bool = False,
):
    """
    Select a preliminary withdrawal source.

    This is intentionally a simple strategy layer.
    Tax calculations and detailed account optimization
    will be added later.
    """

    amount = Decimal(str(amount))

    if amount <= 0:

        return WithdrawalDecision(
            amount=Decimal("0"),
            source="None",
            reason="No portfolio withdrawal required.",
        )

    if market_decline:

        return WithdrawalDecision(
            amount=amount,
            source="Cash Reserve",
            reason=(
                "Market decline condition is active; "
                "use reserve rather than selling investments."
            ),
        )

    return WithdrawalDecision(
        amount=amount,
        source="Chris 401(k)",
        reason=(
            "Normal market conditions; "
            "Chris 401(k) is the primary early-retirement "
            "withdrawal source under the Rule of 55 strategy."
        ),
    )


def print_strategy():

    print()
    print("CROS WITHDRAWAL STRATEGY")
    print("=" * 70)

    for source in sorted(
        WITHDRAWAL_SOURCES,
        key=lambda item: item.priority,
    ):

        print(
            f"{source.priority}. "
            f"{source.name:25} "
            f"{source.tax_treatment:15}"
        )

        print(
            f"   Rule of 55: "
            f"{'Yes' if source.rule_of_55_eligible else 'No'}"
        )

        print(
            f"   {source.notes}"
        )


if __name__ == "__main__":
    print_strategy()