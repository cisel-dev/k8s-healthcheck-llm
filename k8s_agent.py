from langchain_openai.chat_models import ChatOpenAI
from langchain.schema import HumanMessage, SystemMessage, AIMessage
import subprocess
import shlex
import urllib3

# Disable warnings for unverified certificates
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

KUBECONFIG = "/path/to/your/kubeconfig-file"

# Step 1: Function to execute kubectl commands with error handling
def execute_kubectl_command(command):
    """
    Executes a kubectl command and returns the result.

    Args:
        command (str): The kubectl command to execute.

    Returns:
        tuple: (stdout, stderr, success), where success is a boolean indicating if the command succeeded.
    """
    try:
        print(f"\n[DEBUG] Executing command: {command}\n")
        command_args = shlex.split(command)
        result = subprocess.run(command_args, capture_output=True, text=True)

        stdout = result.stdout.strip()
        stderr = result.stderr.strip()

        if result.returncode != 0:
            return stdout, stderr, False
        return stdout, stderr, True

    except FileNotFoundError as e:
        return "", f"Error: Command not found: {str(e)}", False
    except Exception as e:
        return "", f"Error while executing command: {str(e)}", False

# Step 2: Interaction with the LLM to determine which commands to execute
def interact_with_llm():
    """
    Handles interaction with the LLM to generate commands, interpret responses, and synthesize findings.
    
    Returns:
        list: A list of executed commands for tracking.
    """
    # Initialize the LLM
    llm = ChatOpenAI(model="gpt-3.5-turbo", temperature=0)

    # System message defining the LLM's task and goals
    system_message = SystemMessage(
        content=(
            "You are a Kubernetes expert assistant tasked with diagnosing a Kubernetes cluster.\n"
            "Your mission is to provide a thorough analysis of the Kubernetes cluster state, identify all critical anomalies, "
            "and propose detailed and actionable solutions to resolve them.\n\n"
            "### Your Objectives:\n"
            "1. **Identify critical anomalies**:\n"
            "   - Analyze all cluster pods to detect those in problematic states (`CrashLoopBackOff`, `Failed`, `Pending`).\n"
            "   - Prioritize analyzing problematic pods by severity.\n"
            "   - **Each problematic pod must be analyzed and resolved before moving to the next one.**\n"
            "2. **Perform a comprehensive diagnosis of problematic pods**:\n"
            "   - Retrieve pod logs to identify failure causes.\n"
            "   - Examine associated events using `kubectl describe pod` to identify potential issues.\n"
            "   - Check critical dependencies such as ConfigMaps, Secrets, Volumes, and Services.\n"
            "3. **Validate overall cluster health**:\n"
            "   - Check node status to detect resource-related issues (CPU, memory, storage).\n"
            "   - Identify global cluster errors using commands like `kubectl get events`.\n"
            "4. **Synthesize findings and recommendations**:\n"
            "   - Provide a clear table summarizing detected anomalies with the following columns:\n"
            "     - Pod Name\n"
            "     - Namespace\n"
            "     - Status (e.g., CrashLoopBackOff, Failed)\n"
            "     - Cause Identified\n"
            "     - Solution Proposed\n"
            "   - Prioritize recommendations to address the most critical issues first.\n"
            "   - Ensure the table is well-structured and includes actionable insights.\n\n"
            "### Constraints:\n"
            "- **All commands must include**: `--kubeconfig=/path/to/your/kubeconfig-file` and `--insecure-skip-tls-verify`.\n"
            "- **Avoid repeating commands** unless new information justifies re-execution.\n"
            "- If a command fails, analyze the error and propose a realistic alternative.\n"
            "- Avoid focusing entirely on a single recurring issue unless it blocks the entire diagnosis.\n\n"
            "### Workflow:\n"
            "1. **List problematic pods**:\n"
            "   - Start by identifying all pods in problematic states (`CrashLoopBackOff`, `Failed`, `Pending`).\n"
            "   - Filter the results to avoid non-problematic states (`Completed`, `Running`).\n"
            "2. **Analyze each problematic pod**:\n"
            "   - For each pod:\n"
            "     - Retrieve its logs.\n"
            "     - Examine associated events via `kubectl describe pod`.\n"
            "     - Check dependencies like volumes, secrets, and ConfigMaps.\n"
            "   - Document findings step-by-step to construct an actionable analysis.\n"
            "3. **Generate a detailed synthesis**:\n"
            "   - Summarize findings into a table with columns for Pod Name, Namespace, Status, Cause, and Solution.\n"
            "   - Provide actionable recommendations prioritized by urgency.\n"
            "4. **Iterate until no problematic pods remain**:\n"
            "   - Once all pods are analyzed, ensure no unresolved issues remain.\n\n"
            "### Example Output:\n"
            "| Pod Name          | Namespace   | Status           | Cause Identified     | Solution Proposed                      |\n"
            "|-------------------|-------------|------------------|----------------------|---------------------------------------|\n"
            "| my-pod-1          | default     | CrashLoopBackOff | Missing ConfigMap    | Add the required ConfigMap             |\n"
            "| my-pod-2          | kube-system | Pending          | Node resource issue  | Allocate more resources to the cluster |\n"
            "\nProvide the table in plain text markdown format."
        )
    )

    # Initialize interaction
    human_message = HumanMessage(content="Start Kubernetes diagnostics. Propose a kubectl command to execute.")
    messages = [system_message, human_message]
    executed_commands = []
    anomalies = []

    # Loop to interact with the LLM
    while True:
        response = llm.invoke(messages)
        llm_output = response.content.strip()
        print(f"\n[DEBUG] LLM Proposes: {llm_output}\n")

        # Check if the LLM output contains a kubectl command
        if "kubectl" in llm_output:
            command = next((line for line in llm_output.split("\n") if line.startswith("kubectl")), None)
            if command and command not in executed_commands:
                stdout, stderr, success = execute_kubectl_command(command)
                executed_commands.append(command)
                if success:
                    messages.append(HumanMessage(content=f"Command executed successfully. Result:\n{stdout}"))
                else:
                    messages.append(HumanMessage(content=f"Command failed. Error:\n{stderr}"))
            else:
                print("[DEBUG] Command already executed or invalid.")
        elif "table" in llm_output.lower() and "|" in llm_output:
            # If the output contains a markdown table, assume it's the synthesis
            print("\n--- Final Synthesis Generated by LLM ---\n")
            print(llm_output)
            break
        else:
            print("[DEBUG] No new commands or synthesis proposed. Ending interaction.")
            break

    return executed_commands

# Step 3: Orchestrate the workflow
def monitor_kubernetes():
    """
    Main orchestration function for Kubernetes health checks.
    """
    print("\n--- Starting Kubernetes Dynamic HealthCheck ---\n")
    executed_commands = interact_with_llm()

    print("\n--- Executed Commands ---\n")
    for cmd in executed_commands:
        print(f"{cmd}: Success" if cmd else "Failed")

    print("\n--- HealthCheck Completed ---\n")

# Main entry point
if __name__ == "__main__":
    monitor_kubernetes()
