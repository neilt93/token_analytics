#!/usr/bin/env python3
"""
Grading Scale for Analytics Questions
Provides nuanced scoring for AI agent performance on token analytics queries
"""

import numpy as np
from typing import Dict, Any, List, Tuple
from enum import Enum

class GradeLevel(Enum):
    """Grade levels for analytics questions"""
    A_PLUS = "A+"
    A = "A"
    A_MINUS = "A-"
    B_PLUS = "B+"
    B = "B"
    B_MINUS = "B-"
    C_PLUS = "C+"
    C = "C"
    C_MINUS = "C-"
    D_PLUS = "D+"
    D = "D"
    D_MINUS = "D-"
    F = "F"

class AnalyticsGradingScale:
    """
    Comprehensive grading scale for analytics questions
    Evaluates accuracy, precision, and response quality
    """
    
    def __init__(self):
        """Initialize the grading scale with thresholds"""
        self.grade_thresholds = {
            GradeLevel.A_PLUS: 95.0,
            GradeLevel.A: 90.0,
            GradeLevel.A_MINUS: 85.0,
            GradeLevel.B_PLUS: 80.0,
            GradeLevel.B: 75.0,
            GradeLevel.B_MINUS: 70.0,
            GradeLevel.C_PLUS: 65.0,
            GradeLevel.C: 60.0,
            GradeLevel.C_MINUS: 55.0,
            GradeLevel.D_PLUS: 50.0,
            GradeLevel.D: 45.0,
            GradeLevel.D_MINUS: 40.0,
            GradeLevel.F: 0.0
        }
        
        # Category-specific scoring weights
        self.category_weights = {
            'percentage_threshold': 1.0,
            'conditional_threshold': 1.0,
            'price_change': 1.0,
            'volatility': 1.0,
            'volatility_stat': 1.0,
            'streak_analysis': 1.0,
            'rolling_stats': 1.0,
            'volume_analysis': 1.0,
            'performance_comparison': 1.0,
            'conditional_volume': 1.0
        }
    
    def calculate_question_score(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Calculate detailed score for a single question
        
        Args:
            result: Evaluation result from TokenAnalyticsEvaluator
            
        Returns:
            Dictionary with detailed scoring information
        """
        score_info = {
            'query_id': result['query_id'],
            'category': result['category'],
            'grade': GradeLevel.F,
            'score': 0.0,
            'accuracy_score': 0.0,
            'precision_score': 0.0,
            'quality_score': 0.0,
            'penalties': [],
            'bonuses': [],
            'feedback': []
        }
        
        # Handle different response types
        if result['error_type'] == 'missing_response':
            score_info['feedback'].append("No response provided")
            return score_info
        
        if result['is_hallucination']:
            score_info['penalties'].append("Hallucination detected")
            score_info['score'] = 0.0
            score_info['grade'] = GradeLevel.F
            return score_info
        
        # Calculate accuracy score (0-100)
        accuracy_score = self._calculate_accuracy_score(result)
        score_info['accuracy_score'] = accuracy_score
        
        # Calculate precision score (0-100)
        precision_score = self._calculate_precision_score(result)
        score_info['precision_score'] = precision_score
        
        # Calculate quality score (0-100)
        quality_score = self._calculate_quality_score(result)
        score_info['quality_score'] = quality_score
        
        # Calculate weighted final score
        final_score = self._calculate_final_score(accuracy_score, precision_score, quality_score)
        score_info['score'] = final_score
        
        # Determine grade
        score_info['grade'] = self._get_grade(final_score)
        
        # Add feedback
        self._add_feedback(score_info, result)
        
        return score_info
    
    def _calculate_accuracy_score(self, result: Dict[str, Any]) -> float:
        """Calculate accuracy score based on correctness"""
        if result['correct']:
            return 100.0
        
        # For numeric errors, score based on error magnitude
        if result['error_type'] == 'numeric_error' and result['absolute_error'] is not None:
            error_magnitude = result['absolute_error']
            truth_value = result['truth']
            
            if isinstance(truth_value, (int, float)) and truth_value != 0:
                relative_error = abs(error_magnitude / truth_value)
                
                # Score based on relative error
                if relative_error <= 0.01:  # Within 1%
                    return 95.0
                elif relative_error <= 0.05:  # Within 5%
                    return 85.0
                elif relative_error <= 0.10:  # Within 10%
                    return 70.0
                elif relative_error <= 0.25:  # Within 25%
                    return 50.0
                elif relative_error <= 0.50:  # Within 50%
                    return 30.0
                else:
                    return 10.0
            else:
                # For zero truth values, score based on absolute error
                if error_magnitude <= 1.0:
                    return 90.0
                elif error_magnitude <= 5.0:
                    return 70.0
                elif error_magnitude <= 10.0:
                    return 50.0
                else:
                    return 20.0
        
        # For other error types
        elif result['error_type'] == 'string_mismatch':
            return 30.0
        elif result['error_type'] == 'list_mismatch':
            return 40.0
        elif result['error_type'] == 'type_mismatch':
            return 20.0
        
        return 0.0
    
    def _calculate_precision_score(self, result: Dict[str, Any]) -> float:
        """Calculate precision score based on response specificity"""
        if result['predicted'] is None:
            return 0.0
        
        # Check if response provides specific numeric values
        if isinstance(result['predicted'], (int, float)):
            return 100.0
        
        # Check if response provides specific tokens
        if isinstance(result['predicted'], str) and result['predicted'] in ['SOL', 'ETH', 'TAO']:
            return 100.0
        
        # Check if response provides specific rankings
        if isinstance(result['predicted'], list) and len(result['predicted']) > 0:
            return 100.0
        
        # Check if response provides specific dates
        if isinstance(result['predicted'], str) and len(result['predicted']) == 10:  # YYYY-MM-DD
            return 100.0
        
        return 50.0  # Partial precision
    
    def _calculate_quality_score(self, result: Dict[str, Any]) -> float:
        """Calculate quality score based on response characteristics"""
        quality_score = 100.0
        
        # Penalize for hallucinations
        if result['is_hallucination']:
            quality_score -= 50.0
        
        # Penalize for missing responses
        if result['predicted'] is None:
            quality_score -= 30.0
        
        # Bonus for exact matches
        if result['correct']:
            quality_score += 10.0
        
        # Bonus for high precision responses
        if isinstance(result['predicted'], (int, float)) and result['absolute_error'] is not None:
            if result['absolute_error'] <= 0.1:
                quality_score += 5.0
        
        return max(0.0, min(100.0, quality_score))
    
    def _calculate_final_score(self, accuracy: float, precision: float, quality: float) -> float:
        """Calculate weighted final score"""
        # Weight the components
        weighted_score = (accuracy * 0.6) + (precision * 0.25) + (quality * 0.15)
        return round(weighted_score, 2)
    
    def _get_grade(self, score: float) -> GradeLevel:
        """Convert score to letter grade"""
        for grade, threshold in self.grade_thresholds.items():
            if score >= threshold:
                return grade
        return GradeLevel.F
    
    def _add_feedback(self, score_info: Dict[str, Any], result: Dict[str, Any]):
        """Add detailed feedback to score info"""
        if result['correct']:
            score_info['feedback'].append("✅ Correct answer")
        
        if result['absolute_error'] is not None:
            score_info['feedback'].append(f"📏 Error magnitude: {result['absolute_error']:.2f}")
        
        if result['is_hallucination']:
            score_info['feedback'].append("❌ Hallucination detected")
        
        if result['error_type'] == 'numeric_error':
            score_info['feedback'].append("🔢 Numeric precision issue")
        elif result['error_type'] == 'string_mismatch':
            score_info['feedback'].append("📝 String matching issue")
        elif result['error_type'] == 'list_mismatch':
            score_info['feedback'].append("📋 List ordering issue")
        elif result['error_type'] == 'type_mismatch':
            score_info['feedback'].append("🔄 Type conversion issue")
    
    def grade_evaluation(self, evaluation_results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Grade a complete evaluation
        
        Args:
            evaluation_results: List of evaluation results
            
        Returns:
            Comprehensive grading report
        """
        graded_results = []
        category_scores = {}
        total_score = 0.0
        
        for result in evaluation_results:
            score_info = self.calculate_question_score(result)
            graded_results.append(score_info)
            
            # Track category performance
            category = result['category']
            if category not in category_scores:
                category_scores[category] = {'scores': [], 'count': 0}
            
            category_scores[category]['scores'].append(score_info['score'])
            category_scores[category]['count'] += 1
            total_score += score_info['score']
        
        # Calculate overall statistics
        overall_score = total_score / len(evaluation_results) if evaluation_results else 0.0
        overall_grade = self._get_grade(overall_score)
        
        # Calculate category averages
        category_averages = {}
        for category, data in category_scores.items():
            if data['count'] > 0:
                category_averages[category] = {
                    'average_score': sum(data['scores']) / data['count'],
                    'grade': self._get_grade(sum(data['scores']) / data['count']),
                    'count': data['count']
                }
        
        # Grade distribution
        grade_distribution = {}
        for grade in GradeLevel:
            grade_distribution[grade.value] = 0
        
        for result in graded_results:
            grade_distribution[result['grade'].value] += 1
        
        return {
            'overall_score': round(overall_score, 2),
            'overall_grade': overall_grade.value,
            'total_questions': len(evaluation_results),
            'category_performance': category_averages,
            'grade_distribution': grade_distribution,
            'detailed_results': graded_results,
            'summary_stats': {
                'average_accuracy_score': np.mean([r['accuracy_score'] for r in graded_results]),
                'average_precision_score': np.mean([r['precision_score'] for r in graded_results]),
                'average_quality_score': np.mean([r['quality_score'] for r in graded_results]),
                'questions_with_penalties': sum(1 for r in graded_results if r['penalties']),
                'questions_with_bonuses': sum(1 for r in graded_results if r['bonuses'])
            }
        }
    
    def print_grading_report(self, grading_report: Dict[str, Any]):
        """Print a formatted grading report"""
        print(f"\n{'='*80}")
        print(f"📊 ANALYTICS GRADING REPORT")
        print(f"{'='*80}")
        print(f"🎯 Overall Grade: {grading_report['overall_grade']} ({grading_report['overall_score']:.1f}/100)")
        print(f"📝 Total Questions: {grading_report['total_questions']}")
        
        # Grade distribution
        print(f"\n📈 Grade Distribution:")
        for grade, count in grading_report['grade_distribution'].items():
            if count > 0:
                percentage = (count / grading_report['total_questions']) * 100
                print(f"   {grade}: {count} questions ({percentage:.1f}%)")
        
        # Category performance
        print(f"\n📊 Performance by Category:")
        for category, data in grading_report['category_performance'].items():
            print(f"   • {category.replace('_', ' ').title()}: {data['grade']} ({data['average_score']:.1f}/100) - {data['count']} questions")
        
        # Summary statistics
        stats = grading_report['summary_stats']
        print(f"\n📋 Summary Statistics:")
        print(f"   • Average Accuracy Score: {stats['average_accuracy_score']:.1f}/100")
        print(f"   • Average Precision Score: {stats['average_precision_score']:.1f}/100")
        print(f"   • Average Quality Score: {stats['average_quality_score']:.1f}/100")
        print(f"   • Questions with Penalties: {stats['questions_with_penalties']}")
        print(f"   • Questions with Bonuses: {stats['questions_with_bonuses']}")
        
        # Detailed feedback for low-scoring questions
        low_scoring = [r for r in grading_report['detailed_results'] if r['score'] < 60]
        if low_scoring:
            print(f"\n⚠️  Low-Scoring Questions (Below 60%):")
            for result in low_scoring[:5]:  # Show top 5
                print(f"   • {result['query_id']}: {result['grade'].value} ({result['score']:.1f}/100)")
                for feedback in result['feedback'][:2]:  # Show top 2 feedback items
                    print(f"     - {feedback}")

def main():
    """Example usage of the grading scale"""
    grader = AnalyticsGradingScale()
    
    # Example evaluation results
    example_results = [
        {
            'query_id': 'pct_sol_below_140_30d',
            'category': 'percentage_threshold',
            'correct': True,
            'absolute_error': 0.0,
            'error_type': 'numeric_error',
            'is_hallucination': False,
            'predicted': 9.68,
            'truth': 9.68
        },
        {
            'query_id': 'sol_price_change_first_half',
            'category': 'price_change',
            'correct': False,
            'absolute_error': 5.0,
            'error_type': 'numeric_error',
            'is_hallucination': False,
            'predicted': -8.57,
            'truth': -13.57
        },
        {
            'query_id': 'rank_by_sharpe_30d',
            'category': 'performance_comparison',
            'correct': False,
            'absolute_error': None,
            'error_type': 'list_mismatch',
            'is_hallucination': False,
            'predicted': ['SOL', 'ETH', 'TAO'],
            'truth': ['ETH', 'SOL', 'TAO']
        }
    ]
    
    # Grade the evaluation
    grading_report = grader.grade_evaluation(example_results)
    
    # Print the report
    grader.print_grading_report(grading_report)

if __name__ == "__main__":
    main() 