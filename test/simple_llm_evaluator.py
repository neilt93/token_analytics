#!/usr/bin/env python3
"""
Simple LLM-based Evaluator for Agent Responses
More robust evaluation with better error handling
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
    from openai import OpenAI
except ImportError:
    print("❌ OpenAI not installed. Run: pip install openai")
    sys.exit(1)

class SimpleLLMEvaluator:
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
Analyze this crypto agent response:

QUESTION: {question}

AGENT RESPONSE:
{agent_response}

EXPECTED ANSWER: {expected_str}

Provide a simple analysis in this format:
- Correctness: Yes/No/Partial
- Agent's Answer: [extract what they said]
- Expected Answer: [what they should have said]
- Issues: [list problems]
- Quality Score: [1-10]

Be concise and clear.
"""
        
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}],
                temperature=0.1,
                max_tokens=500
            )
            
            content = response.choices[0].message.content
            
            # Parse the response manually
            evaluation = self._parse_llm_response(content)
            
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
                "agent_answer": "Could not evaluate",
                "expected_answer_text": str(expected_answer),
                "issues": [f"LLM evaluation error: {str(e)}"],
                "quality_score": 0,
                "raw_llm_response": f"Error: {str(e)}"
            }
    
    def _parse_llm_response(self, content: str) -> Dict[str, Any]:
        """Parse LLM response into structured format"""
        try:
            # Try to extract key information from the response
            lines = content.split('\n')
            evaluation = {
                "correctness": "Unknown",
                "agent_answer": "Could not extract",
                "expected_answer_text": "Could not extract", 
                "issues": [],
                "quality_score": 0,
                "raw_llm_response": content
            }
            
            for line in lines:
                line = line.strip()
                if line.startswith("- Correctness:"):
                    evaluation["correctness"] = line.split(":", 1)[1].strip()
                elif line.startswith("- Agent's Answer:"):
                    evaluation["agent_answer"] = line.split(":", 1)[1].strip()
                elif line.startswith("- Expected Answer:"):
                    evaluation["expected_answer_text"] = line.split(":", 1)[1].strip()
                elif line.startswith("- Issues:"):
                    issues = line.split(":", 1)[1].strip()
                    evaluation["issues"] = [issues] if issues else []
                elif line.startswith("- Quality Score:"):
                    try:
                        score = int(line.split(":", 1)[1].strip())
                        evaluation["quality_score"] = score
                    except:
                        evaluation["quality_score"] = 0
            
            return evaluation
            
        except Exception as e:
            return {
                "correctness": "Unknown",
                "agent_answer": "Could not extract",
                "expected_answer_text": "Could not extract",
                "issues": [f"Parsing error: {str(e)}"],
                "quality_score": 0,
                "raw_llm_response": content
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

def run_simple_llm_evaluation():
    """Run simple LLM evaluation on all agent responses"""
    
    print("🧠 SIMPLE LLM-BASED AGENT EVALUATION")
    print("=" * 50)
    
    # Load data
    print("📋 Loading queries and agent responses...")
    queries = load_queries_and_truth()
    agent_responses = load_agent_responses("test/sentient_responses.csv")
    
    # Initialize evaluator
    evaluator = SimpleLLMEvaluator()
    
    # Evaluate each response
    evaluations = []
    correct_count = 0
    total_count = 0
    
    print(f"🔄 Evaluating {len(agent_responses)} responses...")
    
    for question_id, response in agent_responses.items():
        if question_id in queries:
            question_data = queries[question_id]
            
            print(f"\n[{total_count + 1:2d}/{len(agent_responses)}] Evaluating: {question_id}")
            print(f"Question: {question_data['question'][:60]}...")
            
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
            
            print(f"   Result: {evaluation['correctness']}")
            print(f"   Quality: {evaluation['quality_score']}/10")
            print(f"   Agent said: {evaluation['agent_answer'][:50]}...")
            
            # Add delay to avoid rate limits
            time.sleep(0.5)
    
    # Save detailed results
    print("\n💾 Saving evaluation results...")
    
    # Save as JSON
    with open("test/simple_llm_evaluation_results.json", "w") as f:
        json.dump(evaluations, f, indent=2)
    
    # Save as CSV
    csv_fields = ['question_id', 'correctness', 'quality_score', 'agent_answer', 'expected_answer_text', 'issues']
    with open("test/simple_llm_evaluation_results.csv", "w", newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=csv_fields)
        writer.writeheader()
        for eval in evaluations:
            writer.writerow({k: eval.get(k, '') for k in csv_fields})
    
    # Print summary
    print("\n" + "=" * 60)
    print("📊 SIMPLE LLM EVALUATION SUMMARY")
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
    print(f"   - test/simple_llm_evaluation_results.json")
    print(f"   - test/simple_llm_evaluation_results.csv")
    
    return evaluations

if __name__ == "__main__":
    run_simple_llm_evaluation() 