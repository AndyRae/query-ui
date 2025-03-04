from dataclasses import dataclass
from typing import List
from hutch_bunny.core.rquest_dto.cohort import Cohort
from hutch_bunny.core.rquest_dto.group import Group
from hutch_bunny.core.rquest_dto.rule import Rule

from availability_query import CustomAvailabilityQuery

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
                        Rule(varname="OMOP", varcat=self.exposure_table, type="TEXT", oper="=", value=self.exposure_omop_code),
                        Rule(varname="OMOP", varcat=self.outcome_table, type="TEXT", oper="=", value=self.outcome_omop_code)
                    ],
                    rules_operator="AND"
                )
            ],
            groups_operator="OR"
        )
        
        # Exposure + Outcome -
        cohort_10 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(varname="OMOP", varcat=self.exposure_table, type="TEXT", oper="=", value=self.exposure_omop_code),
                        Rule(varname="OMOP", varcat=self.outcome_table, type="TEXT", oper="!=", value=self.outcome_omop_code)
                    ],
                    rules_operator="AND"
                )
            ],
            groups_operator="OR"
        )
        
        # Exposure - Outcome +
        cohort_01 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(varname="OMOP", varcat=self.exposure_table, type="TEXT", oper="!=", value=self.exposure_omop_code),
                        Rule(varname="OMOP", varcat=self.outcome_table, type="TEXT", oper="=", value=self.outcome_omop_code)
                    ],
                    rules_operator="AND"
                )
            ],
            groups_operator="OR"
        )
        
        # Exposure - Outcome -
        cohort_00 = Cohort(
            groups=[
                Group(
                    rules=[
                        Rule(varname="OMOP", varcat=self.exposure_table, type="TEXT", oper="!=", value=self.exposure_omop_code),
                        Rule(varname="OMOP", varcat=self.outcome_table, type="TEXT", oper="!=", value=self.outcome_omop_code)
                    ],
                    rules_operator="AND"
                )
            ],
            groups_operator="OR"
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
                char_salt="salt"
            )
            queries.append({
                "application": "AVAILABILITY_QUERY",
                "input": query.to_dict()
            })
            
        return queries 
