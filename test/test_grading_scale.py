#!/usr/bin/env python3
"""
Test script for the Analytics Grading Scale
Demonstrates grading functionality with Perplexity AI evaluation results
"""

import sys
import os
import json
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from grading_scale import AnalyticsGradingScale
from eval import TokenAnalyticsEvaluator

def test_grading_scale():
    """Test the grading scale with Perplexity AI results"""
    
    # Load the Perplexity AI evaluation results
    results_file = "test/perplexity_evaluation_results.json"
    
    try:
        with open(results_file, 'r') as f:
            perplexity_results = json.load(f)
        
        print("📊 Testing Analytics Grading Scale with Perplexity AI Results")
        print("=" * 80)
        
        # Initialize the grading scale
        grader = AnalyticsGradingScale()
        
        # Grade the evaluation
        grading_report = grader.grade_evaluation(perplexity_results['results'])
        
        # Print the comprehensive grading report
        grader.print_grading_report(grading_report)
        
        # Additional analysis
        print(f"\n🔍 Detailed Analysis:")
        print(f"   • Questions with A grades: {grading_report['grade_distribution']['A+'] + grading_report['grade_distribution']['A'] + grading_report['grade_distribution']['A-']}")
        print(f"   • Questions with F grades: {grading_report['grade_distribution']['F']}")
        
        # Show some detailed results
        print(f"\n📋 Sample Detailed Results:")
        for result in grading_report['detailed_results'][:3]:
            print(f"   • {result['query_id']}: {result['grade'].value} ({result['score']:.1f}/100)")
            print(f"     Accuracy: {result['accuracy_score']:.1f}, Precision: {result['precision_score']:.1f}, Quality: {result['quality_score']:.1f}")
            if result['feedback']:
                print(f"     Feedback: {'; '.join(result['feedback'][:2])}")
            print()
        
        # Category analysis
        print(f"📈 Category Performance Analysis:")
        for category, data in grading_report['category_performance'].items():
            print(f"   • {category.replace('_', ' ').title()}: {data['grade']} ({data['average_score']:.1f}/100)")
            print(f"     Questions: {data['count']}")
        
        return grading_report
        
    except FileNotFoundError:
        print(f"❌ Error: Could not find {results_file}")
        print("Please run the Perplexity AI evaluation first.")
        return None
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

def test_grading_components():
    """Test individual grading components"""
    print("\n🧪 Testing Grading Components")
    print("=" * 40)
    
    grader = AnalyticsGradingScale()
    
    # Test cases for different scenarios
    test_cases = [
        {
            'name': 'Perfect Answer',
            'result': {
                'query_id': 'test_perfect',
                'category': 'percentage_threshold',
                'correct': True,
                'absolute_error': 0.0,
                'error_type': 'numeric_error',
                'is_hallucination': False,
                'predicted': 50.0,
                'truth': 50.0
            }
        },
        {
            'name': 'Close Answer',
            'result': {
                'query_id': 'test_close',
                'category': 'price_change',
                'correct': False,
                'absolute_error': 2.0,
                'error_type': 'numeric_error',
                'is_hallucination': False,
                'predicted': 12.0,
                'truth': 10.0
            }
        },
        {
            'name': 'Hallucination',
            'result': {
                'query_id': 'test_hallucination',
                'category': 'performance_comparison',
                'correct': False,
                'absolute_error': None,
                'error_type': 'type_mismatch',
                'is_hallucination': True,
                'predicted': None,
                'truth': ['ETH', 'SOL', 'TAO']
            }
        },
        {
            'name': 'Wrong Ranking',
            'result': {
                'query_id': 'test_ranking',
                'category': 'performance_comparison',
                'correct': False,
                'absolute_error': None,
                'error_type': 'list_mismatch',
                'is_hallucination': False,
                'predicted': ['SOL', 'ETH', 'TAO'],
                'truth': ['ETH', 'SOL', 'TAO']
            }
        }
    ]
    
    for test_case in test_cases:
        print(f"\n📝 {test_case['name']}:")
        score_info = grader.calculate_question_score(test_case['result'])
        print(f"   Grade: {score_info['grade'].value}")
        print(f"   Score: {score_info['score']:.1f}/100")
        print(f"   Accuracy: {score_info['accuracy_score']:.1f}")
        print(f"   Precision: {score_info['precision_score']:.1f}")
        print(f"   Quality: {score_info['quality_score']:.1f}")
        if score_info['feedback']:
            print(f"   Feedback: {'; '.join(score_info['feedback'])}")

def test_grade_thresholds():
    """Test grade threshold calculations"""
    print("\n📊 Testing Grade Thresholds")
    print("=" * 30)
    
    grader = AnalyticsGradingScale()
    
    test_scores = [100, 95, 90, 85, 80, 75, 70, 65, 60, 55, 50, 45, 40, 35, 0]
    
    for score in test_scores:
        grade = grader._get_grade(score)
        print(f"   Score {score:3d}: {grade.value}")

if __name__ == "__main__":
    # Test the grading scale with Perplexity AI results
    grading_report = test_grading_scale()
    
    # Test individual components
    test_grading_components()
    
    # Test grade thresholds
    test_grade_thresholds()
    
    print(f"\n✅ Grading scale testing completed!") 