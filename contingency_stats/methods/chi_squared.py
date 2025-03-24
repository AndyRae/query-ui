from scipy import stats
import numpy as np

from contingency_stats.protocols import ContingencyTable, ContingencyTestProtocol
from contingency_stats.result_schemas import ChiSquaredResult
from contingency_stats.contingency_utils import table_to_array, calculate_expected_values, format_p_value


class ChiSquaredTest(ContingencyTestProtocol[ChiSquaredResult]):
    """Chi-squared test implementation for 2x2 contingency tables."""

    def __init__(self, alpha: float = 0.05, yates_correction: bool = False):
        """
        Initialise the Chi-squared test.

        Args:
            alpha: Significance level (default: 0.05)
        """
        self.alpha = alpha
        self.test_name = "Chi-squared Test"
        self.yates_correction = yates_correction

    def calculate(self, table: ContingencyTable) -> ChiSquaredResult:
        """
        Calculate Chi-squared statistic and p-value for the contingency table.
        Calculate Cramér's V as a measure of the strength of association.

        Args:
            table: A 2x2 contingency table with the structure from ContingencyTableQuery

        Returns:
            ChiSquaredResult with test results
        """
        observed = table_to_array(table)
        expected = calculate_expected_values(observed)

        chi2, p, dof, _ = stats.chi2_contingency(
            observed, correction=self.yates_correction
        )

        n = observed.sum()
        cramers_v = np.sqrt(chi2 / (n * (min(observed.shape) - 1)))

        interpretation = (
            f"There is {'no ' if p >= self.alpha else ''}statistically significant association between exposure and outcome "
            f"({format_p_value(p)}). Chi-squared statistic: {chi2:.2f}, df={dof}" +
            (" (with Yates' correction)" if self.yates_correction else "") +
            f". Cramér's V: {cramers_v:.2f}"
        )

        return ChiSquaredResult(
            test_name=self.test_name + (" with Yates' correction" if self.yates_correction else ""),
            test_statistic=chi2,
            degrees_of_freedom=dof,
            p_value=p,
            is_significant=p < self.alpha,
            cramers_v=cramers_v,
            interpretation=interpretation,
            alpha=self.alpha,
            expected_values=expected.tolist(),
            yates_correction_applied=self.yates_correction,
            additional_info={"observed_values": observed.tolist()}
        )
