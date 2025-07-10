#!/usr/bin/env python3
"""
Run Sentient LLM Evaluation
Evaluates Sentient LLM agents using a benchmark set
"""

import os
import sys
import csv
import json
import time
from dotenv import load_dotenv

# Import your evaluation class
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from eval import TokenAnalyticsEvaluator

# Import the response mechanism
from run_sentient_core import get_agent_responses, _AGENTS, _NUM_AGENTS
from sse_api import get_chat_id

# Load .env for Langfuse, config, etc.
load_dotenv()

def run_sentient_evaluation():
    """
    Evaluate all agents in Sentient LLM system using benchmark questions
    """
    print("🧠 SENTIENT LLM EVALUATION")
    print("=" * 50)

    evaluator = TokenAnalyticsEvaluator()
    queries = evaluator.queries['queries']
    print(f"📋 Found {len(queries)} benchmark queries")
    print("🔄 Collecting responses from Sentient agents...\n")

    responses = {}
    csv_data = []
    
    for i, query in enumerate(queries, 1):
        prompt_id = query['id']
        question = query['question']

        print(f"[{i:2d}/{len(queries)}] {prompt_id}: {question[:60]}...")

        # Get a real chat ID for this question
        try:
            chat_id = get_chat_id()
            print(f"    Chat ID: {chat_id}")
        except Exception as e:
            print(f"❌ Failed to get chat ID: {e}")
            chat_id = f"fallback-chat-{prompt_id}"

        # Use the real chat ID for all agents
        chat_ids = [chat_id] * _NUM_AGENTS

        try:
            result = get_agent_responses(chat_ids, question, prompt_id, "0")
            agent_answers = {agent: result[i][0] for i, agent in enumerate(_AGENTS.keys())}

            # For this evaluation, choose one agent to evaluate (e.g., the first)
            primary_agent = list(_AGENTS.keys())[0]
            response_text = agent_answers[primary_agent]
            responses[prompt_id] = response_text

            # Log to CSV data
            csv_data.append({
                'prompt_id': prompt_id,
                'question': question,
                'chat_id': chat_id,
                'agent': primary_agent,
                'response': response_text,
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

            print(f"    Response:\n{response_text}\n{'-'*40}\n")
            time.sleep(1)

        except Exception as e:
            print(f"❌ Error during response collection: {e}")
            responses[prompt_id] = "ERROR"
            
            # Log error to CSV
            csv_data.append({
                'prompt_id': prompt_id,
                'question': question,
                'chat_id': chat_id,
                'agent': 'unknown',
                'response': f"ERROR: {e}",
                'timestamp': time.strftime('%Y-%m-%d %H:%M:%S')
            })

    # Save responses to JSON
    print("💾 Saving raw responses...")
    os.makedirs("test", exist_ok=True)
    with open("test/sentient_raw_responses.json", "w") as f:
        json.dump(responses, f, indent=2)

    # Save detailed results to CSV
    csv_filename = "test/sentient_responses.csv"
    with open(csv_filename, 'w', newline='', encoding='utf-8') as csvfile:
        fieldnames = ['prompt_id', 'question', 'chat_id', 'agent', 'response', 'timestamp']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(csv_data)
    
    print(f"📄 Detailed results saved to: {csv_filename}")

    print("📊 Running evaluation...")
    summary = evaluator.run_evaluation(responses, "Sentient LLM")

    print("\n" + "=" * 60)
    evaluator.print_summary(summary)

    evaluator.save_results(summary, "test/sentient_evaluation_results.json")
    print(f"\n📄 Results saved to: test/sentient_evaluation_results.json")
    print(f"📄 Raw responses saved to: test/sentient_raw_responses.json")

    return summary


def main():
    print("🚀 Sentient LLM Token Analytics Evaluation")
    print("=" * 60)

    try:
        summary = run_sentient_evaluation()
        print("\n🎉 EVALUATION COMPLETE!")
        print("=" * 60)
        print(f"✅ Accuracy: {summary['accuracy_percentage']:.1f}%")
        print(f"📊 Correct answers: {summary['correct_answers']}/{summary['total_queries']}")
        print(f"❌ Hallucinations: {summary['hallucination_count']} ({summary['hallucination_rate']:.1f}%)")
        print(f"📈 Avg. Error: {summary['average_absolute_error']:.2f}")

        if summary['accuracy_percentage'] >= 90:
            rating = "🏆 EXCELLENT"
        elif summary['accuracy_percentage'] >= 80:
            rating = "🥇 GREAT"
        elif summary['accuracy_percentage'] >= 70:
            rating = "🥈 GOOD"
        elif summary['accuracy_percentage'] >= 60:
            rating = "🥉 FAIR"
        else:
            rating = "⚠️ NEEDS IMPROVEMENT"

        print(f"\n{rating} - {summary['accuracy_percentage']:.1f}% accuracy")

    except KeyboardInterrupt:
        print("\n⏹️ Evaluation interrupted by user")
    except Exception as e:
        print(f"\n❌ Evaluation error: {e}")


if __name__ == "__main__":
    main()
