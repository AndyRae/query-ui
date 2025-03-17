from contingency_table_builder import ContingencyTableQuery
from hutch_bunny.core.upstream.task_api_client import TaskApiClient
from hutch_bunny.core.settings import get_settings, DaemonSettings

settings: DaemonSettings = get_settings(daemon=True)
client = TaskApiClient(settings)

# Initialize the query builder
builder = ContingencyTableQuery(
    exposure_omop_code="8507",    # Male
    outcome_omop_code="24970",   # Ulcer of esophagus
    exposure_table="Person",
    outcome_table="Condition"
)

# Get the complete table
table = builder.build_contingency_table(client, settings.COLLECTION_ID, "user1")

# The results are now clearly labeled
print(f"""
2x2 Contingency Table:
                    With Ulcer of esophagus    Without Ulcer of esophagus
Male:              {table['exposed']['with_outcome']}    {table['exposed']['without_outcome']}
Female:            {table['unexposed']['with_outcome']}    {table['unexposed']['without_outcome']}
""")
