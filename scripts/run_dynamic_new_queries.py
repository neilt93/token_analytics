#!/usr/bin/env python3
"""
Run Dynamic Pipeline for New Queries
Simple script to run the complete dynamic evaluation pipeline for new queries
"""

import sys
import os

# Add the dynamic_data_generation directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'dynamic_data_generation'))

from dynamic_evaluation_orchestrator_new import DynamicEvaluationOrchestratorNew

def main():
    """Run the complete dynamic pipeline for new queries"""
    print("🚀 RUNNING DYNAMIC PIPELINE FOR NEW QUERIES")
    print("=" * 60)
    
    # Initialize orchestrator
    orchestrator = DynamicEvaluationOrchestratorNew()
    
    # Show current status
    print("\n📊 Current System Status:")
    status = orchestrator.get_system_status()
    print(f"Data files: {len(status['data_files'])}")
    print(f"Queries: {status['query_count']}")
    print(f"System ready: {'✅' if status['system_ready'] else '❌'}")
    
    # Run the complete pipeline
    success = orchestrator.run_complete_pipeline(
        days=30,
        queries_file='data/queries_new.yaml'
    )
    
    if success:
        print("\n🎉 SUCCESS! Dynamic pipeline completed.")
        print("Your new queries are ready for evaluation!")
        return 0
    else:
        print("\n❌ FAILED! Dynamic pipeline failed.")
        return 1

if __name__ == "__main__":
    sys.exit(main()) 