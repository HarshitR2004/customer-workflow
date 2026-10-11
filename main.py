"""
CLI Entry Point for the Deliberately Inefficient AI Customer Support Workflow.

Usage:
  python main.py --demo                     Run sample ticket #1 through all 6 sequential steps
  python main.py --ticket-id 2              Run a specific sample ticket (1 through 5)
  python main.py --ticket "My message"      Run a custom support ticket
  python main.py --all                      Run all sample tickets sequentially
  python main.py --provider ollama          Select LLM provider ('ollama' or 'openai')
  python main.py --model lfm2.5:8b          Override model name
"""

import sys
import os
import argparse
from typing import Dict, Any, Optional

# Ensure UTF-8 console output on Windows to prevent charmap encoding errors
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
        sys.stderr.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# Load environment variables from .env if present
try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

from mock_data import SAMPLE_TICKETS, extract_order_id_from_text
from workflow import CustomerSupportWorkflow, WorkflowExecutionError
from observability import mask_api_key


def format_step_banner(step_num: int, total_steps: int, step_name: str) -> str:
    line = "=" * 70
    return f"\n{line}\n[STEP {step_num}/{total_steps}] {step_name.upper()}\n{line}"


def safe_terminal_str(s: str) -> str:
    """Safely sanitize text for terminal output under Windows codepages."""
    try:
        encoding = sys.stdout.encoding or "utf-8"
        return s.encode(encoding, errors="replace").decode(encoding)
    except Exception:
        return s.encode("ascii", errors="replace").decode("ascii")


def step_progress_callback(phase: str, step_num: int, step_name: str, step_record: Optional[Dict[str, Any]] = None, output_text: str = ""):
    """Pretty terminal callback to show step execution and real metrics."""
    if phase == "start":
        print(f"\n--> Running Step {step_num}/6: {step_name}...")
    elif phase == "end" and step_record:
        latency = step_record.get("latency_seconds", 0.0)
        in_tok = step_record.get("input_tokens", 0)
        out_tok = step_record.get("output_tokens", 0)
        tot_tok = step_record.get("total_tokens", 0)

        # Print output preview safely
        clean_preview = safe_terminal_str(output_text.strip())
        if len(clean_preview) > 300:
            preview_str = clean_preview[:280] + "\n    [...truncated in preview...]"
        else:
            preview_str = clean_preview

        print(f"    Result Preview:\n    {preview_str}")
        print(f"    [Metrics] Latency: {latency:.2f}s | Tokens: In={in_tok}, Out={out_tok}, Total={tot_tok}")


def print_workflow_summary_table(result: Dict[str, Any]):
    """Print an ASCII summary table detailing per-step tokens and execution time."""
    metrics = result.get("metrics", {})
    steps = metrics.get("steps", [])

    print("\n" + "=" * 75)
    print("                     EXECUTION BENCHMARK SUMMARY")
    print("=" * 75)
    print(f" Ticket ID: {result.get('ticket_id')} | Provider: {result.get('provider')} | Model: {result.get('model_name')}")
    print("-" * 75)
    print(f"{'Step Name':<32} {'Latency':>10} {'Prompt Tok':>12} {'Output Tok':>12} {'Total Tok':>12}")
    print("-" * 75)

    for s in steps:
        name = s.get("step_name", "")
        # Shorten for table
        if ":" in name:
            name = name.split(":", 1)[1].strip()
        latency_str = f"{s.get('latency_seconds', 0.0):.2f}s"
        in_tok = s.get("input_tokens", 0)
        out_tok = s.get("output_tokens", 0)
        tot_tok = s.get("total_tokens", 0)
        print(f"{name:<32} {latency_str:>10} {in_tok:>12} {out_tok:>12} {tot_tok:>12}")

    print("-" * 75)
    tot_latency = f"{metrics.get('total_latency_seconds', 0.0):.2f}s"
    tot_in = metrics.get("total_input_tokens", 0)
    tot_out = metrics.get("total_output_tokens", 0)
    grand_total = metrics.get("total_tokens", 0)
    print(f"{'TOTALS (6 Sequential Calls)':<32} {tot_latency:>10} {tot_in:>12} {tot_out:>12} {grand_total:>12}")
    print("=" * 75)

    print("\n[AI FinOps Inefficiency Audit]")
    print(" 1. Sequential Calls    : 6 separate LLM calls executed (classification, sentiment, urgency, draft, review, rewrite)")
    print(f" 2. Uniform Model Size  : Massive model ({result.get('model_name')}) used even for simple 1-word classification")
    print(" 3. Redundant Context   : Re-passed previous outputs repeatedly across steps")
    print(" 4. Uncompressed KB     : Entire DemoShop policy manual injected into Step 4 prompt without RAG")
    print(" 5. Obligatory Rewriting: Mandatory QA review and rewrite invoked regardless of initial draft quality")
    print(" 6. Zero Caching        : No response caching, prompt caching, or parallel batching applied")
    if "log_file" in result:
        print(f"\n[Audit Log Saved] -> {result['log_file']}")


