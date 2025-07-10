#!/usr/bin/env python3
"""
LLM-based Evaluator for Agent Responses
Compares agent responses against expected answers using an LLM
"""

import os
import sys
import json
import csv
import time
from typing import Dict, List, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    import openai
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI not installed. Run: pip install openai")
    sys.exit(1)

class LLMEvaluator:
    def __init__(self, model="gpt-4o-mini"):
        self.client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
        self.model = model
        
    def evaluate_response(self, question: str, agent_response: str, expected_answer: Any, question_id: str) -> Dict[str, Any]:
        """
        Evaluate an agent response against the expected answer using LLM
        """
        
        # Format expected answer for LLM
        if isinstance(expected_answer, list):
            expected_str = f"List: {expected_answer}"
        elif isinstance(expected_answer, (int, float)):
            expected_str = f"Number: {expected_answer}"
        else:
            expected_str = f"Text: {expected_answer}"
        
        prompt = f"""
You are an expert evaluator comparing a crypto analytics agent's response against the correct answer.

QUESTION: {question}

AGENT'S RESPONSE:
{agent_response}

EXPECTED ANSWER: {expected_str}

Please evaluate the agent's response and provide:

1. **CORRECTNESS**: Is the agent's answer correct? (Yes/No/Partial)
2. **CONFIDENCE**: How confident are you in this assessment? (High/Medium/Low)
3. **REASONING**: Explain why the answer is correct or incorrect
4. **ISSUES**: What specific problems did you identify?
5. **EXTRACTION**: What numerical/quantitative answer did the agent provide?
6. **COMPARISON**: How does the agent's answer compare to the expected answer?
7. **QUALITY**: Rate the overall quality of the response (1-10)

Respond in JSON format:
{{
    "correctness": "Yes/No/Partial",
    "confidence": "High/Medium/Low", 
    "reasoning": "detailed explanation",
    "issues": ["list of specific problems"],
    "extracted_answer": "what the agent actually said",
    "comparison": "how it compares to expected",
    "quality_score": 1-10,
    "detailed_analysis": "comprehensive breakdown"
}}
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=1000
            )
            
            # Parse JSON response
            content = response.choices[0].message.content
            try:
                evaluation = json.loads(content)
            except json.JSONDecodeError:
                # Fallback if JSON parsing fails
                evaluation = {
                    "correctness": "Unknown",
                    "confidence": "Low",
                    "expected_extraction": "Could not determine",
                    "actual_extraction": "Could not extract",
                    "reasoning": "Failed to parse LLM response",
                    "issues": ["JSON parsing error"],
                    "comparison": "Could not compare",
                    "quality_score": 0,
                    "what_was_missing": "Could not determine",
                    "what_was_wrong": "Could not determine",
                    "detailed_analysis": content
                }
            
            # Add metadata
            evaluation["question_id"] = question_id
            evaluation["question"] = question
            evaluation["expected_answer"] = expected_answer
            evaluation["agent_response"] = agent_response
            
            return evaluation
            
        except Exception as e:
            return {
                "question_id": question_id,
                "question": question,
                "expected_answer": expected_answer,
                "agent_response": agent_response,
                "correctness": "Error",
                "confidence": "Low",
                "reasoning": f"Evaluation failed: {str(e)}",
                "issues": [f"LLM evaluation error: {str(e)}"],
                "extracted_answer": "Could not evaluate",
                "comparison": "Could not compare",
                "quality_score": 0,
                "detailed_analysis": f"Error during evaluation: {str(e)}"
            }

def load_queries_and_truth():
    """Load queries and their expected answers"""
    import yaml
    
    with open("data/queries.yaml", "r") as f:
        data = yaml.safe_load(f)
    
    queries = {}
    for query in data['queries']:
        queries[query['id']] = {
            'question': query['question'],
            'expected_answer': query['truth'],
            'explanation': query.get('explanation', ''),
            'category': query.get('category', '')
        }
    
    return queries

def load_agent_responses(csv_file: str) -> Dict[str, str]:
    """Load agent responses from CSV"""
    responses = {}
    
    with open(csv_file, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            responses[row['prompt_id']] = row['response']
    
    return responses

def run_llm_evaluation():
    """Run LLM evaluation on all agent responses"""
    
    print("🧠 LLM-BASED AGENT EVALUATION")
    print("=" * 50)
    
    # Load data
    print("📋 Loading queries and agent responses...")
    queries = load_queries_and_truth()
    agent_responses = load_agent_responses("test/sentient_responses.csv")
    
    # Initialize evaluator
    evaluator = LLMEvaluator()
    
    # Evaluate each response
    evaluations = []
    correct_count = 0
    total_count = 0
    
    print(f"🔄 Evaluating {len(agent_responses)} responses...")
    
    for question_id, response in agent_responses.items():
        if question_id in queries:
            question_data = queries[question_id]
            
            print(f"\n[{total_count + 1:2d}/{len(agent_responses)}] Evaluating: {question_id}")
            print(f"Question: {question_data['question'][:80]}...")
            
            # Run LLM evaluation
            evaluation = evaluator.evaluate_response(
                question=question_data['question'],
                agent_response=response,
                expected_answer=question_data['expected_answer'],
                question_id=question_id
            )
            
            evaluations.append(evaluation)
            
            # Track statistics
            total_count += 1
            if evaluation['correctness'].lower() == 'yes':
                correct_count += 1
            
            print(f"   Result: {evaluation['correctness']} (Confidence: {evaluation['confidence']})")
            print(f"   Quality: {evaluation['quality_score']}/10")
            
            # Add delay to avoid rate limits
            time.sleep(1)
    
    # Save detailed results
    print("\n💾 Saving evaluation results...")
    
    # Save as JSON
    with open("test/llm_evaluation_results.json", "w") as f:
        json.dump(evaluations, f, indent=2)
    
    # Save as CSV
    csv_fields = ['question_id', 'correctness', 'confidence', 'quality_score', 'reasoning', 'issues', 'extracted_answer', 'comparison']
    with open("test/llm_evaluation_results.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for eval in evaluations:
            writer.writerow({k: eval.get(k, '') for k in csv_fields})
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 LLM EVALUATION SUMMARY")
    print("=" * 60)
    print(f"✅ Correct Answers: {correct_count}/{total_count} ({correct_count/total_count*100:.1f}%)")
    
    # Breakdown by correctness
    correctness_counts = {}
    for eval in evaluations:
        correctness = eval['correctness'].lower()
        correctness_counts[correctness] = correctness_counts.get(correctness, 0) + 1
    
    print("\n📈 Breakdown by Correctness:")
    for correctness, count in correctness_counts.items():
        print(f"   {correctness.title()}: {count} ({count/total_count*100:.1f}%)")
    
    # Average quality score
    quality_scores = [eval['quality_score'] for eval in evaluations if isinstance(eval['quality_score'], (int, float))]
    if quality_scores:
        avg_quality = sum(quality_scores) / len(quality_scores)
        print(f"\n📊 Average Quality Score: {avg_quality:.1f}/10")
    
    print(f"\n📄 Results saved to:")
    print(f"   - test/llm_evaluation_results.json")
    print(f"   - test/llm_evaluation_results.csv")
    
    return evaluations

if __name__ == "__main__":
    run_llm_evaluation() 