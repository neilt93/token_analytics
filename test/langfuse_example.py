#!/usr/bin/env python3
"""
Langfuse Integration Example
Demonstrates how to integrate Langfuse tracking with token analytics evaluations
"""

import os
import json
import sys
from datetime import datetime

# Add the parent directory to the path to import scripts
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from scripts.langfuse_integration import LangfuseTokenAnalyticsTracker

def create_sample_evaluation_data():
    """Create sample evaluation data for demonstration"""
    
    return {
        "agent_name": "Sample AI Agent",
        "total_queries": 15,
        "correct_answers": 12,
        "accuracy_percentage": 80.0,
        "hallucination_rate": 6.7,
        "average_absolute_error": 0.01,
        "results": [
            {
                "query_id": "easy_1",
                "category": "Percentage Threshold",
                "question": "What is the percentage change in SOL price over the last 7 days?",
                "truth": 5.2,
                "predicted": 5.2,
                "correct": True,
                "error_type": None,
                "is_hallucination": False,
                "absolute_error": 0.0
            },
            {
                "query_id": "hard_1",
                "category": "Technical Indicators",
                "question": "What is the 20-day moving average for ETH?",
                "truth": 1850.5,
                "predicted": 1900.0,
                "correct": False,
                "error_type": "calculation_error",
                "is_hallucination": False,
                "absolute_error": 49.5
            },
            {
                "query_id": "easy_2",
                "category": "Volume Analysis",
                "question": "Which token had the highest trading volume yesterday?",
                "truth": "ETH",
                "predicted": "SOL",
                "correct": False,
                "error_type": "wrong_answer",
                "is_hallucination": True,
                "absolute_error": None
            }
        ]
    }

def create_sample_responses():
    """Create sample agent responses"""
    
    return {
        "easy_1": "The percentage change in SOL price over the last 7 days is 5.2%.",
        "hard_1": "The 20-day moving average for ETH is approximately $1900.",
        "easy_2": "SOL had the highest trading volume yesterday with $2.5 billion in volume."
    }

def demonstrate_basic_tracking():
    """Demonstrate basic Langfuse tracking"""
    
    print("🚀 Langfuse Integration Demo")
    print("=" * 40)
    
    # Initialize tracker
    tracker = LangfuseTokenAnalyticsTracker()
    
    # Create sample data
    evaluation_data = create_sample_evaluation_data()
    responses = create_sample_responses()
    
    print(f"📊 Creating trace for {evaluation_data['agent_name']}...")
    
    # Create main evaluation trace
    trace_id = tracker.create_evaluation_trace(
        agent_name=evaluation_data["agent_name"],
        evaluation_results=evaluation_data,
        agent_responses=responses
    )
    
    print(f"✅ Created trace: {trace_id}")
    
    # Create difficulty analysis
    difficulty_trace_id = tracker.track_easy_vs_hard_performance(
        evaluation_data,
        evaluation_data["agent_name"]
    )
    
    print(f"✅ Created difficulty analysis: {difficulty_trace_id}")
    
    return trace_id, difficulty_trace_id

def demonstrate_agent_comparison():
    """Demonstrate agent comparison tracking"""
    
    print("\n🔄 Agent Comparison Demo")
    print("=" * 30)
    
    tracker = LangfuseTokenAnalyticsTracker()
    
    # Create sample comparison data
    comparison_data = {
        "GPT-4": {
            "evaluation_summary": {
                "accuracy_percentage": 85.0,
                "hallucination_rate": 5.0
            }
        },
        "Claude": {
            "evaluation_summary": {
                "accuracy_percentage": 78.0,
                "hallucination_rate": 8.0
            }
        },
        "Perplexity": {
            "evaluation_summary": {
                "accuracy_percentage": 82.0,
                "hallucination_rate": 6.0
            }
        }
    }
    
    agent_names = ["GPT-4", "Claude", "Perplexity"]
    
    print("📊 Creating agent comparison trace...")
    
    comparison_trace_id = tracker.track_agent_comparison(
        comparison_data,
        agent_names
    )
    
    print(f"✅ Created comparison trace: {comparison_trace_id}")
    
    return comparison_trace_id

def demonstrate_custom_metrics():
    """Demonstrate custom metric tracking"""
    
    print("\n📈 Custom Metrics Demo")
    print("=" * 25)
    
    tracker = LangfuseTokenAnalyticsTracker()
    
    # Create a custom trace for specific metrics
    trace_id = f"custom_metrics_{int(datetime.now().timestamp())}"
    
    trace = tracker.langfuse.trace(
        id=trace_id,
        name="Custom Token Analytics Metrics",
        metadata={
            "analysis_type": "custom_metrics",
            "timestamp": datetime.now().isoformat()
        }
    )
    
    # Add custom scores
    trace.score(
        name="cost_per_evaluation",
        value=0.15,  # $0.15 per evaluation
        comment="Average cost per evaluation"
    )
    
    trace.score(
        name="response_time_avg",
        value=0.85,  # 85% of responses under 2 seconds
        comment="85% of responses under 2 seconds"
    )
    
    trace.score(
        name="user_satisfaction",
        value=0.92,  # 92% satisfaction rate
        comment="User satisfaction score"
    )
    
    # Add category-specific metrics
    trace.score(
        name="percentage_threshold_accuracy",
        value=0.95,  # 95% accuracy on percentage questions
        comment="Percentage threshold questions accuracy"
    )
    
    trace.score(
        name="technical_indicators_accuracy",
        value=0.78,  # 78% accuracy on technical questions
        comment="Technical indicators questions accuracy"
    )
    
    tracker.langfuse.flush()
    
    print(f"✅ Created custom metrics trace: {trace_id}")
    
    return trace_id

def main():
    """Main demonstration function"""
    
    print("🎯 Langfuse Integration Examples")
    print("=" * 40)
    
    try:
        # Check if Langfuse credentials are configured
        if not os.getenv("LANGFUSE_PUBLIC_KEY") or not os.getenv("LANGFUSE_SECRET_KEY"):
            print("⚠️  Langfuse credentials not found!")
            print("Please add to your .env file:")
            print("LANGFUSE_PUBLIC_KEY=your_public_key")
            print("LANGFUSE_SECRET_KEY=your_secret_key")
            print("\nGet your credentials from: https://cloud.langfuse.com")
            return
        
        # Run demonstrations
        trace_id, difficulty_id = demonstrate_basic_tracking()
        comparison_id = demonstrate_agent_comparison()
        custom_id = demonstrate_custom_metrics()
        
        print("\n🎉 All demonstrations completed!")
        print(f"📊 Traces created:")
        print(f"   • Main evaluation: {trace_id}")
        print(f"   • Difficulty analysis: {difficulty_id}")
        print(f"   • Agent comparison: {comparison_id}")
        print(f"   • Custom metrics: {custom_id}")
        
        print("\n📋 Next steps:")
        print("1. View traces in Langfuse dashboard")
        print("2. Set up alerts for performance drops")
        print("3. Create custom dashboards")
        print("4. Integrate with your actual evaluations")
        
    except ImportError as e:
        print(f"❌ Error: {e}")
        print("Please install Langfuse: pip install langfuse")
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check your Langfuse credentials and connection")

if __name__ == "__main__":
    main() 