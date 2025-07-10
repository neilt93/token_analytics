#!/usr/bin/env python3
"""
Complete Token Analytics Evaluation Runner
Combines LLM evaluation, grading scale, and comprehensive reporting
"""

import argparse
import json
import sys
import os
from datetime import datetime
from typing import Dict, List, Any

# Import our components
from eval import TokenAnalyticsEvaluator
from grading_scale import AnalyticsGradingScale

def load_agent_responses(file_path: str) -> Dict[str, str]:
    """Load agent responses from JSON file"""
    try:
        with open(file_path, 'r') as f:
            data = json.load(f)
            if isinstance(data, dict) and 'results' in data:
                # Convert results to response format
                responses = {}
                for result in data['results']:
                    if result.get('agent_response'):
                        responses[result['query_id']] = result['agent_response']
                return responses
            elif isinstance(data, dict):
                return data
            else:
                raise ValueError("Invalid response file format")
    except FileNotFoundError:
        print(f"❌ Error: Response file {file_path} not found")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"❌ Error: Invalid JSON in {file_path}")
        sys.exit(1)

def create_sample_responses() -> Dict[str, str]:
    """Create sample responses for testing"""
    return {
        'pct_tao_above_420_30d': "TAO was above $420 for 3.23% of the days during the 30-day period.",
        'pct_sol_below_140_30d': "SOL was below $140 for 9.68% of the days.",
        'pct_days_both_sol_eth_green_30d': "Both SOL and ETH closed higher than the previous day on 40% of the days.",
        'sol_price_change_first_half': "SOL's price decreased by 13.57% during the first half.",
        'eth_price_change_second_half': "ETH's price increased by 5.89% during the second half.",
        'tao_biggest_weekly_gain': "TAO's largest 7-day gain was 8.43% starting 2025-06-23.",
        'sol_longest_streak_above_155': "SOL's longest streak above $155 was 3 consecutive days.",
        'eth_longest_consecutive_red_days': "ETH's longest losing streak was 4 consecutive days.",
        'tao_max_5d_rolling_return': "TAO's highest 5-day rolling return was 7.04%.",
        'sol_min_3d_rolling_return': "SOL's lowest 3-day rolling return was -9.10%.",
        'sol_highest_volume_zscore_day': "SOL had its highest volume z-score on 2025-06-14.",
        'eth_avg_volume_when_sol_drop_gt5': "ETH's average volume was $19,501,480,300.75 on days when SOL dropped more than 5%.",
        'tao_highest_intraday_swing_date': "TAO experienced its largest intraday swing on 2025-06-09.",
        'eth_days_range_gt5pct': "ETH had 0 days where intraday range exceeded 5% of closing price.",
        'pct_sol_close_above_7dma': "SOL closed above its 7-day moving average on 35.48% of days.",
        'rank_by_sharpe_30d': "Ranked by Sharpe ratio: ETH, SOL, TAO.",
        'rank_by_total_return_30d': "Ranked by total return: ETH, SOL, TAO.",
        'rank_by_volatility_30d': "Ranked by volatility: TAO, ETH, SOL.",
        'pct_sol_above_160_when_eth_above_2700': "SOL closed above $160 on 100% of days when ETH was above $2700.",
        'eth_stddev_daily_return_30d': "ETH's daily returns had a standard deviation of 3.3621%."
    }

def run_complete_evaluation(agent_responses: Dict[str, str], 
                          agent_name: str = "Unknown Agent",
                          output_file: str = None,
                          verbose: bool = False) -> Dict[str, Any]:
    """
    Run complete evaluation with LLM extraction and grading
    
    Args:
        agent_responses: Dictionary of query_id to response
        agent_name: Name of the agent being evaluated
        output_file: Optional file to save results
        verbose: Whether to print detailed output
        
    Returns:
        Complete evaluation report
    """
    print(f"\n🚀 Starting Complete Evaluation for: {agent_name}")
    print("=" * 80)
    
    # Initialize evaluator
    evaluator = TokenAnalyticsEvaluator()
    
    # Run evaluation
    print("📊 Running LLM-based evaluation...")
    evaluation_summary = evaluator.run_evaluation(agent_responses, agent_name)
    
    # Print basic summary
    evaluator.print_summary(evaluation_summary)
    
    # Initialize grading scale
    print("\n📈 Applying comprehensive grading scale...")
    grader = AnalyticsGradingScale()
    grading_report = grader.grade_evaluation(evaluation_summary['results'])
    
    # Print grading report
    grader.print_grading_report(grading_report)
    
    # Combine results
    complete_report = {
        'evaluation_summary': evaluation_summary,
        'grading_report': grading_report,
        'metadata': {
            'agent_name': agent_name,
            'evaluation_timestamp': datetime.now().isoformat(),
            'total_queries': len(evaluation_summary['results']),
            'overall_grade': grading_report['overall_grade'],
            'overall_score': grading_report['overall_score']
        }
    }
    
    # Save results if output file specified
    if output_file:
        # Convert GradeLevel enums to strings for JSON serialization
        def convert_grade_levels(obj):
            if isinstance(obj, dict):
                return {k: convert_grade_levels(v) for k, v in obj.items()}
            elif isinstance(obj, list):
                return [convert_grade_levels(item) for item in obj]
            elif hasattr(obj, 'value'):  # GradeLevel enum
                return obj.value
            else:
                return obj
        
        serializable_report = convert_grade_levels(complete_report)
        with open(output_file, 'w') as f:
            json.dump(serializable_report, f, indent=2)
        print(f"\n💾 Complete results saved to: {output_file}")
    
    # Print detailed analysis if verbose
    if verbose:
        print_detailed_analysis(complete_report)
    
    return complete_report

