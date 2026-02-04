import random
from time import sleep
from loguru import logger as log
from supervaizer import (
    Case,
    CaseNodeUpdate,
    EntityStatus,
    JobContext,
    JobInstructions,
    JobResponse,
)

from __init__ import supervaize_account


def custom_case_start(case_id: str, job_id: str, **kwargs):
    log.info(
        f"AGENT ExampleAgent: Starting Case [blue]{case_id}[/blue] with params: {kwargs}"
    )

    kwargs["case_id"] = case_id
    random_sleep = random.uniform(0, 5)
    random_cost = random.uniform(0, 10)
    case = Case.start(
        job_id=job_id,
        account=supervaize_account,
        name=f"Case {case_id}",
        description=f"case {case_id} in job {job_id} - random sleep {random_sleep} - random cost {random_cost}",
    )

    sleep(random_sleep)

    case.update(
        CaseNodeUpdate(
            name=f"Update Case {case_id}",
            cost=random_cost,
            payload={
                "message": f"This a case update after sleeping for {random_sleep} seconds! - cost was {random_cost}"
            },
            is_final=False,
        )
    )

    case.close(case_result={"message": "Case Completed"})

    log.info(f"AGENT ExampleAgent: Case id {case_id} finished")
    return case


def resume_case_with_human_input(case_id: str, job_id: str, **kwargs):
    case = Case.resume(id=case_id, job_id=job_id, account=supervaize_account)

    case.close()
    return