def print_final_response(result: Dict[str, Any]):
    """Display the final customer support response clearly."""
    final_text = safe_terminal_str(result.get("final_response", ""))
    print("\n" + "#" * 75)
    print("                  FINAL DELIVERED CUSTOMER RESPONSE")
    print("#" * 75)
    print(f"\n{final_text}\n")
    print("#" * 75)


def run_single_ticket(workflow: CustomerSupportWorkflow, ticket: Dict[str, Any]):
    """Execute a single ticket through the workflow with rich terminal logging."""
    print("\n" + "#" * 75)
    print(f" STARTING TICKET EXECUTION: {ticket.get('id', 'CUSTOM')} - {ticket.get('title', 'Support Request')}")
    print("#" * 75)
    print(f"Customer Query:\n\"{ticket['text']}\"\n")

    try:
        result = workflow.run(
            ticket_text=ticket["text"],
            ticket_id=ticket.get("id", "CUSTOM"),
            explicit_order_id=ticket.get("order_id"),
            verbose_callback=step_progress_callback,
        )
        print_final_response(result)
        print_workflow_summary_table(result)
    except WorkflowExecutionError as e:
        print(f"\n[ERROR] Workflow failed gracefully: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\n[ABORTED] Workflow execution stopped by user.")
        sys.exit(130)
    except Exception as e:
        print(f"\n[UNEXPECTED ERROR] An unhandled error occurred: {type(e).__name__}: {e}")
        sys.exit(1)


def main():
    parser = argparse.ArgumentParser(
        description="Deliberately Inefficient AI Customer Support Workflow (LangChain Baseline)",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--demo",
        action="store_true",
        help="Run the primary demo customer support ticket (Order #12345 delayed headphones)",
    )
    group.add_argument(
        "--ticket",
        type=str,
        help="Custom customer support ticket text to process",
    )
    group.add_argument(
        "--ticket-id",
        type=int,
        choices=[1, 2, 3, 4, 5],
        help="Run a specific sample ticket by number (1 to 5)",
    )
    group.add_argument(
        "--all",
        action="store_true",
        help="Run all 5 sample tickets sequentially (Warning: higher token and time consumption)",
    )

    parser.add_argument(
        "--provider",
        type=str,
        choices=["ollama", "openai"],
        default=None,
        help="LLM provider: 'ollama' (default, local) or 'openai'",
    )
    parser.add_argument(
        "--model",
        type=str,
        default=None,
        help="Model name (e.g. 'lfm2.5:8b' for ollama or 'gpt-4o' for openai)",
    )
    parser.add_argument(
        "--no-neatlogs",
        action="store_true",
        help="Disable Neatlogs remote telemetry export",
    )

    args = parser.parse_args()

    # If no argument is provided, default to --demo to run exactly one ticket
    if not (args.demo or args.ticket or args.ticket_id or args.all):
        print("[Notice] No ticket option specified. Defaulting to --demo (Ticket 1).")
        args.demo = True

    # Initialize workflow
    try:
        workflow = CustomerSupportWorkflow(
            provider=args.provider,
            model_name=args.model,
            enable_neatlogs=not args.no_neatlogs,
        )
    except Exception as e:
        print(f"\n[INITIALIZATION ERROR] Could not initialize workflow: {e}")
        sys.exit(1)

    print("===========================================================================")
    print("   DEMOSHOP DELIBERATELY INEFFICIENT AI CUSTOMER SUPPORT WORKFLOW")
    print("===========================================================================")
    print(f" LLM Provider   : {workflow.provider.upper()}")
    print(f" Configured Model: {workflow.model_name}")
    print(f" Neatlogs Status: {'Enabled' if workflow.neatlogs_handler else 'Disabled / Local Only'}")
    neatlogs_key = os.getenv("NEATLOGS_API_KEY")
    if neatlogs_key:
        print(f" Neatlogs API Key: {mask_api_key(neatlogs_key)}")
    print("===========================================================================")

    if args.demo:
        run_single_ticket(workflow, SAMPLE_TICKETS[0])

    elif args.ticket_id:
        idx = args.ticket_id - 1
        run_single_ticket(workflow, SAMPLE_TICKETS[idx])

    elif args.ticket:
        detected_order = extract_order_id_from_text(args.ticket)
        custom_ticket = {
            "id": "CUSTOM-1",
            "title": "Custom User Ticket",
            "order_id": detected_order,
            "text": args.ticket,
        }
        run_single_ticket(workflow, custom_ticket)

    elif args.all:
        print(f"\nExecuting all {len(SAMPLE_TICKETS)} sample tickets sequentially...")
        for i, t in enumerate(SAMPLE_TICKETS, 1):
            print(f"\n>>> Running Ticket {i}/{len(SAMPLE_TICKETS)}: {t['id']} <<<")
            run_single_ticket(workflow, t)


if __name__ == "__main__":
    main()
