import time
from hutch_bunny.core.upstream.task_api_client import TaskApiClient
from hutch_bunny.core.settings import get_settings, DaemonSettings
from hutch_bunny.core.rquest_dto.cohort import Cohort
from hutch_bunny.core.rquest_dto.group import Group
from availability_query import CustomAvailabilityQuery
from rule import CustomRule
from query_result import QueryResult
from job_response import JobResponse

settings: DaemonSettings = get_settings(daemon=True)

client = TaskApiClient(settings)

url = "/task/"
groups = [
    Group(
        rules=[
            CustomRule(
                varname="OMOP", varcat="Person", type_="TEXT", operator="=", value="8507"
            )
        ],
        rules_operator="AND",
    )
]
cohort = Cohort(groups=groups, groups_operator="OR")

query = CustomAvailabilityQuery(
    cohort=cohort,
    uuid="unique_id",
    owner="user1",
    collection=settings.COLLECTION_ID,
    protocol_version="v2",
    char_salt="salt",
)

payload = {"application": "AVAILABILITY_QUERY", "input": query.to_dict()}

response = client.post(url, data=payload)

job_response = JobResponse.from_dict(response.json())

# sleep
time.sleep(5)

url = f"/task/results/{job_response.job_uuid}/{settings.COLLECTION_ID}"

response = client.get(url)

result = QueryResult.from_api_response(response.json())

print(result)
