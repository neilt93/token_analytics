#!/usr/bin/env python3
"""
Create Notion Table for GPT vs Perplexity Comparison
Generates a copyable table with questions, responses, evaluations, and grades
"""

import json
import sys
import os
from typing import Dict, List, Any

def load_evaluation_results(file_path: str) -> Dict[str, Any]:
    """Load evaluation results from JSON file"""
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print(f"❌ Error: File {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {file_path}")
        sys.exit(1)

def calculate_grade(accuracy_percentage: float, hallucination_rate: float) -> str:
    """Calculate grade based on accuracy and hallucination rate"""
    if hallucination_rate > 50:
        return "F"
    elif accuracy_percentage >= 90:
        return "A"
    elif accuracy_percentage >= 80:
        return "B"
    elif accuracy_percentage >= 70:
        return "C"
    elif accuracy_percentage >= 60:
        return "D"
    else:
        return "F"

def truncate_text(text: str, max_length: int = 200) -> str:
    """Truncate text to max length with ellipsis"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."

def create_notion_table(gpt_results: Dict[str, Any], pplx_results: Dict[str, Any]) -> str:
    """Create Notion table comparing GPT and Perplexity results"""
    
    # Calculate overall grades
    gpt_grade = calculate_grade(gpt_results['accuracy_percentage'], gpt_results['hallucination_rate'])
    pplx_grade = calculate_grade(pplx_results['accuracy_percentage'], pplx_results['hallucination_rate'])
    
    # Create table header
    table = "| Question | GPT Response | Perplexity Response | GPT Evaluation | Perplexity Evaluation | GPT Grade | Perplexity Grade |\n"
    table += "|----------|--------------|-------------------|----------------|----------------------|-----------|------------------|\n"
    
    # Create lookup for results by query_id
    gpt_lookup = {result['query_id']: result for result in gpt_results['results']}
    pplx_lookup = {result['query_id']: result for result in pplx_results['results']}
    
    # Get all unique query IDs
    all_query_ids = set(gpt_lookup.keys()) | set(pplx_lookup.keys())
    
    for query_id in sorted(all_query_ids):
        gpt_result = gpt_lookup.get(query_id, {})
        pplx_result = pplx_lookup.get(query_id, {})
        
        # Extract data
        question = gpt_result.get('question', pplx_result.get('question', 'Unknown'))
        gpt_response = truncate_text(gpt_result.get('agent_response', 'No response'))
        pplx_response = truncate_text(pplx_result.get('agent_response', 'No response'))
        
        # GPT evaluation
        gpt_correct = "✅" if gpt_result.get('correct', False) else "❌"
        gpt_error = gpt_result.get('error_type', 'N/A')
        gpt_hallucination = "🤖" if gpt_result.get('is_hallucination', False) else ""
        gpt_eval = f"{gpt_correct} {gpt_error} {gpt_hallucination}".strip()
        
        # Perplexity evaluation
        pplx_correct = "✅" if pplx_result.get('correct', False) else "❌"
        pplx_error = pplx_result.get('error_type', 'N/A')
        pplx_hallucination = "🤖" if pplx_result.get('is_hallucination', False) else ""
        pplx_eval = f"{pplx_correct} {pplx_error} {pplx_hallucination}".strip()
        
        # Individual question grades
        gpt_question_grade = calculate_grade(
            100 if gpt_result.get('correct', False) else 0,
            100 if gpt_result.get('is_hallucination', False) else 0
        )
        pplx_question_grade = calculate_grade(
            100 if pplx_result.get('correct', False) else 0,
            100 if pplx_result.get('is_hallucination', False) else 0
        )
        
        # Add row to table
        table += f"| {question} | {gpt_response} | {pplx_response} | {gpt_eval} | {pplx_eval} | {gpt_question_grade} | {pplx_question_grade} |\n"
    
    # Add summary row
    table += "\n| **SUMMARY** | **GPT Overall** | **Perplexity Overall** | **GPT Performance** | **Perplexity Performance** | **GPT Grade** | **Perplexity Grade** |\n"
    table += "|-------------|----------------|----------------------|-------------------|------------------------|--------------|-------------------|\n"
    
    gpt_summary = f"Accuracy: {gpt_results['accuracy_percentage']:.1f}%, Hallucinations: {gpt_results['hallucination_rate']:.1f}%"
    pplx_summary = f"Accuracy: {pplx_results['accuracy_percentage']:.1f}%, Hallucinations: {pplx_results['hallucination_rate']:.1f}%"
    
    gpt_perf = f"Correct: {gpt_results['correct_answers']}/{gpt_results['total_queries']}"
    pplx_perf = f"Correct: {pplx_results['correct_answers']}/{pplx_results['total_queries']}"
    
    table += f"| **Overall Results** | {gpt_summary} | {pplx_summary} | {gpt_perf} | {pplx_perf} | **{gpt_grade}** | **{pplx_grade}** |\n"
    
    return table

def main():
    """Main function to create the comparison table"""
    
    # File paths
    gpt_file = "test/chatgpt_evaluation_results.json"
    pplx_file = "test/perplexity_evaluation_results.json"
    
    # Check if files exist
    if not os.path.exists(gpt_file):
        print(f"❌ Error: {gpt_file} not found")
        print("Please run the ChatGPT evaluation first:")
        print("python test/run_chatgpt_eval.py")
        sys.exit(1)
    
    if not os.path.exists(pplx_file):
        print(f"❌ Error: {pplx_file} not found")
        print("Please run the Perplexity evaluation first:")
        print("python test/run_perplexity_eval.py")
        sys.exit(1)
    
    # Load results
    print("📊 Loading evaluation results...")
    gpt_results = load_evaluation_results(gpt_file)
    pplx_results = load_evaluation_results(pplx_file)
    
    # Create table
    print("📋 Creating Notion table...")
    table = create_notion_table(gpt_results, pplx_results)
    
    # Save to file
    output_file = "gpt_vs_perplexity_comparison_table.md"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write("# GPT vs Perplexity AI Comparison Table\n\n")
        f.write("## Summary\n\n")
        f.write(f"- **GPT Accuracy**: {gpt_results['accuracy_percentage']:.1f}% ({gpt_results['correct_answers']}/{gpt_results['total_queries']})\n")
        f.write(f"- **GPT Hallucination Rate**: {gpt_results['hallucination_rate']:.1f}%\n")
        f.write(f"- **Perplexity Accuracy**: {pplx_results['accuracy_percentage']:.1f}% ({pplx_results['correct_answers']}/{pplx_results['total_queries']})\n")
        f.write(f"- **Perplexity Hallucination Rate**: {pplx_results['hallucination_rate']:.1f}%\n\n")
        f.write("## Detailed Comparison\n\n")
        f.write(table)
    
    print(f"✅ Table saved to: {output_file}")
    print("\n📋 Copy the table below to Notion:")
    print("=" * 80)
    print(table)
    print("=" * 80)

if __name__ == "__main__":
    main() 