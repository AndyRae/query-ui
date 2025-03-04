from contingency_table_builder import ContingencyTableQuery
from hutch_bunny.core.upstream.task_api_client import TaskApiClient
from hutch_bunny.core.settings import get_settings, DaemonSettings
import time

settings: DaemonSettings = get_settings(daemon=True)
client = TaskApiClient(settings)

# Create the contingency table query
contingency_builder = ContingencyTableQuery(
    exposure_omop_code="201820",  # Diabetes mellitus
    outcome_omop_code="316139",  # Heart disease
    exposure_table="Condition",
    outcome_table="Condition",
)

# Execute queries and get job responses
job_responses = contingency_builder.execute_queries(
    client=client, collection_id=settings.COLLECTION_ID, owner="user1"
)

# Wait for jobs to complete
time.sleep(30)

# Fetch results
results = contingency_builder.fetch_results(
    settings.COLLECTION_ID, client, job_responses
)

print(results)
