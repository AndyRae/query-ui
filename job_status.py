from pydantic import BaseModel

class JobStatus(BaseModel):
    job_uuid: str
    status: str

    @classmethod
    def from_api_response(cls, response_data: list) -> 'JobStatus':
        job_uuid, status = next(iter(response_data[0].items()))
        return cls(job_uuid=job_uuid, status=status)
