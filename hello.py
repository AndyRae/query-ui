from hutch_bunny.core.upstream.task_api_client import TaskApiClient
from hutch_bunny.core.settings import get_settings, DaemonSettings
from hutch_bunny.core.rquest_dto.cohort import Cohort
from hutch_bunny.core.rquest_dto.group import Group
from hutch_bunny.core.rquest_dto.rule import Rule
from availability_query import CustomAvailabilityQuery

settings: DaemonSettings = get_settings(daemon=True)

client = TaskApiClient(settings)

url = "/task/"
groups = [
    Group(
        rules=[
            Rule(varname="OMOP", varcat="Person", type="TEXT", oper="=", value="8507")
        ],
        rules_operator="OR",
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

print(response.json())
