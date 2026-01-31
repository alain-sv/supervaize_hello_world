# Copyright (c) 2024-2025 Alain Prasquier - Supervaize.com. All rights reserved.
#
# This Source Code Form is subject to the terms of the Mozilla Public License, v. 2.0.
# If a copy of the MPL was not distributed with this file, you can obtain one at
# https://mozilla.org/MPL/2.0/.

# This is an example file.
# It must be copied / renamed to supervaizer_control.py
# and edited to configure your agent(s)

import os

import shortuuid
from rich.console import Console
from supervaizer import (
    Agent,
    AgentMethod,
    AgentMethodField,
    AgentMethods,
    Case,
    CaseNodeUpdate,
    EntityStatus,
    JobContext,
    JobInstructions,
    JobResponse,
    Parameter,
    ParametersSetup,
    Server,
)
from supervaizer.account import Account

# Create a console with default style set to yellow
console = Console(style="yellow")

# Public url of your hosted agent  (including port if needed)
# Use loca.lt or ngrok to get a public url during development.
# This can be setup from environment variables.
# SUPERVAIZER_HOST and SUPERVAIZER_PORT
DEV_PUBLIC_URL = "https://myagent-dev.loca.lt"
# Public url of your hosted agent
PROD_PUBLIC_URL = os.getenv("SUPERVAIZE_PUBLIC_URL")

# Define the parameters and secrets expected by the agent
agent_parameters: ParametersSetup | None = ParametersSetup.from_list([
    Parameter(
        name="OPEN_API_KEY",
        description="OpenAPI Key",
        is_environment=True,
        is_secret=True,
    ),
    Parameter(
        name="AGENTMAIL_API_KEY",
        description="AgentMail API key - see https://agentmail.to",
        is_environment=True,
        is_secret=True,
    ),
    Parameter(
        name="AGENTMAIL_EMAIL",
        description="AgentMail email - see https://agentmail.to",
        is_environment=True,
        is_secret=False,
    ),
])

job_start_fields: list[AgentMethodField] = [
    AgentMethodField(
        name="Company to research",
        type=str,
        field_type="CharField",
        description="Company to research",
        default="Google",
        required=True,
    ),
    AgentMethodField(
        name="Max number of results",
        type=int,
        field_type="IntegerField",
        description="Max number of results",
        default=10,
        required=True,
    ),
    AgentMethodField(
        name="Subscribe to updates",
        type=bool,
        field_type="BooleanField",
        description="Subscribe to updates",
        default=False,
        required=False,
    ),
    AgentMethodField(
        name="Type of research",
        type=str,
        field_type="ChoiceField",
        description="Type of research",
        choices=[["A", "Advanced"], ["R", "Restricted"]],
        required=True,
    ),
    AgentMethodField(
        name="List of countries",
        type=list[str],
        field_type="MultipleChoiceField",
        description="List of countries",
        choices=[
            ["PA", "Panama"],
            ["PG", "Papua New Guinea"],
            ["PY", "Paraguay"],
            ["PE", "Peru"],
            ["PH", "Philippines"],
            ["PN", "Pitcairn"],
            ["PL", "Poland"],
        ],
        required=True,
    ),
    AgentMethodField(
        name="languages",
        type=list[str],
        field_type="MultipleChoiceField",
        description="languages",
        choices=[["en", "English"], ["fr", "French"], ["es", "Spanish"]],
        required=False,
    ),
    AgentMethodField(
        name="languages",
        type=list[str],
        field_type="MultipleChoiceField",
        description="languages",
        choices=[["en", "English"], ["fr", "French"], ["es", "Spanish"]],
        required=False,
    ),
]

job_start_method: AgentMethod = AgentMethod(
    name="start",  # This is required
    method="hello_world.job_start",  # Path to the main function in dotted notation.
    is_async=False,  # Only use sync methods for the moment
    params={"action": "start"},  # If default parameters must be passed to the function.
    fields=job_start_fields,
    description="Start the collection of new competitor summary",
)

job_stop_method: AgentMethod = AgentMethod(
    name="stop",
    method="control.stop",
    params={"action": "stop"},
    description="Stop the agent",
)
job_status_method: AgentMethod = AgentMethod(
    name="status",
    method="hello.mystatus",
    params={"status": "statusvalue"},
    description="Get the status of the agent",
)
custom_method: AgentMethod = AgentMethod(
    name="custom",
    method="control.custom",
    params={"action": "custom"},
    description="Custom method",
)

custom_method2: AgentMethod = AgentMethod(
    name="custom2",
    method="control.custom2",
    params={"action": "custom2"},
    description="Custom method",
)


