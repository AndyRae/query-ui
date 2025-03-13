from dataclasses import dataclass
from typing import Dict, Optional
from hutch_bunny.core.rquest_dto.cohort import Cohort
from hutch_bunny.core.rquest_dto.group import Group
from job_status import JobStatus
from rule import CustomRule
from query_result import QueryResult
from job_response import JobResponse
from availability_query import CustomAvailabilityQuery
from hutch_bunny.core.upstream.task_api_client import TaskApiClient
import time

@dataclass
class ContingencyTableQuery:
    exposure_omop_code: str
    outcome_omop_code: str
    exposure_table: str = "Condition"
    outcome_table: str = "Condition"

    def execute_single_query(
        self, 
        client: TaskApiClient, 
        collection_id: str, 
        owner: str,
        exposure_present: bool,
        outcome_present: bool
    ) -> int:
        """Execute a single query and return its count"""
        # Build the rules based on presence/absence
        rules = [
            CustomRule(
                varname="OMOP",
                varcat=self.exposure_table,
                type_="TEXT",
                operator="=" if exposure_present else "!=",
                value=self.exposure_omop_code,
            ),
            CustomRule(
                varname="OMOP",
                varcat=self.outcome_table,
                type_="TEXT",
                operator="=" if outcome_present else "!=",
                value=self.outcome_omop_code,
            ),
        ]

        # Create cohort
        cohort = Cohort(
            groups=[Group(rules=rules, rules_operator="AND")],
            groups_operator="OR",
        )

        # Create and execute query
        query = CustomAvailabilityQuery(
            cohort=cohort,
            uuid=f"contingency_{exposure_present}_{outcome_present}",
            owner=owner,
            collection=collection_id,
            protocol_version="v2",
            char_salt="salt",
        )

        payload = {"application": "AVAILABILITY_QUERY", "input": query.to_dict()}

        print(payload)
        
        # Send query and get job response
        response = client.post("/task/", data=payload)
        job_response = JobResponse.from_dict(response.json())

        print(job_response)

        # Wait for completion
        while True:
            status_response = client.get(f"/task/status/{job_response.job_uuid}")
            status = JobStatus.from_api_response(status_response.json())
            print(status)

            if status.status == "JOB_DONE":
                break
            time.sleep(2)

        # Get results
        result_response = client.get(f"/task/results/{job_response.job_uuid}/{collection_id}")
        result = QueryResult.from_api_response(result_response.json())
        
        return result.queryResult.count

    def build_contingency_table(
        self, 
        client: TaskApiClient, 
        collection_id: str, 
        owner: str
    ) -> Dict[str, Dict[str, int]]:
        """Build the complete 2x2 contingency table"""
        table = {
            "exposed": {
                "with_outcome": self.execute_single_query(
                    client, collection_id, owner, 
                    exposure_present=True, outcome_present=True
                ),
                "without_outcome": self.execute_single_query(
                    client, collection_id, owner, 
                    exposure_present=True, outcome_present=False
                )
            },
            "unexposed": {
                "with_outcome": self.execute_single_query(
                    client, collection_id, owner, 
                    exposure_present=False, outcome_present=True
                ),
                "without_outcome": self.execute_single_query(
                    client, collection_id, owner, 
                    exposure_present=False, outcome_present=False
                )
            }
        }
        return table
