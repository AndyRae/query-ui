from pydantic import BaseModel
from typing import List

class QueryResultData(BaseModel):
    count: int
    datasetsCount: int
    files: List[str]  

class QueryResult(BaseModel):
    status: str
    protocolVersion: str
    uuid: str
    message: str
    queryResult: QueryResultData
    collection_id: str

    @classmethod
    def from_api_response(cls, response_data: dict) -> 'QueryResult':
        return cls(**response_data)
