"""Module for creating REST API's"""
from typing import ClassVar, Optional
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class Job(BaseModel):
    """Model for representing a job"""
    _job_counter: ClassVar[int] = 0
    job_id: int
    job_name: str
    test_case: str

    def __init__(self, **data):
        Job._job_counter += 1
        data['job_id'] = Job._job_counter
        super().__init__(**data)

job_database: list[Job] = []
args_database: list[str] = []

@app.get("/")
def root():
    """Root endpoint for checking if the server is alive.

    """
    return {"I'm alive"}

def _get_job_by_id(job_id: int) -> Job:
    """Returns the Job by job_id"""
    return [job for job in job_database if job.job_id == job_id][0]

@app.get("/jobs")
def get_jobs(job_id: Optional[int] = None):
    """Returns all jobs or a specific job"""
    if job_id is None:
        return job_database
    return _get_job_by_id(job_id)

@app.post("/job")
def create_job(new_job: Job):
    """Creates a new job"""
    job_database.append(new_job)

@app.post("/args")
def create_args(robot_args: str):
    """Creates args"""
    args_database.append(robot_args)

@app.post("/run")
def execute_job(job_id: int):
    """Executes the specified job."""
    exec_job: Job = _get_job_by_id(job_id)
    #TODO: pass the fields into a robot parser at this point