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
        
        # Initialize OpenAI client for LLM judge - REQUIRED
        if not self.llm_api_key:
            # Force load from environment
            from dotenv import load_dotenv
            load_dotenv()
            self.llm_api_key = os.getenv('OPENAI_API_KEY')
        
        if not self.llm_api_key:
            raise ValueError("❌ OPENAI_API_KEY is required! Add it to your .env file")
        
        try:
            from openai import OpenAI
            self.llm_client = OpenAI(api_key=self.llm_api_key)
            print(f"✅ Initialized OpenAI client for LLM judge evaluation")
        except ImportError:
            raise ImportError("❌ OpenAI package required! Install with: pip install openai")
        
    def _load_queries(self) -> Dict:
        """Load queries from YAML file"""
        with open(self.queries_file, 'r') as f:
            return yaml.safe_load(f)
    
    def _evaluate_with_llm_judge(self, agent_response: str, question: str, truth_value: Any, query_id: str) -> Dict:
        """Use an LLM to evaluate the agent response against the truth value"""
        
        # Create evaluation prompt
        prompt = f"""You are an expert evaluator for AI agents answering cryptocurrency analytics questions.

QUESTION: {question}

TRUTH VALUE: {truth_value}

AGENT RESPONSE: {agent_response}

Please evaluate the agent's response and return a JSON object with these exact fields:

{{
    "correct": boolean,  // true if the agent's answer matches or is very close to the truth value
    "extracted_value": // the specific value/answer the agent provided (number, date, list, etc.) or null if unclear
    "is_hallucination": boolean,  // true only if the agent made up obviously false information
    "is_refusal": boolean,  // true if the agent refused to answer (e.g., "I don't have access to this data")
    "error_type": "string",  // one of: "correct", "minor_error", "major_error", "extraction_failed", "refusal", "hallucination"
    "absolute_error": number or null,  // for numeric answers, the absolute difference from truth
    "explanation": "string"  // brief explanation of your evaluation
}}

Guidelines:
- For percentages, allow ±2% tolerance for "correct"
- For prices/returns, allow ±5% tolerance for "correct" 
- For dates, must be exact match
- For rankings, order must be exactly correct
- "refusal" is NOT a hallucination - it's honest uncertainty
- Only mark as "hallucination" if agent provides confident but false information
- If response is unclear but not obviously false, use "extraction_failed"

Return ONLY the JSON object, no other text."""


        
        try:
            response = self.llm_client.chat.completions.create(
                model="gpt-4o",  # Use full GPT-4o for evaluation
                messages=[
                    {"role": "system", "content": "You are a precise evaluator. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=300
            )
            
            result_text = response.choices[0].message.content.strip()
            
            # Clean up response - remove any markdown formatting
            if result_text.startswith("```json"):
                result_text = result_text[7:]
            if result_text.endswith("```"):
                result_text = result_text[:-3]
            result_text = result_text.strip()
            
            # Parse JSON response
            import json
            evaluation = json.loads(result_text)
            
            # Validate required fields
            required_fields = ["correct", "extracted_value", "is_hallucination", "is_refusal", "error_type", "absolute_error", "explanation"]
            for field in required_fields:
                if field not in evaluation:
                    evaluation[field] = None
            
            return evaluation
            
        except Exception as e:
            print(f"⚠️  LLM evaluation failed for {query_id}: {e}")
            if 'result_text' in locals():
                print(f"    Raw response: {result_text[:200]}...")
            # Fallback to simple evaluation
            return {
                "correct": False,
                "extracted_value": None,
                "is_hallucination": False,
                "is_refusal": "don't have access" in agent_response.lower() or "cannot provide" in agent_response.lower(),
                "error_type": "evaluation_failed",
                "absolute_error": None,
                "explanation": f"LLM evaluation failed: {e}"
            }

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
        # OpenAI API key is guaranteed to be available at this point
        
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
                return None
                
        except Exception as e:
            print(f"LLM extraction error: {e}")
            return None
    
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
        
        # Use LLM judge to evaluate the response
        category = query['category']
        evaluation = self._evaluate_with_llm_judge(
            agent_response, 
            query['question'], 
            query['truth'], 
            query_id
        )
        
        result = {
            'query_id': query_id,
            'question': query['question'],
            'category': category,
            'truth': query['truth'],
            'explanation': query.get('explanation', ''),  # May not exist after cleanup
            'agent_name': agent_name,
            'agent_response': agent_response,
            'predicted': evaluation['extracted_value'],
            'correct': evaluation['correct'],
            'absolute_error': evaluation['absolute_error'],
            'error_type': evaluation['error_type'],
            'is_hallucination': evaluation['is_hallucination'],
            'is_refusal': evaluation['is_refusal'],
            'llm_evaluation_explanation': evaluation['explanation'],
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