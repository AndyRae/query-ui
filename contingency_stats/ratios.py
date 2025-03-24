from typing import Optional

from protocols import ContingencyTable


def calculate_risk_ratio(table: ContingencyTable) -> Optional[float]:
    """
    Calculate the risk ratio (relative risk) from a contingency table.

    Args:
        table: ContingencyTable with exposed and unexposed groups

    Returns:
        Risk ratio or None if calculation is not possible due to division by zero
    """
    exposed_with_outcome = table["exposed"]["with_outcome"]
    exposed_without_outcome = table["exposed"]["without_outcome"]
    unexposed_with_outcome = table["unexposed"]["with_outcome"]
    unexposed_without_outcome = table["unexposed"]["without_outcome"]

    exposed_total = exposed_with_outcome + exposed_without_outcome
    unexposed_total = unexposed_with_outcome + unexposed_without_outcome

    # Check for division by zero
    if exposed_total == 0 or unexposed_total == 0 or unexposed_with_outcome == 0:
        return None

    risk_exposed = exposed_with_outcome / exposed_total
    risk_unexposed = unexposed_with_outcome / unexposed_total

    return float(risk_exposed / risk_unexposed)


def calculate_odds_ratio(table: ContingencyTable) -> Optional[float]:
    """
    Calculate the odds ratio from a contingency table.

    Args:
        table: ContingencyTable with exposed and unexposed groups

    Returns:
        Odds ratio or None if calculation is not possible due to division by zero
    """
    a = table["exposed"]["with_outcome"]
    b = table["exposed"]["without_outcome"]
    c = table["unexposed"]["with_outcome"]
    d = table["unexposed"]["without_outcome"]

    # Check for division by zero
    if b * c == 0:
        return None

    return float((a * d) / (b * c))


def calculate_risk_difference(table: ContingencyTable) -> Optional[float]:
    """
    Calculate the risk difference from a contingency table.

    Args:
        table: ContingencyTable with exposed and unexposed groups

    Returns:
        Risk difference or None if calculation is not possible due to division by zero
    """
    exposed_with_outcome = table["exposed"]["with_outcome"]
    exposed_without_outcome = table["exposed"]["without_outcome"]
    unexposed_with_outcome = table["unexposed"]["with_outcome"]
    unexposed_without_outcome = table["unexposed"]["without_outcome"]

    exposed_total = exposed_with_outcome + exposed_without_outcome
    unexposed_total = unexposed_with_outcome + unexposed_without_outcome

    # Check for division by zero
    if exposed_total == 0 or unexposed_total == 0:
        return None

    risk_exposed = exposed_with_outcome / exposed_total
    risk_unexposed = unexposed_with_outcome / unexposed_total

    return float(risk_exposed - risk_unexposed)