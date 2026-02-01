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
    AgentMethods,
    Server,
    Account,
    AgentMethod,
    AgentMethodField,
    ParametersSetup,
    Parameter,
)

console = Console(style="yellow")

#### SIMPLE AGENT ####
agent_name = "Hello World AI Agent"

# Define the parameters and secrets expected by the agent
simple_agent_parameters = ParametersSetup.from_list([
    Parameter(
        name="SIMPLE AGENT PARAMETER",
        description="Setup agent parameter in this workspace",
        is_environment=True,
    ),
    Parameter(
        name="SIMPLE AGENT SECRET",
        description="Setup agent secret in this workspace",
        is_environment=True,
        is_secret=True,
    ),
])


# Define the start method for the agent
job_start_method = AgentMethod(
    name="start",
    method="simple_agent.job_start",
    is_async=False,
    params={"action": "start"},
    fields=[
        AgentMethodField(
            name="How many times to say hello",
            type=int,
            field_type="IntegerField",
            required=True,
        )
    ],
)
# Define the Agent
simple_agent: Agent = Agent(
    name=agent_name,
    id=shortuuid.uuid(f"{agent_name}"),
    author="Alain Prasquier <al1@supervaize.com>",  # Author of the agent
    version="1.0",  # Version string
    description="This is a test agent",
    tags=["hello world", "ai agent"],
    methods=AgentMethods(
        job_start=job_start_method,
    ),
    parameters_setup=simple_agent_parameters,
)


# Always provide a default value to prevent error.
# Get from app.supervaize.com
supervaize_account: Account = Account(
    workspace_id=os.getenv("SUPERVAIZE_WORKSPACE_ID") or "dummy_workspace_id",
    api_key=os.getenv("SUPERVAIZE_API_KEY") or "dummy_api_key",
    api_url=os.getenv("SUPERVAIZE_API_URL") or "https://app.supervaize.com",
)

# Define the supervaizer server capabilities
sv_server: Server = Server(
    agents=[simple_agent],  # [simple_agent, email_agent]
    a2a_endpoints=True,  # Enable A2A endpoints
    supervisor_account=supervaize_account,  # Account from Supervaize
)


# Expose the FastAPI app instance for deployment
app = sv_server.app


if __name__ == "__main__":
    # Start the supervaize server
    sv_server.launch(log_level="DEBUG")
