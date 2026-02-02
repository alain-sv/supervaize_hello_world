from loguru import logger
from supervaizer import (
    EntityStatus,
    JobContext,
    JobInstructions,
    JobResponse,
)


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
    cases = 0
    cost = 0.0

    job_fields = kwargs.get("fields", {})
    job_context: JobContext = kwargs.get("context", {})
    job_instructions: JobInstructions | None = job_context.job_instructions

    job_id = job_context.job_id

    logger.info(f"AGENT ExampleAgent: Starting Job {job_id}")
    logger.info(f"AGENT ExampleAgent: Job Fields : {job_fields}")
    logger.info(f"AGENT ExampleAgent: Job Instructions : {job_instructions}")

    for i in range(3):
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
                logger.error(f"AGENT ExampleAgent: Error on case {case_id}: {e}")
                if job_instructions and job_instructions.stop_on_error:
                    logger.error(f"AGENT ExampleAgent: STOPPING JOB ON ERROR: {e}")
                    raise Exception(e)
                else:
                    logger.info(
                        "AGENT ExampleAgent: CONTINUING JOB - stop_on_error is False"
                    )
        else:
            logger.warning(f"AGENT ExampleAgent: STOPPING JOB: {explanation}")
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

    logger.info(
        f"AGENT ExampleAgent: Job {job_id} completed - Total cost: {cost} -> {res}"
    )

    return res
