"""
Agent that runs cases with a human-in-the-loop approval step.
Each case does work, then requests human approval before closing.
"""

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
        f"AGENT HumanLoopAgent: Starting Case [blue]{case_id}[/blue] with params: {kwargs}"
    )
    kwargs["case_id"] = case_id
    random_sleep = random.uniform(0, 5)
    random_cost = random.uniform(0, 10)
    case = Case.start(
        job_id=job_id,
        account=supervaize_account,
        name=f"Case {case_id}",
        description=f"case {case_id} in job {job_id} - random sleep {random_sleep} - random cost {random_cost}",
        case_id=case_id,
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

    # Human-in-the-loop: every case asks for approval before completing
    case.request_human_input(
        CaseNodeUpdate(
            name="Human approval",
            cost=0.0,
            payload={
                "supervaizer_form": {
                    "question": f"Case {case_id} has run (sleep {random_sleep:.1f}s, cost {random_cost:.1f}). Approve to complete or reject.",
                    "answer": {
                        "fields": [
                            {
                                "name": "Approved",
                                "description": "Approve and complete this case",
                                "type": bool,
                                "field_type": "BooleanField",
                                "required": False,
                            },
                            {
                                "name": "Rejected",
                                "description": "Reject this case",
                                "type": bool,
                                "field_type": "BooleanField",
                                "required": False,
                            },
                        ],
                    },
                },
                "case_id": case_id,
                "cost_so_far": random_cost,
            },
            is_final=False,
        ),
        "Please approve to continue or reject this case.",
    )
    log.info(f"AGENT HumanLoopAgent: Case {case_id} waiting for human input")
    return case


def handle_human_input(**kwargs) -> JobResponse:
    """Called by the platform when a human submits the form from request_human_input."""
    context_raw = kwargs.get("context")
    if context_raw is None:
        raise ValueError("context is required in kwargs")
    if isinstance(context_raw, dict):
        job_context = JobContext(**context_raw)
    else:
        job_context = context_raw
    job_id = job_context.job_id
    fields = kwargs.get("fields", {})
    payload = kwargs.get("payload") or {}
    case_id = (
        getattr(job_context, "case_id", None)
        or fields.get("case_id")
        or kwargs.get("case_id")
        or payload.get("case_id")
    )
    if not case_id:
        raise ValueError("case_id not found in context, fields or payload")
    cost_so_far = float(fields.get("cost_so_far") or payload.get("cost_so_far", 0) or 0)

    case = Case.resume(id=case_id, job_id=job_id, account=supervaize_account)
    approved = fields.get("Approved") is True
    rejected = fields.get("Rejected") is True
    if approved and not rejected:
        case.update(
            CaseNodeUpdate(
                name="✅ Human approved",
                cost=0.0,
                payload={"status": "approved"},
                is_final=False,
            )
        )
        case.close(
            case_result={"message": "Case Completed", "status": "approved"},
            final_cost=cost_so_far,
        )
    else:
        case.update(
            CaseNodeUpdate(
                name="❌ Human rejected",
                cost=0.0,
                payload={"status": "rejected"},
                is_final=False,
            )
        )
        case.close(
            case_result={"message": "Case rejected", "status": "rejected"},
            final_cost=cost_so_far,
        )
    log.info(
        f"AGENT HumanLoopAgent: Human input processed for case {case_id} (approved={approved})"
    )
    return JobResponse(
        job_id=job_id,
        status=EntityStatus.COMPLETED,
        message="Human input processed",
        payload={"case_id": case_id, "approved": approved},
    )


def job_start(**kwargs) -> JobResponse | None:
    """Synchronous job: runs N cases, each pauses for human approval before completing."""
    log.info(f"AGENT HumanLoopAgent: Received kwargs: {kwargs}")

    job_fields = kwargs.get("fields", {})
    job_context: JobContext = kwargs.get("context", {})
    job_instructions: JobInstructions | None = job_context.job_instructions
    job_id = job_context.job_id

    how_many = int(job_fields.get("How many cases to run", 1))
    cases = 0
    cost = 0.0

    for i in range(how_many):
        check, explanation = (
            job_instructions.check(cases=cases, cost=cost)
            if job_instructions
            else (True, "No conditions")
        )
        if not check:
            log.warning(f"AGENT HumanLoopAgent: STOPPING JOB: {explanation}")
            break
        case_id = f"C{i + 1}"
        try:
            case_result = custom_case_start(case_id=case_id, job_id=job_id, **kwargs)
            cost += getattr(case_result, "cost", 0.0)
            cases += 1
        except Exception as e:
            log.error(f"AGENT HumanLoopAgent: Error on case {case_id}: {e}")
            if job_instructions and job_instructions.stop_on_error:
                raise

    return JobResponse(
        job_id=job_id,
        status=EntityStatus.COMPLETED,
        message=f"Started {cases} case(s) awaiting human approval",
        payload={"cases_started": cases, "cost_so_far": cost},
        cost=cost,
    )


def job_stop(**kwargs) -> None:
    job_context = kwargs.get("context") or {}
    job_id = getattr(job_context, "job_id", None) or (
        job_context.get("job_id") if isinstance(job_context, dict) else None
    )
    log.info(f"AGENT HumanLoopAgent: job_stop requested for job_id={job_id}")


def job_status(**kwargs):
    job_context = kwargs.get("context") or {}
    job_id = getattr(job_context, "job_id", None) or (
        job_context.get("job_id") if isinstance(job_context, dict) else None
    )
    log.info(f"AGENT HumanLoopAgent: job_status requested for job_id={job_id}")
    return {"status": "idle", "job_id": job_id}
