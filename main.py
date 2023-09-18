"""Module for creating REST API's"""
import uvicorn
import subprocess
import os
from pathlib import Path
from typing import ClassVar, Optional
from fastapi import FastAPI, HTTPException, status
from pydantic import BaseModel

app = FastAPI()

jobs_path: str = "/tmp/jobs/"
jobs_log_path: str = "/tmp/jobs_log/"

class Job(BaseModel):
    """Model for representing a job"""
    job_name: str
    test_case: str


@app.get("/")
def root():
    """Root endpoint for checking if the server is alive.

    """
    return {"I'm alive"}


def _get_all_jobs() -> list[Job]:
    existing_jobs: list[Job] = []
    if os.path.exists(jobs_path):

        # List all files in the directory
        file_names = os.listdir(jobs_path)
        for file in file_names:
            job_name: str = file
            job_name, _ = os.path.splitext(job_name)
            job_test_case: str = Path(f"/tmp/jobs/{file}").read_text()
            existing_jobs.append(Job(job_name=job_name, test_case=job_test_case))
        return existing_jobs
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='No Jobs found!')
    
def _get_job_by_name(job_name: str) -> Job:
    all_jobs = _get_all_jobs()
    try:
        job = [job for job in all_jobs if job.job_name == job_name][0]
    except IndexError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"No job with name: {job_name}, found!")
    return job


@app.get("/jobs")
def get_jobs(job_name: Optional[str] = None) -> dict:
    """Returns all jobs or a specific job"""
    if job_name is None:
        return _get_all_jobs()
    return _get_job_by_name(job_name)

@app.post("/job")
def create_job(new_job: Job) -> None:
    """Creates a new job"""
    if not os.path.exists(jobs_path):
        os.makedirs(jobs_path)
        print(f"Directory {jobs_path} created successfully!")
    with open(f"/tmp/jobs/{new_job.job_name}.robot", "w") as robot_file:
        robot_file.write(new_job.test_case)

@app.post("/run")
def execute_job(job_name: str) -> None:
    """Executes the specified job."""
    if not os.path.exists(jobs_log_path):
        os.makedirs(jobs_log_path)
        print(f"Directory {jobs_log_path} created successfully!")
    file_names = os.listdir(jobs_path)   
    exec_job: Job = _get_job_by_name(job_name)
    exec_job_name: str = exec_job.job_name
    log_name: str = f"log_{exec_job_name}"
    print(f"the file name: {file_names}]")
    if log_name in file_names:
        print(f"the file name: {file_names}]")
        result = subprocess.run(f"sudo rm {jobs_log_path}/{log_name}.html", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    result = subprocess.run(f"robot --log {jobs_log_path}/{log_name} /tmp/jobs/{exec_job_name}.robot", 
                            shell=True, 
                            stdout=subprocess.PIPE, 
                            stderr=subprocess.PIPE, 
                            text=True)
    print(result)

@app.delete("/job")
def delete_job(job_name: str) -> None:
    result = subprocess.run(f"rm /tmp/jobs/{job_name}.robot", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)

@app.get("/log")
def get_log(job_name: str) -> str:
    job = _get_job_by_name(job_name)
    job_name = job.job_name

    log_name: str = f"log_{job_name}.html"
    log_raw_string = Path(f"/tmp/jobs_log/{log_name}").read_text()
    return log_raw_string

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)