agent_name = "Hello World AI Agent"

# Define the Agent
agent: Agent = Agent(
    name=agent_name,
    id=shortuuid.uuid(f"{agent_name}"),
    author="Alain Prasquier <al1@supervaize.com>",  # Author of the agent
    developer="Alain Prasquier <al1@supervaize.com>",  # Developer of the controller integration
    maintainer="Alain Prasquier <al1@supervaize.com>",  # Maintainer of the integration
    editor="Alain Prasquier <al1@supervaize.com>",  # Editor (usually a company)
    version="1.0",  # Version string
    description="This is a test agent",
    tags=["hello world", "ai agent"],
    methods=AgentMethods(
        job_start=job_start_method,
        job_stop=job_stop_method,
        job_status=job_status_method,
        chat=None,
        custom={"custom1": custom_method, "custom2": custom_method2},
    ),
    parameters_setup=agent_parameters,
    instructions_path="supervaize_instructions.html",  # Path where instructions page is served
)

# For export purposes, use dummy values if environment variables are not set
account: Account = Account(
    workspace_id=os.getenv("SUPERVAIZE_WORKSPACE_ID") or "dummy_workspace_id",
    api_key=os.getenv("SUPERVAIZE_API_KEY") or "dummy_api_key",
    api_url=os.getenv("SUPERVAIZE_API_URL") or "https://app.supervaize.com",
)

# Define the supervaizer server capabilities
sv_server: Server = Server(
    agents=[agent],
    a2a_endpoints=True,  # Enable A2A endpoints
    supervisor_account=account,  # Account of the supervisor from Supervaize
)


# Expose the FastAPI app instance for deployment
app = sv_server.app


# Custom method to start a synchronous job.
def job_start(**kwargs) -> JobResponse:
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

    console.print(f"AGENT ExampleAgent: Starting Job [blue]{job_id}[/blue] ")
    console.print(f"AGENT ExampleAgent: Job Fields : {job_fields}")
    console.print(f"AGENT ExampleAgent: Job Instructions : {job_instructions}")

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
                console.print(
                    f"AGENT ExampleAgent: [red]Error on case {case_id}: {e}[/red]"
                )
                if job_instructions and job_instructions.stop_on_error:
                    console.print(
                        f"AGENT ExampleAgent: [red]STOPPING JOB ON ERROR: {e}[/red]"
                    )
                    raise Exception(e)
                else:
                    console.print(
                        "AGENT ExampleAgent: CONTINUING JOB - stop_on_error is False"
                    )
        else:
            console.print(
                f"AGENT ExampleAgent: [orange]STOPPING JOB: {explanation}[/orange]"
            )
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

    console.print(
        f"AGENT ExampleAgent: Job [blue]{job_id}[/blue] completed   - Total cost: {cost} -> {res}"
    )

    return res


def custom_case_start(case_id: str, job_id: str, **kwargs):
    console.print(
        f"AGENT ExampleAgent: Starting Case [blue]{case_id}[/blue] with params: {kwargs}"
    )
    print(
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
        nodes=nodes,
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

    console.print(f"AGENT ExampleAgent: Case id {case_id} finished")
    return case


def resume_case_with_human_input(case_id: str, job_id: str, **kwargs):
    case = Case.resume(id=case_id, job_id=job_id, account=supervaize_account)

    case.close()
    return


def email_agent(supervaize_account: Account, agent_name="Email Agent") -> Agent:
    """
    Define the Agent
    """
    return Agent(
        name=agent_name,
        id=shortuuid.uuid(f"{agent_name}"),
        author="Alain Prasquier <al1@supervaize.com>",  # Author of the agent
        developer="Alain Prasquier <al1@supervaize.com>",  # Developer of the controller integration
        maintainer="Alain Prasquier <al1@supervaize.com>",  # Maintainer of the integration
        editor="Alain Prasquier <al1@supervaize.com>",  # Editor (usually a company)
        version="1.0",  # Version string
        description="This is a test agent",
        tags=["hello world", "ai agent"],
        methods=AgentMethods(
            job_start=job_start_method(supervaize_account=supervaize_account),
            job_stop=job_start_method(supervaize_account=supervaize_account),
            job_status=job_start_method(supervaize_account=supervaize_account),
            chat=None,
            custom={
                "custom1": custom_method(supervaize_account=supervaize_account),
                "custom2": custom_method2(supervaize_account=supervaize_account),
            },
        ),
        parameters_setup=agent_parameters,
        instructions_path="supervaize_instructions.html",  # Path where instructions page is served
    )
