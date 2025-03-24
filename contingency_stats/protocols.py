from typing import Protocol, Dict, TypedDict, TypeVar
from contingency_stats.result_schemas import BaseStatResult


class ContingencyTable(TypedDict):
    """Type definition for contingency table structure from ContingencyTableQuery."""
    exposed: Dict[str, int]
    unexposed: Dict[str, int]


# Clever pydantic typing for test result that's a subclass of BaseStatResult
# When defining you can specialise StatTestProtocol with the specific result type
T_Result = TypeVar('T_Result', bound=BaseStatResult)


class ContingencyTestProtocol(Protocol[T_Result]):
    """Protocol defining the interface for statistical tests."""

    def calculate(self, table: ContingencyTable) -> T_Result:
        """
        Calculate the statistical test from the contingency table.

        Args:
            table: A 2x2 contingency table with the structure from ContingencyTableQuery

        Returns:
            A test specific result object that inherits from BaseStatResult
        """
        ...
