#!/usr/bin/env python3
"""
Langfuse Integration for Token Analytics Evaluation
Tracks AI performance, evaluations, and metrics in Langfuse
"""

import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from langfuse import Langfuse
except ImportError:
    print("❌ Langfuse not installed. Install with: pip install langfuse")
    print("Then set your Langfuse credentials in .env:")
    print("LANGFUSE_PUBLIC_KEY=your_public_key")
    print("LANGFUSE_SECRET_KEY=your_secret_key")
    print("LANGFUSE_HOST=https://us.cloud.langfuse.com")
    exit(1)

class LangfuseTokenAnalyticsTracker:
    """Track token analytics evaluations in Langfuse"""
    
    def __init__(self):
        """Initialize Langfuse client"""
        self.langfuse = Langfuse(
            public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
            secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
            host=os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
        )
        
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            print("⚠️  Langfuse credentials not found in .env")
            print("Please add LANGFUSE_PUBLIC_KEY and LANGFUSE_SECRET_KEY to your .env file")
    
    def create_evaluation_trace(self, 
                              agent_name: str, 
                              evaluation_results: Dict[str, Any],
                              agent_responses: Dict[str, str]) -> str:
        """Create a trace for a complete evaluation"""
        
        trace_id = f"token_analytics_eval_{agent_name}_{int(time.time())}"
        
        # Create the main trace using the new API
        with self.langfuse.start_as_current_span(
            name=f"Token Analytics Evaluation - {agent_name}",
            metadata={
                "agent_name": agent_name,
                "total_queries": evaluation_results.get("total_queries", 0),
                "correct_answers": evaluation_results.get("correct_answers", 0),
                "accuracy_percentage": evaluation_results.get("accuracy_percentage", 0),
                "hallucination_rate": evaluation_results.get("hallucination_rate", 0),
                "average_absolute_error": evaluation_results.get("average_absolute_error", 0),
                "evaluation_timestamp": datetime.now().isoformat()
            }
        ):
            # Add overall score
            overall_score = evaluation_results.get("accuracy_percentage", 0)
            self.langfuse.score_current_trace(
                name="overall_accuracy",
                value=overall_score / 100,  # Convert to 0-1 scale
                comment=f"Overall accuracy: {overall_score:.1f}%"
            )
            # Add hallucination score (inverted - lower is better)
            hallucination_rate = evaluation_results.get("hallucination_rate", 0)
            self.langfuse.score_current_trace(
                name="hallucination_rate",
                value=1 - (hallucination_rate / 100),  # Invert so lower hallucination = higher score
                comment=f"Hallucination rate: {hallucination_rate:.1f}%"
            )
            # Create spans for each question
            for result in evaluation_results.get("results", []):
                self._create_question_span(result, agent_responses.get(result["query_id"], ""))
        print(f"✅ Created Langfuse trace: {trace_id}")
        return trace_id
    
    def _create_question_span(self, result: Dict[str, Any], agent_response: str):
        """Create a span for a single question evaluation"""
        with self.langfuse.start_as_current_span(
            name=f"Question: {result['query_id']}",
            metadata={
                "query_id": result["query_id"],
                "category": result.get("category", "unknown"),
                "question": result.get("question", ""),
                "truth": result.get("truth"),
                "predicted": result.get("predicted"),
                "correct": result.get("correct", False),
                "error_type": result.get("error_type"),
                "is_hallucination": result.get("is_hallucination", False),
                "absolute_error": result.get("absolute_error")
            }
        ):
            # Add the generation (AI response)
            if agent_response:
                with self.langfuse.start_as_current_span(name="AI Response", metadata={
                    "query_id": result["query_id"],
                    "category": result.get("category", "unknown"),
                    "model": result.get("agent_name", "Unknown"),
                    "input": result.get("question", ""),
                    "output": agent_response
                }):
                    pass
            # Add scores for this question
            if result.get("correct", False):
                self.langfuse.score_current_trace(
                    name="correctness", 
                    value=1.0, 
                    comment="Correct answer"
                )
            else:
                self.langfuse.score_current_trace(
                    name="correctness", 
                    value=0.0, 
                    comment="Incorrect answer"
                )
            if result.get("is_hallucination", False):
                self.langfuse.score_current_trace(
                    name="hallucination", 
                    value=0.0, 
                    comment="Hallucination detected"
                )
            else:
                self.langfuse.score_current_trace(
                    name="hallucination", 
                    value=1.0, 
                    comment="No hallucination"
                )
            # Add error score if applicable
            if result.get("absolute_error") is not None:
                error = result["absolute_error"]
                error_score = max(0, 1 - (error / 100))  # Assuming max error of 100%
                self.langfuse.score_current_trace(
                    name="precision", 
                    value=error_score, 
                    comment=f"Error: {error}"
                )
    
    def track_agent_comparison(self, 
                              comparison_results: Dict[str, Any],
                              agent_names: List[str]) -> str:
        """Track comparison between multiple agents"""
        trace_id = f"agent_comparison_{int(time.time())}"
        with self.langfuse.start_as_current_span(
            name="Token Analytics Agent Comparison",
            metadata={
                "agent_names": agent_names,
                "comparison_timestamp": datetime.now().isoformat()
            }
        ):
            for agent_name, results in comparison_results.items():
                accuracy = results.get("evaluation_summary", {}).get("accuracy_percentage", 0)
                hallucination_rate = results.get("evaluation_summary", {}).get("hallucination_rate", 0)
                self.langfuse.score_current_trace(
                    name=f"{agent_name}_accuracy",
                    value=accuracy / 100,
                    comment=f"{agent_name} accuracy: {accuracy:.1f}%"
                )
                self.langfuse.score_current_trace(
                    name=f"{agent_name}_hallucination",
                    value=1 - (hallucination_rate / 100),
                    comment=f"{agent_name} hallucination rate: {hallucination_rate:.1f}%"
                )
            best_agent = max(comparison_results.keys(), 
                            key=lambda x: comparison_results[x].get("evaluation_summary", {}).get("accuracy_percentage", 0))
            self.langfuse.score_current_trace(
                name="best_agent",
                value=1.0,
                comment=f"Best performing agent: {best_agent}"
            )
        print(f"✅ Created comparison trace: {trace_id}")
        return trace_id
    
    def track_easy_vs_hard_performance(self, 
                                      evaluation_results: Dict[str, Any],
                                      agent_name: str) -> str:
        """Track performance on easy vs hard questions"""
        trace_id = f"difficulty_analysis_{agent_name}_{int(time.time())}"
        with self.langfuse.start_as_current_span(
            name=f"Difficulty Analysis - {agent_name}",
            metadata={
                "agent_name": agent_name,
                "analysis_timestamp": datetime.now().isoformat()
            }
        ):
            easy_results = []
            hard_results = []
            for result in evaluation_results.get("results", []):
                if result.get("query_id", "").startswith("easy_"):
                    easy_results.append(result)
                else:
                    hard_results.append(result)
            if easy_results:
                easy_correct = sum(1 for r in easy_results if r.get("correct", False))
                easy_accuracy = (easy_correct / len(easy_results)) * 100
                easy_hallucination = (sum(1 for r in easy_results if r.get("is_hallucination", False)) / len(easy_results)) * 100
                self.langfuse.score_current_trace(
                    name="easy_questions_accuracy",
                    value=easy_accuracy / 100,
                    comment=f"Easy questions accuracy: {easy_accuracy:.1f}%"
                )
                self.langfuse.score_current_trace(
                    name="easy_questions_hallucination",
                    value=1 - (easy_hallucination / 100),
                    comment=f"Easy questions hallucination: {easy_hallucination:.1f}%"
                )
            if hard_results:
                hard_correct = sum(1 for r in hard_results if r.get("correct", False))
                hard_accuracy = (hard_correct / len(hard_results)) * 100
                hard_hallucination = (sum(1 for r in hard_results if r.get("is_hallucination", False)) / len(hard_results)) * 100
                self.langfuse.score_current_trace(
                    name="hard_questions_accuracy",
                    value=hard_accuracy / 100,
                    comment=f"Hard questions accuracy: {hard_accuracy:.1f}%"
                )
                self.langfuse.score_current_trace(
                    name="hard_questions_hallucination",
                    value=1 - (hard_hallucination / 100),
                    comment=f"Hard questions hallucination: {hard_hallucination:.1f}%"
                )
        print(f"✅ Created difficulty analysis trace: {trace_id}")
        return trace_id

