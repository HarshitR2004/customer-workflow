"""
Six-Step Sequential AI Customer Support Workflow built with LangChain.

This workflow intentionally implements architectural inefficiencies to serve as
a baseline benchmark for AI FinOps analysis:
1. Exactly six sequential, single-purpose LLM API calls.
2. The same general-purpose model is used for all steps, even 1-token classification.
3. Repetitive context passing between steps.
4. Entire unindexed DemoShop knowledge base injected into Step 4.
5. Unconditional review and rewrite steps on every execution.
6. Zero caching, zero batching, zero model routing.
"""

import os
import re
from typing import Dict, Any, Optional
from langchain_core.output_parsers import StrOutputParser

from prompts import (
    CLASSIFICATION_PROMPT,
    SENTIMENT_PROMPT,
    URGENCY_PROMPT,
    RESPONSE_GENERATION_PROMPT,
    REVIEW_PROMPT,
    REWRITE_PROMPT,
)
from mock_data import (
    DEMOSHOP_KNOWLEDGE_BASE,
    extract_order_id_from_text,
    get_mock_order,
    format_order_details,
)
from observability import (
    WorkflowMetricsCallback,
    setup_neatlogs,
    flush_neatlogs,
    save_execution_log,
)


class WorkflowExecutionError(Exception):
    """Custom exception raised when a workflow step encounters an error."""
    pass


def clean_llm_output(raw_text: str) -> str:
    """
    Strips internal reasoning/thinking blocks (e.g. <think>...</think> from reasoning models)
    so downstream steps receive clean text, while preserving accurate token measurements.
    """
    if not isinstance(raw_text, str):
        raw_text = str(raw_text)
    # Remove closed thinking tags
    cleaned = re.sub(r"<think>.*?</think>", "", raw_text, flags=re.DOTALL).strip()
    # Remove unclosed thinking tag if model truncated mid-thought
    if "<think>" in cleaned and "</think>" not in cleaned:
        parts = cleaned.split("<think>", 1)
        cleaned = parts[0].strip() or parts[1].strip()
    return cleaned if cleaned else raw_text.strip()


def build_llm(
    provider: Optional[str] = None,
    model_name: Optional[str] = None,
    temperature: float = 0.2,
):
    """
    Construct the configurable LangChain LLM instance.
    Supports local Ollama (defaulting to 'lfm2.5:8b') or OpenAI (defaulting to 'gpt-4o').
    """
    chosen_provider = (
        provider
        or os.getenv("LLM_PROVIDER")
        or "ollama"
    ).lower().strip()

    if chosen_provider == "openai":
        from langchain_openai import ChatOpenAI

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise WorkflowExecutionError(
                "OpenAI provider selected, but OPENAI_API_KEY is not set in environment or .env file."
            )
        chosen_model = model_name or os.getenv("OPENAI_MODEL", "gpt-4o")
        return ChatOpenAI(
            model=chosen_model,
            temperature=temperature,
            api_key=api_key,
        ), "openai", chosen_model

    else:
        # Default: Local Ollama
        from langchain_ollama import ChatOllama

        chosen_model = model_name or os.getenv("OLLAMA_MODEL", "lfm2.5:8b")
        base_url = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")

        return ChatOllama(
            model=chosen_model,
            base_url=base_url,
            temperature=temperature,
        ), "ollama", chosen_model


