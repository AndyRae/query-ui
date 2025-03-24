from typing import Tuple, Literal
import numpy as np
from scipy import stats

from contingency_stats.protocols import ContingencyTable, ContingencyTestProtocol
from contingency_stats.result_schemas import FishersExactResult
from contingency_stats.contingency_utils import table_to_array, format_p_value


class FishersExactTest(ContingencyTestProtocol[FishersExactResult]):
    """Fisher's Exact test implementation for 2x2 contingency tables, supporting different alternative hypotheses."""

    def __init__(self, alpha: float = 0.05, confidence_level: float = 0.95, alternative: Literal["two-sided", "greater", "less"] = "two-sided"):
        """
        Initialise the Fisher's Exact test.

        Args:
            alpha: Significance level (default: 0.05)
            confidence_level: Confidence level for intervals (default: 0.95)
            alternative: Type of hypothesis test ('two-sided', 'greater', or 'less')
        """
        self.alpha = alpha
        self.confidence_level = confidence_level
        self.alternative = alternative
        self.test_name = f"Fisher's Exact Test ({alternative})"

    def _calculate_odds_ratio_ci(
            self, table: np.ndarray, confidence_level: float
    ) -> Tuple[float, Tuple[float, float]]:
        """
        Calculate the odds ratio and confidence interval.

        Args:
            table: 2x2 numpy array of the contingency table
            confidence_level: Confidence level (e.g., 0.95 for 95% CI)

        Returns:
            Tuple of (odds_ratio, (lower_bound, upper_bound))
        """
        a, b = table[0, 0], table[0, 1]
        c, d = table[1, 0], table[1, 1]

        odds_ratio = (a * d) / (b * c) if (b * c) != 0 else float('inf')

        if odds_ratio != float('inf'):
            log_odds = np.log(odds_ratio)
            if any(x == 0 for x in [a, b, c, d]):
                se_log_odds = np.nan
            else:
                se_log_odds = np.sqrt(1 / a + 1 / b + 1 / c + 1 / d)

            z = stats.norm.ppf(1 - (1 - confidence_level) / 2)
            log_lower = log_odds - z * se_log_odds
            log_upper = log_odds + z * se_log_odds

            lower = np.round(np.exp(log_lower), 3)
            upper = np.round(np.exp(log_upper), 3)
        else:
            lower, upper = float('nan'), float('inf')

        return odds_ratio, (lower, upper)

    def calculate(self, table: ContingencyTable) -> FishersExactResult:
        """
        Calculate Fisher's Exact test for the contingency table.

        Args:
            table: A 2x2 contingency table with the structure from ContingencyTableQuery

        Returns:
            FishersExactResult with test results
        """
        observed = table_to_array(table)

        # Calculate Fisher's Exact test with the chosen alternative hypothesis
        _, p = stats.fisher_exact(observed, alternative=self.alternative)

        # Calculate odds ratio and confidence interval
        odds_ratio, ci = self._calculate_odds_ratio_ci(observed, self.confidence_level)

        # Construct interpretation based on alternative hypothesis
        if self.alternative == "two-sided":
            interpretation = (
                f"There is {'no' if p >= self.alpha else 'a'} statistically significant association between exposure and outcome "
                f"({format_p_value(p)}). Odds ratio: {odds_ratio:.2f} "
                f"(95% CI: {ci[0]:.2f} to {ci[1] if ci[1] != float('inf') else 'infinity'})"
            )
        elif self.alternative == "greater":
            interpretation = (
                f"There is {'no' if p >= self.alpha else 'a'} statistically significant positive association (odds ratio > 1) "
                f"between exposure and outcome ({format_p_value(p)})."
            )
        else:  # "less"
            interpretation = (
                f"There is {'no' if p >= self.alpha else 'a'} statistically significant negative association (odds ratio < 1) "
                f"between exposure and outcome ({format_p_value(p)})."
            )

        return FishersExactResult(
            test_name=self.test_name,
            p_value=p,
            is_significant=p < self.alpha,
            interpretation=interpretation,
            alpha=self.alpha,
            odds_ratio=odds_ratio,
            confidence_interval=ci,
            additional_info={
                "observed_values": observed.tolist(),
                "confidence_level": self.confidence_level,
                "alternative": self.alternative,
            }
        )
