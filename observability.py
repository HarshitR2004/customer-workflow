"""
Observability and execution logging module for the AI Customer Support Workflow.

Features:
- Neatlogs cloud observability integration with neatlogs.langchain_handler()
- Local JSON and JSONL execution telemetry logging
- Real-time token usage and latency tracking via LangChain callbacks
- API key masking to prevent leaking secrets in logs or terminal
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult

# Default neatlogs credentials (fallback if not in environment)
DEFAULT_NEATLOGS_API_KEY = "qlandigNwgrvCTBGuLb2xRIpRQQBtpTw"
DEFAULT_NEATLOGS_ENDPOINT = "https://ingest.neatlogs.com"
DEFAULT_NEATLOGS_WORKFLOW = "demo-workflow"


def mask_api_key(key: Optional[str]) -> str:
    """Mask sensitive API keys for safe logging and terminal output."""
    if not key:
        return "[NOT SET]"
    key_str = str(key).strip()
    if len(key_str) <= 8:
        return "****"
    return f"{key_str[:4]}...{key_str[-4:]}"


class WorkflowMetricsCallback(BaseCallbackHandler):
    """
    LangChain callback handler that records real execution metrics
    (exact token usage and elapsed latency) for each workflow step.
    """

    def __init__(self):
        super().__init__()
        self.current_step_name: str = ""
        self.current_step_index: int = 0
        self.step_start_time: float = 0.0
        self.steps: List[Dict[str, Any]] = []
        self._last_token_usage: Dict[str, int] = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    def start_step(self, step_index: int, step_name: str):
        """Mark the beginning of a step before invoking its chain."""
        self.current_step_index = step_index
        self.current_step_name = step_name
        self.step_start_time = time.perf_counter()
        self._last_token_usage = {
            "input_tokens": 0,
            "output_tokens": 0,
            "total_tokens": 0,
        }

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Capture real token consumption reported by the LLM provider."""
        input_tokens = 0
        output_tokens = 0
        total_tokens = 0

        # Method 1: Check generation message usage_metadata (standard in modern LangChain)
        if response.generations:
            for gen_list in response.generations:
                for gen in gen_list:
                    msg = getattr(gen, "message", None)
                    if msg and hasattr(msg, "usage_metadata") and msg.usage_metadata:
                        usage = msg.usage_metadata
                        input_tokens += usage.get("input_tokens", 0)
                        output_tokens += usage.get("output_tokens", 0)
                        total_tokens += usage.get("total_tokens", 0)

        # Method 2: Check llm_output['token_usage'] (e.g. OpenAI provider)
        if total_tokens == 0 and response.llm_output and "token_usage" in response.llm_output:
            usage = response.llm_output["token_usage"]
            input_tokens = usage.get("prompt_tokens", 0)
            output_tokens = usage.get("completion_tokens", 0)
            total_tokens = usage.get("total_tokens", 0)

        self._last_token_usage = {
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "total_tokens": total_tokens or (input_tokens + output_tokens),
        }

    def complete_step(
        self,
        output_text: str,
        status: str = "SUCCESS",
        error_msg: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Record step completion with metrics."""
        elapsed_seconds = round(time.perf_counter() - self.step_start_time, 3)

        step_record = {
            "step_index": self.current_step_index,
            "step_name": self.current_step_name,
            "timestamp": datetime.now().isoformat(),
            "latency_seconds": elapsed_seconds,
            "input_tokens": self._last_token_usage["input_tokens"],
            "output_tokens": self._last_token_usage["output_tokens"],
            "total_tokens": self._last_token_usage["total_tokens"],
            "status": status,
            "error": error_msg,
            "output_snippet": (output_text[:120] + "...") if len(output_text) > 120 else output_text,
        }
        self.steps.append(step_record)
        return step_record

    def get_aggregate_summary(self) -> Dict[str, Any]:
        """Compute aggregate workflow metrics across all executed steps."""
        total_latency = sum(s["latency_seconds"] for s in self.steps)
        total_input_tokens = sum(s["input_tokens"] for s in self.steps)
        total_output_tokens = sum(s["output_tokens"] for s in self.steps)
        total_tokens = sum(s["total_tokens"] for s in self.steps)

        return {
            "total_steps": len(self.steps),
            "total_latency_seconds": round(total_latency, 3),
            "total_input_tokens": total_input_tokens,
            "total_output_tokens": total_output_tokens,
            "total_tokens": total_tokens,
            "steps": self.steps,
        }


def setup_neatlogs(
    api_key: Optional[str] = None,
    endpoint: Optional[str] = None,
    workflow_name: Optional[str] = None,
) -> Optional[Any]:
    """
    Initialize Neatlogs cloud observability and return the LangChain callback handler.
    Falls back gracefully if Neatlogs encounters a connection issue.
    """
    key = api_key or os.getenv("NEATLOGS_API_KEY", DEFAULT_NEATLOGS_API_KEY)
    ep = endpoint or os.getenv("NEATLOGS_ENDPOINT", DEFAULT_NEATLOGS_ENDPOINT)
    wf = workflow_name or os.getenv("NEATLOGS_WORKFLOW_NAME", DEFAULT_NEATLOGS_WORKFLOW)

    try:
        import neatlogs

        neatlogs.init(
            api_key=key,
            endpoint=ep,
            workflow_name=wf,
        )
        handler = neatlogs.langchain_handler()
        return handler
    except Exception as e:
        print(f"[Observability Warning] Could not initialize Neatlogs ({type(e).__name__}: {e}). Continuing with local logging.")
        return None


def flush_neatlogs():
    """Flush pending Neatlogs events if available."""
    try:
        import neatlogs

        neatlogs.flush()
    except Exception:
        pass


def save_execution_log(
    run_record: Dict[str, Any],
    log_dir: str = "logs",
) -> str:
    """
    Save execution run record to both a persistent JSONL audit log
    and an individual JSON run file.
    """
    os.makedirs(log_dir, exist_ok=True)

    # 1. Append to workflow_runs.jsonl
    jsonl_path = os.path.join(log_dir, "workflow_runs.jsonl")
    with open(jsonl_path, "a", encoding="utf-8") as f:
        f.write(json.dumps(run_record, ensure_ascii=False) + "\n")

    # 2. Write individual run snapshot
    run_id = run_record.get("run_id", int(time.time()))
    ticket_id = run_record.get("ticket_id", "custom")
    run_json_path = os.path.join(log_dir, f"run_{run_id}_{ticket_id}.json")
    with open(run_json_path, "w", encoding="utf-8") as f:
        json.dump(run_record, f, indent=2, ensure_ascii=False)

    return jsonl_path