class CustomerSupportWorkflow:
    """
    Executes the 6-step deliberately inefficient LangChain customer support workflow.
    """

    def __init__(
        self,
        provider: Optional[str] = None,
        model_name: Optional[str] = None,
        enable_neatlogs: bool = True,
    ):
        self.llm, self.provider, self.model_name = build_llm(provider, model_name)
        self.parser = StrOutputParser()
        self.neatlogs_handler = setup_neatlogs() if enable_neatlogs else None

        # Build the six individual sequential chains
        self.classification_chain = CLASSIFICATION_PROMPT | self.llm | self.parser
        self.sentiment_chain = SENTIMENT_PROMPT | self.llm | self.parser
        self.urgency_chain = URGENCY_PROMPT | self.llm | self.parser
        self.response_chain = RESPONSE_GENERATION_PROMPT | self.llm | self.parser
        self.review_chain = REVIEW_PROMPT | self.llm | self.parser
        self.rewrite_chain = REWRITE_PROMPT | self.llm | self.parser

    def _get_callbacks(self, metrics_cb: WorkflowMetricsCallback):
        """Assemble active callbacks for chain invocation."""
        callbacks = [metrics_cb]
        if self.neatlogs_handler:
            callbacks.append(self.neatlogs_handler)
        return callbacks

    def _notify(self, cb: Optional[Any], *args):
        """Safely invoke verbose progress callback without interrupting execution."""
        if cb:
            try:
                cb(*args)
            except Exception:
                pass

    def run(
        self,
        ticket_text: str,
        ticket_id: str = "CUSTOM",
        explicit_order_id: Optional[str] = None,
        log_dir: str = "logs",
        verbose_callback: Optional[Any] = None,
    ) -> Dict[str, Any]:
        """
        Execute all 6 sequential steps for a customer support ticket.
        """
        metrics = WorkflowMetricsCallback()
        detected_order_id = explicit_order_id or extract_order_id_from_text(ticket_text)
        order_record = get_mock_order(detected_order_id)
        order_details_text = format_order_details(order_record)

        run_result: Dict[str, Any] = {
            "ticket_id": ticket_id,
            "ticket_text": ticket_text,
            "order_id": detected_order_id,
            "provider": self.provider,
            "model_name": self.model_name,
            "steps_data": {},
        }

        # ----------------------------------------------------------------------
        # ----------------------------------------------------------------------
        # Step 1: Complaint Classification
        # ----------------------------------------------------------------------
        metrics.start_step(1, "Step 1: Complaint Classification")
        self._notify(verbose_callback, "start", 1, "Complaint Classification")
        try:
            raw_classification = self.classification_chain.invoke(
                {"ticket_text": ticket_text},
                config={"callbacks": self._get_callbacks(metrics)},
            )
            classification = clean_llm_output(raw_classification)
            step_record = metrics.complete_step(classification, status="SUCCESS")
            run_result["steps_data"]["classification"] = classification
        except Exception as e:
            metrics.complete_step("", status="FAILED", error_msg=str(e))
            raise WorkflowExecutionError(f"Step 1 (Classification) failed: {e}") from e
        self._notify(verbose_callback, "end", 1, "Complaint Classification", step_record, classification)

        # ----------------------------------------------------------------------
        # Step 2: Sentiment Analysis
        # ----------------------------------------------------------------------
        metrics.start_step(2, "Step 2: Sentiment Analysis")
        self._notify(verbose_callback, "start", 2, "Sentiment Analysis")
        try:
            raw_sentiment = self.sentiment_chain.invoke(
                {"ticket_text": ticket_text},
                config={"callbacks": self._get_callbacks(metrics)},
            )
            sentiment = clean_llm_output(raw_sentiment)
            step_record = metrics.complete_step(sentiment, status="SUCCESS")
            run_result["steps_data"]["sentiment"] = sentiment
        except Exception as e:
            metrics.complete_step("", status="FAILED", error_msg=str(e))
            raise WorkflowExecutionError(f"Step 2 (Sentiment Analysis) failed: {e}") from e
        self._notify(verbose_callback, "end", 2, "Sentiment Analysis", step_record, sentiment)

        # ----------------------------------------------------------------------
        # Step 3: Urgency Detection (Redundant Context)
        # ----------------------------------------------------------------------
        metrics.start_step(3, "Step 3: Urgency Detection")
        self._notify(verbose_callback, "start", 3, "Urgency Detection")
        try:
            raw_urgency = self.urgency_chain.invoke(
                {
                    "ticket_text": ticket_text,
                    "classification": classification,
                    "sentiment": sentiment,
                },
                config={"callbacks": self._get_callbacks(metrics)},
            )
            urgency = clean_llm_output(raw_urgency)
            step_record = metrics.complete_step(urgency, status="SUCCESS")
            run_result["steps_data"]["urgency"] = urgency
        except Exception as e:
            metrics.complete_step("", status="FAILED", error_msg=str(e))
            raise WorkflowExecutionError(f"Step 3 (Urgency Detection) failed: {e}") from e
        self._notify(verbose_callback, "end", 3, "Urgency Detection", step_record, urgency)

        # ----------------------------------------------------------------------
        # Step 4: Response Generation (Full Knowledge Base Injection)
        # ----------------------------------------------------------------------
        metrics.start_step(4, "Step 4: Response Generation")
        self._notify(verbose_callback, "start", 4, "Response Generation (Full KB)")
        try:
            raw_draft = self.response_chain.invoke(
                {
                    "ticket_text": ticket_text,
                    "classification": classification,
                    "sentiment": sentiment,
                    "urgency": urgency,
                    "order_details": order_details_text,
                    "knowledge_base": DEMOSHOP_KNOWLEDGE_BASE,
                },
                config={"callbacks": self._get_callbacks(metrics)},
            )
            draft_response = clean_llm_output(raw_draft)
            step_record = metrics.complete_step(draft_response, status="SUCCESS")
            run_result["steps_data"]["draft_response"] = draft_response
        except Exception as e:
            metrics.complete_step("", status="FAILED", error_msg=str(e))
            raise WorkflowExecutionError(f"Step 4 (Response Generation) failed: {e}") from e
        self._notify(verbose_callback, "end", 4, "Response Generation", step_record, draft_response)

        # ----------------------------------------------------------------------
        # Step 5: Response Review
        # ----------------------------------------------------------------------
        metrics.start_step(5, "Step 5: Response Review")
        self._notify(verbose_callback, "start", 5, "Response Review")
        try:
            raw_review = self.review_chain.invoke(
                {
                    "ticket_text": ticket_text,
                    "classification": classification,
                    "sentiment": sentiment,
                    "urgency": urgency,
                    "order_details": order_details_text,
                    "draft_response": draft_response,
                },
                config={"callbacks": self._get_callbacks(metrics)},
            )
            review_feedback = clean_llm_output(raw_review)
            step_record = metrics.complete_step(review_feedback, status="SUCCESS")
            run_result["steps_data"]["review_feedback"] = review_feedback
        except Exception as e:
            metrics.complete_step("", status="FAILED", error_msg=str(e))
            raise WorkflowExecutionError(f"Step 5 (Response Review) failed: {e}") from e
        self._notify(verbose_callback, "end", 5, "Response Review", step_record, review_feedback)

        # ----------------------------------------------------------------------
        # Step 6: Response Rewriting
        # ----------------------------------------------------------------------
        metrics.start_step(6, "Step 6: Response Rewriting")
        self._notify(verbose_callback, "start", 6, "Response Rewriting")
        try:
            raw_final = self.rewrite_chain.invoke(
                {
                    "ticket_text": ticket_text,
                    "draft_response": draft_response,
                    "review_feedback": review_feedback,
                },
                config={"callbacks": self._get_callbacks(metrics)},
            )
            final_response = clean_llm_output(raw_final)
            step_record = metrics.complete_step(final_response, status="SUCCESS")
            run_result["steps_data"]["final_response"] = final_response
        except Exception as e:
            metrics.complete_step("", status="FAILED", error_msg=str(e))
            raise WorkflowExecutionError(f"Step 6 (Response Rewriting) failed: {e}") from e
        self._notify(verbose_callback, "end", 6, "Response Rewriting", step_record, final_response)

        # Finalize and record summary
        summary = metrics.get_aggregate_summary()
        run_result["metrics"] = summary
        run_result["final_response"] = final_response

        # Save logs to JSON & JSONL
        try:
            saved_log_file = save_execution_log(run_result, log_dir=log_dir)
            run_result["log_file"] = saved_log_file
        except Exception as e:
            print(f"[Warning] Failed to write local log file: {e}")

        # Flush Neatlogs telemetries
        flush_neatlogs()

        return run_result
