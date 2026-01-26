# mortgage_calculator/services.py
from decimal import Decimal, getcontext

getcontext().prec = 28

def monthly_payment(principal: Decimal, annual_rate_pct: Decimal, years: int) -> Decimal:
    if years <= 0:
        raise ValueError("years must be > 0")
    if principal <= 0:
        raise ValueError("principal must be > 0")

    n = Decimal(years) * Decimal(12)
    r = (annual_rate_pct / Decimal(100)) / Decimal(12)

    if r == 0:
        return principal / n

    denom = Decimal(1) - (Decimal(1) + r) ** (-n)
    return (principal * r) / denom