# Custom method to start a synchronous job.
def job_start(**kwargs) -> JobResponse | None:
    """
    This is a synchronous job : all cases are executed in the same process.
    It is useful for testing and development.

    Expects a JobResponse object to be returned.

    **kwargs:
        fields: dict
            The custom fields required for the job execution. Defined by you in the job_start_method.
        context: JobContext
            The context of the job - contains job_id, mission_id, mission_context. Provided by the Supervaize platform.
        conditions: JobInstructions
            The conditions of the job - contains stop_on_error, max_cases, etc. Defined by the user when the job is created in the Supervaize platform.
    """

    log.info(f"AGENT ExampleAgent: Received kwargs: {kwargs}")
    for key, value in kwargs.items():
        log.debug(f"AGENT kwargs - {key}: {value}")

    cases = 0
    cost = 0.0

    job_fields = kwargs.get("fields", {})
    job_context: JobContext = kwargs.get("context", {})
    job_instructions: JobInstructions | None = job_context.job_instructions

    job_id = job_context.job_id

    log.info(f"AGENT ExampleAgent: Starting Job {job_id}")
    log.info(f"AGENT ExampleAgent: Job Fields : {job_fields}")
    log.info(f"AGENT ExampleAgent: Job Instructions : {job_instructions}")
    log.info(
        f"AGENT ExampleAgent: Agent Parameters : {kwargs.get('encrypted_agent_parameters', None)}"
    )

    """
    Sample logs: 
    This is how we receive the 
    agent_parameters = [
        {
            "name": "SIMPLE AGENT SECRET",
            "team_id": 2,
            "description": "Setup agent secret in this workspace",
            "is_environment": True,
            "value": "123456",
            "is_secret": True,
            "is_required": False,
        },
        {
            "name": "SIMPLE AGENT PARAMETER",
            "team_id": 2,
            "description": "Setup agent parameter in this workspace",
            "is_environment": True,
            "value": "123456",
            "is_secret": False,
            "is_required": False,
        },
    ]
    
    - Sample job_context:
    {'job_context': {'workspace_id': 'odm', 'job_id': '01KGG50ZMY557VTC8YAQBAHKXP', 
    'started_by': 'alp', 'started_at': '2026-02-02T21:44:32.159453+00:00', 'mission_id': '01KGG50ZMFYMHG9N5FGCACF0XA', 
    'mission_name': 'Operate Agent Hello World AI Agent', 'job_instructions': {'max_cost': None, 'max_cases': None,
    'max_duration': None, 'stop_on_error': True, 'stop_on_warning': False}}, 'job_fields': {'How many times to say hello': '3'}, 
    'encrypted_agent_parameters': 'TnPjhEHJnwOT+tsbI9CvpUt3taqKNoep4LnrgCxtv3fHrMIMRBHHAUW8bvCq2Rxak/LqtEaYi3FknWnGYYdPyld5/oGay0fEkcJMiRa5P5OmJHiAXW+kncNLlPiKSpaELyuXnGTP+E9sI+ktkPlYFbCsy1+DqvwB0gJ3mEAA2SUH5P8Fzic7DY3ksb1Kuqyd24hm+3maMGnyn4a5T4mb90Hc4w6h1xRjsR4UaqHOSpxVV4SstIUbgf0thcQxxgrHGYejxsBT9TD6lqvzUoO/fvmpcYNt1k7r8ppv9VwUGM+5Ah2gwoYN7HhFM5kXwfhP2fm4LF1UYVkTlAlxeSerTAF8pPPCzXqWI+BluCpsQRvL0Qc0MuVow8XJ2xD0Q/EJs4N7hMDhznIvsU1OVLegzycwH2+vVDDphy2aXBePZmx7dRJNKSvKPampuLi7so/IxGXTOc02GuUogBk7Hh729MOtA3zRaMrKVUJMnhXEQS4tjm/Xfeaf3odMOXgoeSXB8WAu7wfLflzuIa3CFpnp/daLtdi7Q9NccGLgkpgASUIuq0HviN+FB0qH1QAYX4x8bfVC/JIpb2je8/AKijl6EzwZ9bm5unLo78kEDw/vBD25JCHMg/G8MoqyKK2myFmyHSxbmenT85c6f2B2xFYEXrMZRrqPxfVNAH8rdcH+0+rjRemm0U+erGsI2Lg/KnmPjYTlK5NJA/MoBCZBUfNAozIS7cvUQr1MWSrrNdpFdIzBWL1pNA3ZJcISLrvIxuFgDKyM4xz+365rOLALa2qHMk1bovjmTGtgAMP3VTdf59JWtQOvpIw+sv7kH5D2FgHkzJFuPo8Eobna4teKQWORikvGgdxLv8q4m7pxdyTSJDU='}

    """

    # Get main job field:
    how_many_times_to_say_hello = int(job_fields.get("How many times to say hello")))

    for i in range(how_many_times_to_say_hello):
        # Check if the conditions to continue the job are met.
        check, explanation = (
            job_instructions.check(cases=cases, cost=cost)
            if job_instructions
            else (True, "No conditions")
        )
        if check:  # REQUIRED - the job conditions must be met for the job to continue.
            case_id = f"C{i + 1}"
            try:
                case_result = custom_case_start(
                    case_id=case_id, job_id=job_id, **kwargs
                )  # Execute case - case_is is optional.
                cost += getattr(case_result, "cost", 1.1)  # Increment cost of job
                cases += 1  # Increment number of cases
            except Exception as e:
                log.error(f"AGENT ExampleAgent: Error on case {case_id}: {e}")
                if job_instructions and job_instructions.stop_on_error:
                    log.error(f"AGENT ExampleAgent: STOPPING JOB ON ERROR: {e}")
                    raise Exception(e)
                else:
                    log.info(
                        "AGENT ExampleAgent: CONTINUING JOB - stop_on_error is False"
                    )
        else:
            log.warning(f"AGENT ExampleAgent: STOPPING JOB: {explanation}")
            break

    final_deliverable = {"VERY": "IMPORTANT"}
    # start = main(action="run")
    res = JobResponse(
        job_id=job_id,
        status=EntityStatus.COMPLETED,
        message="Job Completed",
        payload=final_deliverable,
        cost=cost,
    )

    log.info(
        f"AGENT ExampleAgent: Job {job_id} completed - Total cost: {cost} -> {res}"
    )

    return res


def job_stop(**kwargs) -> None:
    """
    Called when the platform requests to stop the running job.
    For this sync agent a no-op is enough; long-running agents would set a stop flag here.
    """
    job_context = kwargs.get("context") or {}
    job_id = getattr(job_context, "job_id", None) or (
        job_context.get("job_id") if isinstance(job_context, dict) else None
    )
    log.info(f"AGENT ExampleAgent: job_stop requested for job_id={job_id}")


def job_status(**kwargs):
    """
    Return current job/agent status. Platform may call this to display status.
    """
    job_context = kwargs.get("context") or {}
    job_id = getattr(job_context, "job_id", None) or (
        job_context.get("job_id") if isinstance(job_context, dict) else None
    )
    log.info(f"AGENT ExampleAgent: job_status requested for job_id={job_id}")
    return {"status": "idle", "job_id": job_id}
