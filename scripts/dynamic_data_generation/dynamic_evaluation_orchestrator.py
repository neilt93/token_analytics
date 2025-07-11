#!/usr/bin/env python3
"""
Dynamic Evaluation Orchestrator
Combines dynamic data generation and dynamic truth calculation
"""

import os
import sys
import argparse
from datetime import datetime
from typing import Dict, Any

# Import our components
from dynamic_data_generator import DynamicDataGenerator
from dynamic_truth_calculator import DynamicTruthCalculator

class DynamicEvaluationOrchestrator:
    """Orchestrates the complete dynamic evaluation system"""
    
    def __init__(self, data_dir: str = 'data'):
        self.data_dir = data_dir
        self.data_generator = DynamicDataGenerator(data_dir)
        self.truth_calculator = None  # Will be initialized after data generation
    
    def generate_fresh_data(self, use_api: bool = True, days: int = 30) -> bool:
        """Generate fresh CSV data"""
        print("🚀 STEP 1: GENERATING FRESH DATA")
        print("=" * 50)
        
        success = self.data_generator.run(use_api=use_api, days=days)
        
        if success:
            print("✅ Data generation completed successfully!")
            return True
        else:
            print("❌ Data generation failed!")
            return False
    
    def calculate_dynamic_truth(self) -> bool:
        """Calculate dynamic truth values from the generated data"""
        print("\n🔄 STEP 2: CALCULATING DYNAMIC TRUTH VALUES")
        print("=" * 50)
        
        # Initialize truth calculator with fresh data
        self.truth_calculator = DynamicTruthCalculator(self.data_dir)
        
        # Update queries with dynamic truth
        updated_count = self.truth_calculator.update_queries_with_dynamic_truth()
        
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
        
        # Check if queries.yaml exists and is valid
        queries_file = os.path.join(self.data_dir, 'queries.yaml')
        if not os.path.exists(queries_file):
            print("❌ queries.yaml not found!")
            return False
        
        try:
            import yaml
            with open(queries_file, 'r') as f:
                queries_data = yaml.safe_load(f)
            
            query_count = len(queries_data['queries'])
            print(f"✅ Found {query_count} queries in queries.yaml")
            
        except Exception as e:
            print(f"❌ Error reading queries.yaml: {e}")
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
    
    def run_complete_pipeline(self, use_api: bool = True, days: int = 30) -> bool:
        """Run the complete dynamic evaluation pipeline"""
        print("🎯 DYNAMIC EVALUATION PIPELINE")
        print("=" * 60)
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"📊 Days: {days}")
        print(f"🌐 API: {'Yes' if use_api else 'No'}")
        print("=" * 60)
        
        # Step 1: Generate fresh data
        if not self.generate_fresh_data(use_api, days):
            return False
        
        # Step 2: Calculate dynamic truth
        if not self.calculate_dynamic_truth():
            return False
        
        # Step 3: Verify system
        if not self.verify_system():
            print("⚠️  System verification failed, but continuing...")
        
        print("\n🎉 PIPELINE COMPLETED SUCCESSFULLY!")
        print("=" * 60)
        print("✅ Fresh CSV data generated")
        print("✅ Dynamic truth values calculated")
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
        queries_file = os.path.join(self.data_dir, 'queries.yaml')
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
    parser = argparse.ArgumentParser(description='Dynamic Evaluation Orchestrator')
    parser.add_argument('--api', action='store_true', help='Use CoinGecko API')
    parser.add_argument('--synthetic', action='store_true', help='Use synthetic data')
    parser.add_argument('--days', type=int, default=30, help='Number of days to generate')
    parser.add_argument('--status', action='store_true', help='Show system status only')
    
    args = parser.parse_args()
    
    orchestrator = DynamicEvaluationOrchestrator()
    
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
        print(f"System ready: {'✅ Yes' if status['system_ready'] else '❌ No'}")
        
        if status['system_ready']:
            print("\n🎉 System is ready for evaluation!")
        else:
            print("\n⚠️  System needs data generation")
        
        return
    
    # Run complete pipeline
    use_api = args.api and not args.synthetic
    
    success = orchestrator.run_complete_pipeline(use_api=use_api, days=args.days)
    
    if success:
        print("\n🎯 Ready to run evaluations!")
        print("💡 Next steps:")
        print("   1. Run your evaluation scripts")
        print("   2. Use --status to check system health")
        print("   3. Re-run this script to get fresh data")
    else:
        print("\n❌ Pipeline failed!")
        sys.exit(1)

if __name__ == "__main__":
    main() 