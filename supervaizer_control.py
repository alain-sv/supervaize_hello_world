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
    AgentMethods,
    AgentMethodField,
    Parameter,
    ParametersSetup,
    Server,
)
from supervaizer.account import Account
from supervaizer.__version__ import API_VERSION, VERSION

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
        name="Details of research",
        type=str,
        field_type="CharField",
        description="Details of research",
        default="",
        required=False,
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


@app.get("/api/context")
def api_context() -> dict:
    """Return context for the home page (version, base URLs, show_admin)."""
    base = sv_server.public_url or f"{sv_server.scheme}://{sv_server.host}:{sv_server.port}"
    return {
        "version": VERSION,
        "api_version": API_VERSION,
        "base": base,
        "public_url": sv_server.public_url or base,
        "full_url": f"{sv_server.scheme}://{sv_server.host}:{sv_server.port}",
        "show_admin": bool(sv_server.api_key),
    }


if __name__ == "__main__":
    # Start the supervaize server
    sv_server.launch(log_level="DEBUG", start_uvicorn=True)