def print_detailed_analysis(report: Dict[str, Any]):
    """Print detailed analysis of evaluation results"""
    print(f"\n🔍 Detailed Analysis")
    print("=" * 50)
    
    eval_summary = report['evaluation_summary']
    grading_report = report['grading_report']
    
    # Performance breakdown
    print(f"📊 Performance Breakdown:")
    print(f"   • Correct Answers: {eval_summary['correct_answers']}/{eval_summary['total_queries']}")
    print(f"   • Accuracy Rate: {eval_summary['accuracy_percentage']:.1f}%")
    print(f"   • Hallucination Rate: {eval_summary['hallucination_rate']:.1f}%")
    print(f"   • Average Error: {eval_summary['average_absolute_error']:.2f}")
    
    # Grade distribution
    print(f"\n📈 Grade Distribution:")
    for grade, count in grading_report['grade_distribution'].items():
        if count > 0:
            percentage = (count / grading_report['total_questions']) * 100
            print(f"   • {grade}: {count} questions ({percentage:.1f}%)")
    
    # Category performance
    print(f"\n📋 Category Performance:")
    for category, data in grading_report['category_performance'].items():
        print(f"   • {category.replace('_', ' ').title()}: {data['grade']} ({data['average_score']:.1f}/100)")
    
    # Top and bottom performers
    detailed_results = grading_report['detailed_results']
    top_performers = sorted(detailed_results, key=lambda x: x['score'], reverse=True)[:3]
    bottom_performers = sorted(detailed_results, key=lambda x: x['score'])[:3]
    
    print(f"\n🏆 Top Performers:")
    for result in top_performers:
        print(f"   • {result['query_id']}: {result['grade'].value} ({result['score']:.1f}/100)")
    
    print(f"\n⚠️  Bottom Performers:")
    for result in bottom_performers:
        print(f"   • {result['query_id']}: {result['grade'].value} ({result['score']:.1f}/100)")
        if result['feedback']:
            print(f"     - {'; '.join(result['feedback'][:2])}")

def compare_agents(agent_files: List[str], agent_names: List[str] = None) -> Dict[str, Any]:
    """Compare multiple agents"""
    if agent_names is None:
        agent_names = [f"Agent_{i+1}" for i in range(len(agent_files))]
    
    print(f"\n🔍 Comparing {len(agent_files)} Agents")
    print("=" * 60)
    
    comparison_results = {}
    
    for file_path, agent_name in zip(agent_files, agent_names):
        print(f"\n📊 Evaluating {agent_name}...")
        agent_responses = load_agent_responses(file_path)
        report = run_complete_evaluation(agent_responses, agent_name, verbose=False)
        comparison_results[agent_name] = report
    
    # Print comparison summary
    print(f"\n📊 Agent Comparison Summary")
    print("=" * 60)
    print(f"{'Agent Name':<20} {'Grade':<5} {'Score':<8} {'Accuracy':<10} {'Hallucination':<12}")
    print("-" * 60)
    
    for agent_name, report in comparison_results.items():
        eval_summary = report['evaluation_summary']
        grading_report = report['grading_report']
        print(f"{agent_name:<20} {grading_report['overall_grade']:<5} {grading_report['overall_score']:<8.1f} {eval_summary['accuracy_percentage']:<10.1f}% {eval_summary['hallucination_rate']:<12.1f}%")
    
    return comparison_results

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Complete Token Analytics Evaluation")
    parser.add_argument("--agent-name", default="Test Agent", help="Name of the agent being evaluated")
    parser.add_argument("--responses-file", help="JSON file with agent responses")
    parser.add_argument("--output", help="Output file for results")
    parser.add_argument("--verbose", action="store_true", help="Print detailed analysis")
    parser.add_argument("--sample", action="store_true", help="Use sample responses for testing")
    parser.add_argument("--compare", nargs="+", help="Compare multiple agent response files")
    parser.add_argument("--agent-names", nargs="+", help="Names for agents being compared")
    
    args = parser.parse_args()
    
    # Handle comparison mode
    if args.compare:
        agent_names = args.agent_names if args.agent_names else None
        comparison_results = compare_agents(args.compare, agent_names)
        
        # Save comparison results
        if args.output:
            # Convert GradeLevel enums to strings for JSON serialization
            def convert_grade_levels(obj):
                if isinstance(obj, dict):
                    return {k: convert_grade_levels(v) for k, v in obj.items()}
                elif isinstance(obj, list):
                    return [convert_grade_levels(item) for item in obj]
                elif hasattr(obj, 'value'):  # GradeLevel enum
                    return obj.value
                else:
                    return obj
            
            serializable_results = convert_grade_levels(comparison_results)
            with open(args.output, 'w') as f:
                json.dump(serializable_results, f, indent=2)
            print(f"\n💾 Comparison results saved to: {args.output}")
        return
    
    # Load agent responses
    if args.sample:
        print("🧪 Using sample responses for testing...")
        agent_responses = create_sample_responses()
    elif args.responses_file:
        agent_responses = load_agent_responses(args.responses_file)
    else:
        print("❌ Error: Must specify --responses-file or --sample")
        sys.exit(1)
    
    # Run evaluation
    report = run_complete_evaluation(
        agent_responses=agent_responses,
        agent_name=args.agent_name,
        output_file=args.output,
        verbose=args.verbose
    )
    
    print(f"\n✅ Evaluation completed successfully!")
    print(f"🎯 Final Grade: {report['grading_report']['overall_grade']} ({report['grading_report']['overall_score']:.1f}/100)")

if __name__ == "__main__":
    main() 