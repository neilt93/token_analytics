import yaml
import pandas as pd
import json
import re
import requests
from datetime import datetime
from typing import Dict, List, Any, Union
import numpy as np
import os

class TokenAnalyticsEvaluator:
    """
    Automated evaluator for token analytics AI agents
    Tests agents against real market data benchmarks
    """
    
    def __init__(self, queries_file: str = 'data/queries.yaml', llm_api_key: str = None):
        """
        Initialize evaluator with benchmark queries
        
        Args:
            queries_file: Path to YAML file containing queries and truth values
            llm_api_key: API key for LLM parsing (optional)
        """
        self.queries_file = queries_file
        self.queries = self._load_queries()
        self.results = []
        self.llm_api_key = llm_api_key or os.getenv('OPENAI_API_KEY')
        
    def _load_queries(self) -> Dict:
        """Load queries from YAML file"""
        with open(self.queries_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _extract_with_llm(self, agent_response: str, question: str, category: str, expected_type: str) -> Any:
        """
        Use LLM to extract structured data from agent response
        
        Args:
            agent_response: Raw response from agent
            question: Original question asked
            category: Question category
            expected_type: Expected data type (number, percentage, date, token, ranking)
            
        Returns:
            Extracted value in appropriate type
        """
        if not self.llm_api_key:
            # Fallback to regex if no LLM API key
            return self._extract_with_regex_fallback(agent_response, expected_type)
        
        try:
            # Create parsing prompt
            system_prompt = f"""You are a data extraction specialist. Extract the specific answer from the agent's response.

Question: {question}
Category: {category}
Expected type: {expected_type}

Extract ONLY the answer in the appropriate format:
- For numbers: return just the number (e.g., 42.5)
- For percentages: return just the number (e.g., 15.3 for 15.3%)
- For dates: return YYYY-MM-DD format
- For tokens: return the token symbol (SOL, ETH, TAO)
- For rankings: return list of tokens in order (e.g., ["ETH", "SOL", "TAO"])
- If no clear answer found, return null

Respond with ONLY the extracted value, no explanation."""

            headers = {
                "Authorization": f"Bearer {self.llm_api_key}",
                "Content-Type": "application/json"
            }
            
            data = {
                "model": "gpt-4o-mini",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Agent response: {agent_response}"}
                ],
                "temperature": 0.1,
                "max_tokens": 50
            }
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=10
            )
            
            if response.status_code == 200:
                extracted_text = response.json()["choices"][0]["message"]["content"].strip()
                
                # Parse based on expected type
                if expected_type == "number" or expected_type == "percentage":
                    try:
                        return float(extracted_text)
                    except ValueError:
                        return None
                elif expected_type == "date":
                    # Validate date format
                    if re.match(r'\d{4}-\d{2}-\d{2}', extracted_text):
                        return extracted_text
                    return None
                elif expected_type == "token":
                    if extracted_text.upper() in ['SOL', 'ETH', 'TAO']:
                        return extracted_text.upper()
                    return None
                elif expected_type == "ranking":
                    try:
                        # Parse JSON list
                        if extracted_text.startswith('[') and extracted_text.endswith(']'):
                            tokens = json.loads(extracted_text)
                            if all(t.upper() in ['SOL', 'ETH', 'TAO'] for t in tokens):
                                return [t.upper() for t in tokens]
                        return None
                    except:
                        return None
                else:
                    return extracted_text
            else:
                print(f"LLM API Error: {response.status_code}")
                return self._extract_with_regex_fallback(agent_response, expected_type)
                
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return self._extract_with_regex_fallback(agent_response, expected_type)
    
    def _extract_with_regex_fallback(self, text: str, expected_type: str) -> Any:
        """
        Fallback regex extraction when LLM is not available
        """
        if not text:
            return None
            
        if expected_type == "percentage":
            # Look for percentage pattern with % symbol
            percentage_pattern = r'([+-]?([0-9]*[.])?[0-9]+)\s*%'
            match = re.search(percentage_pattern, text)
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
            
            # Look for percentage words
            percentage_words_pattern = r'([+-]?([0-9]*[.])?[0-9]+)\s*(?:percent|percentage)'
            match = re.search(percentage_words_pattern, text.lower())
            if match:
                try:
                    return float(match.group(1))
                except ValueError:
                    pass
                    
        elif expected_type == "number":
            # Remove dollar signs and common words
            text = text.lower()
            text = re.sub(r'\$', '', text)
            text = re.sub(r'\b(about|approximately|roughly|around)\b', '', text)
            
            # For price changes, look for decrease/increase context
            is_negative = False
            if 'decrease' in text or 'decreased' in text or 'down' in text:
                is_negative = True
            elif 'increase' in text or 'increased' in text or 'up' in text:
                is_negative = False
            
            # Find numbers (including decimals and negatives)
            number_pattern = r'([+-]?([0-9]*[.])?[0-9]+)'
            match = re.search(number_pattern, text)
            if match:
                try:
                    value = float(match.group(1))
                    if is_negative and value > 0:
                        return -value
                    return value
                except ValueError:
                    pass
                    
        elif expected_type == "date":
            # Look for YYYY-MM-DD pattern
            match = re.search(r'\d{4}-\d{2}-\d{2}', text)
            if match:
                return match.group(0)
                
        elif expected_type == "token":
            text = text.upper()
            tokens = ['SOL', 'ETH', 'TAO']
            for token in tokens:
                if token in text:
                    return token
                    
        elif expected_type == "ranking":
            text = text.upper()
            tokens = ['SOL', 'ETH', 'TAO']
            found_tokens = []
            
            # Remove common ranking words and symbols
            text = re.sub(r'\b(ranked|ranking|order|by|as|follows?|is|are)\b', '', text)
            text = re.sub(r'[->>\-\s]+', ' ', text)
            text = re.sub(r'[,\s]+', ' ', text)
            
            # Split by spaces and find tokens in order
            words = text.split()
            for word in words:
                if word in tokens and word not in found_tokens:
                    found_tokens.append(word)
            
            # If we found tokens but not all 3, try a different approach
            if found_tokens and len(found_tokens) < 3:
                for token in tokens:
                    if token in text and token not in found_tokens:
                        found_tokens.append(token)
            
            return found_tokens if found_tokens else None
        
        return None
    
    def _extract_numeric_percentage(self, text: str) -> Union[float, None]:
        """
        Extract percentage value from text response
        Handles formats like 'about 9.7%', 'approximately 45.2%', 'roughly 64.5%'
        """
        if not text:
            return None
            
        # Use LLM for extraction
        return self._extract_with_llm(text, "percentage_threshold", "percentage_threshold", "percentage")
    
    def _extract_plain_number(self, text: str) -> Union[float, None]:
        """
        Extract any numeric value, ignoring $ signs and common words
        Handles formats like '$33.15', 'about 2.31', 'approximately -1.16'
        """
        if not text:
            return None
            
        # Use LLM for extraction
        return self._extract_with_llm(text, "price_change", "price_change", "number")
    
    def _extract_number_from_text(self, text: str) -> Union[float, None]:
        """
        Legacy function - now delegates to appropriate extractor
        """
        return self._extract_plain_number(text)
    
    def _extract_token_from_text(self, text: str) -> Union[str, None]:
        """
        Extract token symbol from text response
        """
        if not text:
            return None
            
        # Use LLM for extraction
        return self._extract_with_llm(text, "volatility", "volatility", "token")
    
    def _extract_token_name(self, text: str, token_list: List[str] = None) -> Union[str, None]:
        """
        Extract token name from text response with fallback
        """
        if not text:
            return None
            
        if token_list is None:
            token_list = ['SOL', 'ETH', 'TAO']
            
        # Use LLM for extraction
        return self._extract_with_llm(text, "volatility", "volatility", "token")
    
    def _extract_date_from_text(self, text: str) -> Union[str, None]:
        """
        Extract date from text response
        """
        if not text:
            return None
            
        # Use LLM for extraction
        return self._extract_with_llm(text, "price_analysis", "price_analysis", "date")
    
    def _normalize_ranking(self, text: str) -> Union[List[str], None]:
        """
        Extract and normalize ranking from text response
        Handles formats like 'ETH, SOL, TAO', 'ETH->SOL->TAO', 'ETH > SOL > TAO'
        """
        if not text:
            return None
            
        # Use LLM for extraction
        return self._extract_with_llm(text, "performance_comparison", "performance_comparison", "ranking")
    
    def _extract_list_from_text(self, text: str) -> Union[List[str], None]:
        """
        Legacy function - now delegates to normalize_ranking
        """
        return self._normalize_ranking(text)
    
    def _calculate_accuracy(self, predicted: Any, truth: Any, category: str) -> Dict:
        """
        Calculate accuracy metrics for different response types
        """
        result = {
            'correct': False,
            'absolute_error': None,
            'error_type': None
        }
        
        # Handle numeric responses (percentages, price changes, etc.)
        if isinstance(truth, (int, float)) and isinstance(predicted, (int, float)):
            result['absolute_error'] = abs(predicted - truth)
            result['correct'] = result['absolute_error'] <= 1.0  # Within 1% tolerance
            result['error_type'] = 'numeric_error'
            
        # Handle string responses (token names, dates)
        elif isinstance(truth, str) and isinstance(predicted, str):
            result['correct'] = predicted.upper() == truth.upper()
            result['error_type'] = 'string_mismatch'
            
        # Handle list responses (rankings)
        elif isinstance(truth, list) and isinstance(predicted, list):
            result['correct'] = predicted == truth
            result['error_type'] = 'list_mismatch'
            
        # Handle mixed types or missing predictions
        else:
            result['error_type'] = 'type_mismatch'
            
        return result
    
    def evaluate_agent_response(self, query_id: str, agent_response: str, agent_name: str = "Unknown") -> Dict:
        """
        Evaluate a single agent response against the truth
        
        Args:
            query_id: ID of the query being evaluated
            agent_response: Raw text response from the agent
            agent_name: Name/identifier of the agent
            
        Returns:
            Dictionary with evaluation results
        """
        # Find the query
        query = None
        for q in self.queries['queries']:
            if q['id'] == query_id:
                query = q
                break
                
        if not query:
            raise ValueError(f"Query ID {query_id} not found")
        
        # Extract predicted value based on category and question type
        predicted = None
        category = query['category']
        question = query['question'].lower()
        
        # Use LLM-based extraction for all categories
        if category == 'percentage_threshold':
            predicted = self._extract_with_llm(agent_response, query['question'], category, "percentage")
        elif category == 'price_change':
            predicted = self._extract_with_llm(agent_response, query['question'], category, "number")
        elif category == 'volatility':
            # For volatility, check if it's asking for a token name or numeric range
            if 'most volatile' in question or 'which token' in question:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "token")
            else:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "number")
        elif category == 'volatility_stat':
            # For volatility statistics, extract numbers
            predicted = self._extract_with_llm(agent_response, query['question'], category, "number")
        elif category in ['volume_analysis', 'performance_comparison']:
            if 'ranking' in question or 'rank' in question:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "ranking")
            else:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "token")
        elif category == 'price_analysis':
            if 'date' in question:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "date")
            elif 'ranking' in question or 'rank' in question:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "ranking")
            else:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "token")
        elif category in ['conditional_threshold', 'streak_analysis', 'rolling_stats', 'conditional_volume']:
            # For these categories, try to extract the most relevant type
            if 'percentage' in question or '%' in question:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "percentage")
            elif 'date' in question:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "date")
            elif 'token' in question or any(token in question for token in ['SOL', 'ETH', 'TAO']):
                predicted = self._extract_with_llm(agent_response, query['question'], category, "token")
            else:
                predicted = self._extract_with_llm(agent_response, query['question'], category, "number")
        else:
            # Default to number extraction
            predicted = self._extract_with_llm(agent_response, query['question'], category, "number")
        
        # Calculate accuracy
        accuracy = self._calculate_accuracy(predicted, query['truth'], category)
        
        # Determine if response is a hallucination (more nuanced)
        is_hallucination = False
        if predicted is None:
            is_hallucination = True
        elif isinstance(predicted, (int, float)):
            # For percentages, flag if > 100 or < -100
            if category == 'percentage_threshold' and (predicted > 100 or predicted < 0):
                is_hallucination = True
            # For price changes, flag if > 1000% or < -1000%
            elif category == 'price_change' and (predicted > 1000 or predicted < -1000):
                is_hallucination = True
            # For volatility ranges, flag if > 1000
            elif category == 'volatility' and predicted > 1000:
                is_hallucination = True
        elif isinstance(predicted, str):
            # Flag if token name is not valid
            if predicted not in ['SOL', 'ETH', 'TAO', '2025-06-11', '2025-06-23']:
                is_hallucination = True
        elif isinstance(predicted, list):
            # Flag if ranking contains invalid tokens
            valid_tokens = ['SOL', 'ETH', 'TAO']
            if not all(token in valid_tokens for token in predicted):
                is_hallucination = True
        
        result = {
            'query_id': query_id,
            'question': query['question'],
            'category': category,
            'truth': query['truth'],
            'explanation': query['explanation'],
            'agent_name': agent_name,
            'agent_response': agent_response,
            'predicted': predicted,
            'correct': accuracy['correct'],
            'absolute_error': accuracy['absolute_error'],
            'error_type': accuracy['error_type'],
            'is_hallucination': is_hallucination,
            'timestamp': datetime.now().isoformat()
        }
        
        return result
    
    def run_evaluation(self, agent_responses: Dict[str, str], agent_name: str = "Unknown") -> Dict:
        """
        Run full evaluation on all queries
        
        Args:
            agent_responses: Dictionary mapping query_id to agent response
            agent_name: Name/identifier of the agent
            
        Returns:
            Summary statistics and detailed results
        """
        results = []
        
        for query in self.queries['queries']:
            query_id = query['id']
            
            if query_id in agent_responses:
                result = self.evaluate_agent_response(
                    query_id, 
                    agent_responses[query_id], 
                    agent_name
                )
                results.append(result)
            else:
                # Missing response
                result = {
                    'query_id': query_id,
                    'question': query['question'],
                    'category': query['category'],
                    'truth': query['truth'],
                    'agent_name': agent_name,
                    'agent_response': None,
                    'predicted': None,
                    'correct': False,
                    'absolute_error': None,
                    'error_type': 'missing_response',
                    'is_hallucination': False,
                    'timestamp': datetime.now().isoformat()
                }
                results.append(result)
        
        # Calculate summary statistics
        total_queries = len(results)
        correct_answers = sum(1 for r in results if r['correct'])
        hallucinations = sum(1 for r in results if r['is_hallucination'])
        
        # Calculate average absolute error for numeric responses
        numeric_errors = [r['absolute_error'] for r in results if r['absolute_error'] is not None]
        avg_absolute_error = np.mean(numeric_errors) if numeric_errors else 0
        
        summary = {
            'agent_name': agent_name,
            'total_queries': total_queries,
            'correct_answers': correct_answers,
            'accuracy_percentage': (correct_answers / total_queries) * 100 if total_queries > 0 else 0,
            'hallucination_count': hallucinations,
            'hallucination_rate': (hallucinations / total_queries) * 100 if total_queries > 0 else 0,
            'average_absolute_error': avg_absolute_error,
            'results': results,
            'timestamp': datetime.now().isoformat()
        }
        
        return summary
    
    def print_summary(self, summary: Dict):
        """Print formatted evaluation summary"""
        print(f"\n{'='*80}")
        print(f"📊 EVALUATION SUMMARY: {summary['agent_name']}")
        print(f"{'='*80}")
        print(f"✅ Correct Answers: {summary['correct_answers']}/{summary['total_queries']} ({summary['accuracy_percentage']:.1f}%)")
        print(f"❌ Hallucinations: {summary['hallucination_count']} ({summary['hallucination_rate']:.1f}%)")
        print(f"📏 Avg Absolute Error: {summary['average_absolute_error']:.2f}")
        print(f"⏰ Evaluation Time: {summary['timestamp']}")
        
        # Category breakdown
        categories = {}
        for result in summary['results']:
            cat = result['category']
            if cat not in categories:
                categories[cat] = {'total': 0, 'correct': 0}
            categories[cat]['total'] += 1
            if result['correct']:
                categories[cat]['correct'] += 1
        
        print(f"\n📈 Performance by Category:")
        for cat, stats in categories.items():
            accuracy = (stats['correct'] / stats['total']) * 100
            print(f"   • {cat.replace('_', ' ').title()}: {stats['correct']}/{stats['total']} ({accuracy:.1f}%)")
    
    def save_results(self, summary: Dict, filename: str = None):
        """Save evaluation results to JSON file"""
        if filename is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"evaluation_results_{summary['agent_name']}_{timestamp}.json"
        
        with open(filename, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"\n💾 Results saved to: {filename}")

def main():
    """Example usage of the evaluator"""
    evaluator = TokenAnalyticsEvaluator()
    
    # Example agent responses (replace with actual agent responses)
    example_responses = {
        'pct_tao_above_400': "TAO was above $400 for approximately 13% of the days.",
        'sol_price_change_30d': "SOL's price decreased by about 2.3% over the 30-day period.",
        'highest_avg_volume': "ETH had the highest average daily volume.",
        'eth_highest_close_date': "ETH had its highest close on 2025-06-11.",
        'rank_by_avg_close': "Ranked by average close price: ETH, TAO, SOL."
    }
    
    # Run evaluation
    summary = evaluator.run_evaluation(example_responses, "Example Agent")
    
    # Print results
    evaluator.print_summary(summary)
    
    # Save results
    evaluator.save_results(summary)

if __name__ == "__main__":
    main() 