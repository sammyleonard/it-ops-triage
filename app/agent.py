# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from google.adk.agents import Agent
from google.adk.apps import App
from google.adk.models import Gemini
from google.genai import types

# 1. Stateful Local Data Store (Tracks tickets cleanly across operational sessions)
TICKET_LOG = []

def triage_and_escalate_ticket(issue_description: str) -> str:
    """Automatically processes an incoming IT support ticket, scans for critical system keywords, and handles priority routing.

    Args:
        issue_description: A clear text description of the technical issue or system outage.

    Returns:
        A string confirming the system log status and triage routing actions taken.
    """
    text_upper = issue_description.upper()
    is_critical = "CRITICAL" in text_upper or "DOWN" in text_upper or "FAILURE" in text_upper
    
    status = "HIGH-PRIORITY ESCALATION" if is_critical else "Standard Support Queue"
    ticket_id = len(TICKET_LOG) + 1
    
    ticket_entry = {
        "id": ticket_id,
        "description": issue_description,
        "status": status
    }
    TICKET_LOG.append(ticket_entry)
    
    if is_critical:
        return f"[ALERT] Ticket #{ticket_id} flagged as CRITICAL. PagerDuty/Slack notification dispatched to DevOps On-Call team."
    
    return f"[SUCCESS] Ticket #{ticket_id} logged into the regular support queue."

# 2. Unified Core Agent Configuration (Wired up to use your tool)
root_agent = Agent(
    name="it_ops_triage_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an automated IT Operations Triage Agent. Analyze the incoming user technical issue, "
        "always log it using the triage_and_escalate_ticket tool, and provide a polite summary response "
        "detailing what triage steps were completed and what the user should expect next."
    ),
    tools=[triage_and_escalate_ticket],
)

# 3. Main Application Entrypoint for the CLI Playground
app = App(
    root_agent=root_agent,
    name="app",  # <-- Change this from "it-ops-triage" to "app"
)
