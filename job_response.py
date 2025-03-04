from dataclasses import dataclass
from typing import Optional


@dataclass
class JobResponse:
    job_id: str
    job_uuid: str
    message: Optional[str] = None

    @classmethod
    def from_dict(cls, data: dict) -> "JobResponse":
        return cls(
            job_id=data["job-id"],
            job_uuid=data["job-uuid"],
            message=data.get("message"),
        )
