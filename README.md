## **1. Prerequisites**

### **Required Software and Environments**
1. **Python 3.10+**:
   - Ensure that Python 3.10 or a later version is installed.
   - Check your Python version:
     ```bash
     python3 --version
     ```

2. **Kubernetes Access**:
   - You need a valid kubeconfig file with the necessary permissions to interact with your Kubernetes cluster.
   - By default, the script uses the file `~/.kube/config`. If you use another file, set it via the `KUBECONFIG` environment variable:
     ```bash
     export KUBECONFIG=/path/to/your/kubeconfig-file
     ```

3. **OpenAI API Access**:
   - Set up your OpenAI API key in an environment variable named `OPENAI_API_KEY`:
     ```bash
     export OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
     ```

---

## **2. Installing Dependencies**

- **Step 1**: Create a Python virtual environment (optional but recommended):
  ```bash
  python3 -m venv env
  source env/bin/activate
  pip install -r requirements.txt
  ```

---

## **3. Usage**

1. **Run the Script**:
   - Execute the script to start the dynamic Kubernetes diagnostic process:
     ```bash
     python k8s_agent.py
     ```

2. **Script Output**:
   - **LLM Suggestions**: The model will propose `kubectl` commands to analyze the cluster's state.
   - **Automatic Execution**: Proposed commands will be executed automatically, and the results will be displayed in real-time.
   - **Problem Summary**: At the end, a summary table will show the executed commands and the detected issues.

3. **Summary Table**:
   - Upon completion, a table will be generated summarizing the executed commands and identified issues.
