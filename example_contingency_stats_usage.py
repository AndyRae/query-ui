from contingency_stats.protocols import ContingencyTable
from contingency_stats.methods.chi_squared import ChiSquaredTest
from contingency_stats.methods.fishers_exact import FishersExactTest

# Create a sample 2x2 contingency table
# This example represents:
#   - 30 out of 100 exposed subjects had the outcome
#   - 10 out of 100 unexposed subjects had the outcome
# For the purpose of this example, we'll interpret "outcome" as having a disease and "exposed" as smokers
table: ContingencyTable = {
    "exposed": {
        "with_outcome": 30,
        "without_outcome": 70
    },
    "unexposed": {
        "with_outcome": 10,
        "without_outcome": 90
    }
}

# Example Question: “Is smoking status related to having (or not having) the disease?”
# Null Hypothesis: There is no association between smoking status and disease status
# Use: A Chi-Square test of independence or, for small counts, Fisher’s Exact test.
# Insight: smoking status and disease status occur together more (or less) often than chance would predict
# i.e., is there a statistical association?

fishers_exact_test = FishersExactTest(
    alpha=0.05,  # 95% confidence interval for p-value
    confidence_level=0.99,  # 99% confidence interval for odds ratio
    alternative="two-sided"  # Alternative hypothesis (default: 'two-sided')
)
result = fishers_exact_test.calculate(table)
print(result.dict())

chi_squared_test = ChiSquaredTest(
    alpha=0.05,  # 95% confidence interval for p-value
    yates_correction=False
)
result = chi_squared_test.calculate(table)
print(result.dict())

chi_squared_test_yates = ChiSquaredTest(
    alpha=0.05,  # 95% confidence interval for p-value
    yates_correction=True
)
result = chi_squared_test_yates.calculate(table)
print(result.dict())