def integrate_with_existing_evaluation(evaluation_file: str, agent_name: str):
    """Integrate existing evaluation results with Langfuse"""
    with open(evaluation_file, 'r') as f:
        evaluation_results = json.load(f)
    responses_file = evaluation_file.replace("_evaluation_results.json", "_raw_responses.json")
    if os.path.exists(responses_file):
        with open(responses_file, 'r') as f:
            agent_responses = json.load(f)
    else:
        agent_responses = {}
    tracker = LangfuseTokenAnalyticsTracker()
    trace_id = tracker.create_evaluation_trace(agent_name, evaluation_results, agent_responses)
    difficulty_trace_id = tracker.track_easy_vs_hard_performance(evaluation_results, agent_name)
    print(f"📊 Langfuse integration complete!")
    print(f"   Main trace: {trace_id}")
    print(f"   Difficulty analysis: {difficulty_trace_id}")
    return trace_id

def main():
    print("🚀 Langfuse Integration for Token Analytics")
    print("=" * 50)
    evaluation_files = [
        "test/chatgpt_evaluation_results.json",
        "test/perplexity_evaluation_results.json"
    ]
    tracker = LangfuseTokenAnalyticsTracker()
    for eval_file in evaluation_files:
        if os.path.exists(eval_file):
            agent_name = "ChatGPT" if "chatgpt" in eval_file else "Perplexity"
            print(f"\n📊 Integrating {agent_name} evaluation...")
            integrate_with_existing_evaluation(eval_file, agent_name)
    print("\n✅ Langfuse integration complete!")
    print("\n📋 Next steps:")
    print("1. View traces in Langfuse dashboard")
    print("2. Set up alerts for performance drops")
    print("3. Create custom dashboards for monitoring")
    print("4. Use traces for A/B testing different AI models")

if __name__ == "__main__":
    main() 