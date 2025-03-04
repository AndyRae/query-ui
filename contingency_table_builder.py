from dataclasses import dataclass
from typing import List, Dict, Any
from hutch_bunny.core.rquest_dto.cohort import Cohort
from hutch_bunny.core.rquest_dto.group import Group
from hutch_bunny.core.rquest_dto.rule import Rule
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

    def build_cohorts(self) -> List[Cohort]:
        """Builds four cohorts for a 2x2 contingency table"""
        # Exposure + Outcome +
        cohort_11 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(
                            varname="OMOP",
                            varcat=self.exposure_table,
                            type="TEXT",
                            oper="=",
                            value=self.exposure_omop_code,
                        ),
                        Rule(
                            varname="OMOP",
                            varcat=self.outcome_table,
                            type="TEXT",
                            oper="=",
                            value=self.outcome_omop_code,
                        ),
                    ],
                    rules_operator="AND",
                )
            ],
            groups_operator="OR",
        )

        # Exposure + Outcome -
        cohort_10 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(
                            varname="OMOP",
                            varcat=self.exposure_table,
                            type="TEXT",
                            oper="=",
                            value=self.exposure_omop_code,
                        ),
                        Rule(
                            varname="OMOP",
                            varcat=self.outcome_table,
                            type="TEXT",
                            oper="!=",
                            value=self.outcome_omop_code,
                        ),
                    ],
                    rules_operator="AND",
                )
            ],
            groups_operator="OR",
        )

        # Exposure - Outcome +
        cohort_01 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(
                            varname="OMOP",
                            varcat=self.exposure_table,
                            type="TEXT",
                            oper="!=",
                            value=self.exposure_omop_code,
                        ),
                        Rule(
                            varname="OMOP",
                            varcat=self.outcome_table,
                            type="TEXT",
                            oper="=",
                            value=self.outcome_omop_code,
                        ),
                    ],
                    rules_operator="AND",
                )
            ],
            groups_operator="OR",
        )

        # Exposure - Outcome -
        cohort_00 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(
                            varname="OMOP",
                            varcat=self.exposure_table,
                            type="TEXT",
                            oper="!=",
                            value=self.exposure_omop_code,
                        ),
                        Rule(
                            varname="OMOP",
                            varcat=self.outcome_table,
                            type="TEXT",
                            oper="!=",
                            value=self.outcome_omop_code,
                        ),
                    ],
                    rules_operator="AND",
                )
            ],
            groups_operator="OR",
        )

        return [cohort_11, cohort_10, cohort_01, cohort_00]

    def build_queries(self, collection_id: str, owner: str) -> List[dict]:
        """Builds complete query payloads for all four cells of the contingency table"""
        cohorts = self.build_cohorts()
        queries = []

        for i, cohort in enumerate(cohorts):
            query = CustomAvailabilityQuery(
                cohort=cohort,
                uuid=f"contingency_{i}",
                owner=owner,
                collection=collection_id,
                protocol_version="v2",
                char_salt="salt",
            )
            queries.append(
                {"application": "AVAILABILITY_QUERY", "input": query.to_dict()}
            )

        return queries

    def execute_queries(
        self, client: TaskApiClient, collection_id: str, owner: str
    ) -> List[JobResponse]:
        """Executes all queries and returns job responses"""
        queries = self.build_queries(collection_id, owner)
        job_responses: List[JobResponse] = []

        for query in queries:
            response = client.post("/task/", data=query)
            job_responses.append(JobResponse.from_dict(response.json()))

        return job_responses

    def fetch_results(
        self,
        collection_id: str,
        client: TaskApiClient,
        job_responses: List[JobResponse],
    ) -> List[Dict[str, Any]]:
        """Fetches results for all job responses"""
        results = []
        for job in job_responses:
            response = client.get(f"/task/results/{job.job_uuid}/{collection_id}")
            results.append(response.json())
        return results

    def wait_for_jobs(
        self,
        client: TaskApiClient,
        job_responses: List[JobResponse],
        max_attempts: int = 30,
        delay: int = 2,
    ) -> List[JobResponse]:
        """
        Waits for all jobs to complete with a polling mechanism

        Args:
            client: The API client
            job_responses: List of job responses to check
            max_attempts: Maximum number of polling attempts
            delay: Delay between polling attempts in seconds

        Returns:
            List of completed job responses
        """
        completed_jobs: List[JobResponse] = []
        attempts = 0

        while len(completed_jobs) < len(job_responses) and attempts < max_attempts:
            for job in job_responses:
                if job not in completed_jobs:
                    # Implement the actual status check API call here
                    response = client.get(f"/task/{job.job_uuid}/status")
                    status = response.json().get("status")

                    if status == "COMPLETED":
                        completed_jobs.append(job)
                    elif status == "FAILED":
                        raise Exception(f"Job {job.job_uuid} failed")

            if len(completed_jobs) < len(job_responses):
                time.sleep(delay)
                attempts += 1

        if len(completed_jobs) < len(job_responses):
            raise TimeoutError("Not all jobs completed within the maximum attempts")

        return completed_jobs
