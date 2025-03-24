import numpy as np
from contingency_stats.protocols import ContingencyTable


def create_contingency_typeddict(results: list) -> ContingencyTable:
    """Creates a ContingencyTable TypedDict from results list.

    Assumes results are ordered as: [11, 10, 01, 00]
    """
    return ContingencyTable(
        exposed={"with_outcome": results[0], "without_outcome": results[1]},
        unexposed={"with_outcome": results[2], "without_outcome": results[3]}
    )


def table_to_array(table: ContingencyTable) -> np.ndarray:
    """
    Convert a contingency table dict to a 2x2 numpy array.
    """
    return np.array([
        [table["exposed"]["with_outcome"], table["exposed"]["without_outcome"]],
        [table["unexposed"]["with_outcome"], table["unexposed"]["without_outcome"]]
    ])


def calculate_expected_values(observed: np.ndarray) -> np.ndarray:
    """
    Calculate expected values for a 2x2 contingency table.
    """
    row_sums = observed.sum(axis=1, keepdims=True)
    col_sums = observed.sum(axis=0, keepdims=True)
    total = observed.sum()

    return row_sums @ col_sums / total


def format_p_value(p_value: float) -> str:
    """
    Format p-value for reporting.
    """
    if p_value < 0.001:
        return "p < 0.001"
    else:
        return f"p = {p_value:.3f}"