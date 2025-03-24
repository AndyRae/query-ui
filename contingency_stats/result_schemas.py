from pydantic import BaseModel, Field
from typing import Dict, Any, Optional, List, Tuple


class BaseStatResult(BaseModel):
    """Base model for all statistical test results."""

    test_name: str = Field(..., description="Name of the statistical test")
    p_value: float = Field(..., description="P-value of the test result")
    alpha: float = Field(0.05, description="Significance level used for the test")

    is_significant: bool = Field(..., description="Whether the result is statistically significant")
    interpretation: str = Field(..., description="Interpretation of the statistical results")

    additional_info: Dict[str, Any] = Field(
        default_factory=dict,
        description="Additional test-specific information"
    )


class ChiSquaredResult(BaseStatResult):
    """Chi-squared test specific result model."""

    test_statistic: float = Field(..., description="Chi-squared statistic value")
    degrees_of_freedom: int = Field(..., description="Degrees of freedom")
    cramers_v: float = Field(..., description="Cramér's V effect size")
    expected_values: Optional[List[List[float]]] = Field(
        None, description="Expected values for each cell"
    )
    yates_correction_applied: bool = Field(
        False, description="Whether Yates' correction was applied"
    )


class FishersExactResult(BaseStatResult):
    """Fisher's exact test specific result model."""

    odds_ratio: float = Field(..., description="Odds ratio")
    confidence_interval: Tuple[float, float] = Field(
        ..., description="Confidence interval for the odds ratio"
    )