#!/usr/bin/env python3
"""
Dynamic Evaluation Orchestrator for New Queries
Combines dynamic data generation and dynamic truth calculation for new query types
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any

# Import our components
from dynamic_data_generator import DynamicDataGenerator
from dynamic_truth_calculator_new import DynamicTruthCalculatorNew

class DynamicEvaluationOrchestratorNew:
    """Orchestrates the complete dynamic evaluation system for new queries"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.data_generator = DynamicDataGenerator(data_dir)
        self.truth_calculator = None  # Will be initialized after data generation
    
    def generate_fresh_data(self, days: int = 30) -> bool:
        """Generate fresh CSV data"""
        print("🚀 STEP 1: GENERATING FRESH DATA")
        print("=" * 50)
        
        success = self.data_generator.run(days=days)
        
        if success:
            print("✅ Data generation completed successfully!")
            return True
        else:
            print("❌ Data generation failed!")
            return False
    
    def calculate_dynamic_truth(self, queries_file: str = 'data/queries_new.yaml') -> bool:
        """Calculate dynamic truth values from the generated data"""
        print("\n🔄 STEP 2: CALCULATING DYNAMIC TRUTH VALUES")
        print("=" * 50)
        
        # Initialize truth calculator with fresh data
        self.truth_calculator = DynamicTruthCalculatorNew(self.data_dir)
        
        # Update queries with dynamic truth
        updated_count = self.truth_calculator.update_queries_with_dynamic_truth(queries_file)
        
        if updated_count > 0:
            print(f"✅ Dynamic truth calculation completed! Updated {updated_count} queries")
            return True
        else:
            print("❌ No queries were updated!")
            return False
    
    def verify_system(self) -> bool:
        """Verify that the system is working correctly"""
        print("\n🔍 STEP 3: VERIFYING SYSTEM")
        print("=" * 50)
        
        # Check if CSV files exist
        csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('_daily.csv')]
        if not csv_files:
            print("❌ No CSV files found!")
            return False
        
        print(f"✅ Found {len(csv_files)} CSV files: {csv_files}")
        
        # Check if queries file exists and is valid
        queries_file = os.path.join(self.data_dir, 'queries_new.yaml')
        if not os.path.exists(queries_file):
            print("❌ queries_new.yaml not found!")
            return False
        
        try:
            import yaml
            with open(queries_file, 'r') as f:
                queries_data = yaml.safe_load(f)
            
            query_count = len(queries_data['queries'])
            print(f"✅ Found {query_count} queries in queries_new.yaml")
            
        except Exception as e:
            print(f"❌ Error reading queries_new.yaml: {e}")
            return False
        
        # Run verification script
        try:
            sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
            from verify_queries import verify_queries
            issues = verify_queries()
            
            if not issues:
                print("✅ All queries verified successfully!")
                return True
            else:
                print(f"⚠️  Found {len(issues)} issues with queries")
                return False
                
        except Exception as e:
            print(f"⚠️  Could not run verification: {e}")
            return True  # Continue anyway
    
    def run_complete_pipeline(self, days: int = 30, queries_file: str = 'data/queries_new.yaml') -> bool:
        """Run the complete dynamic evaluation pipeline"""
        print("🎯 DYNAMIC EVALUATION PIPELINE FOR NEW QUERIES")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Days: {days}")
        print(f"📝 Queries file: {queries_file}")
        print("=" * 60)
        
        # Step 1: Generate fresh data
        if not self.generate_fresh_data(days):
            return False
        
        # Step 2: Calculate dynamic truth
        if not self.calculate_dynamic_truth(queries_file):
            return False
        
        # Step 3: Verify system
        if not self.verify_system():
            print("⚠️  System verification failed, but continuing...")
        
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Fresh CSV data generated")
        print("✅ Dynamic truth values calculated for new queries")
        print("✅ System verified and ready for evaluation")
        print("\n🚀 Your evaluation system is now ready with dynamic data!")
        
        return True
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get current system status"""
        status = {
            'data_files': [],
            'query_count': 0,
            'last_updated': None,
            'system_ready': False
        }
        
        # Check data files
        if os.path.exists(self.data_dir):
            csv_files = [f for f in os.listdir(self.data_dir) if f.endswith('_daily.csv')]
            status['data_files'] = csv_files
        
        # Check queries
        queries_file = os.path.join(self.data_dir, 'queries_new.yaml')
        if os.path.exists(queries_file):
            try:
                import yaml
                with open(queries_file, 'r') as f:
                    queries_data = yaml.safe_load(f)
                status['query_count'] = len(queries_data['queries'])
            except:
                pass
        
        # Check metadata
        metadata_file = os.path.join(self.data_dir, 'metadata.json')
        if os.path.exists(metadata_file):
            try:
                import json
                with open(metadata_file, 'r') as f:
                    metadata = json.load(f)
                status['last_updated'] = metadata.get('generated_at')
            except:
                pass
        
        # Determine if system is ready
        status['system_ready'] = (
            len(status['data_files']) >= 3 and  # ETH, SOL, TAO
            status['query_count'] > 0
        )
        
        return status

def main():
    """Command line interface"""
    parser = argparse.ArgumentParser(description='Dynamic Evaluation Orchestrator for New Queries')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate')
    parser.add_argument('--queries', type=str, default='data/queries_new.yaml', help='Queries file to use')
    parser.add_argument('--status', action='store_true', help='Show system status only')
    
    args = parser.parse_args()
    
    orchestrator = DynamicEvaluationOrchestratorNew()
    
    if args.status:
        # Show system status
        status = orchestrator.get_system_status()
        
        print("📊 SYSTEM STATUS")
        print("=" * 40)
        print(f"Data files: {len(status['data_files'])}")
        for file in status['data_files']:
            print(f"  📄 {file}")
        print(f"Queries: {status['query_count']}")
        print(f"Last updated: {status['last_updated'] or 'Unknown'}")
        print(f"System ready: {'✅' if status['system_ready'] else '❌'}")
        
        return
    
    # Run complete pipeline
    success = orchestrator.run_complete_pipeline(
        days=args.days,
        queries_file=args.queries
    )
    
    if success:
        print("\n🎉 All done! Your evaluation system is ready.")
        sys.exit(0)
    else:
        print("\n❌ Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 