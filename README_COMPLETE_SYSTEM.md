# Token Analytics Evaluation System

A comprehensive evaluation framework for testing AI agents on cryptocurrency analytics questions using real market data.

## 🎯 Overview

This system provides:
- **LLM-based evaluation** with robust data extraction
- **30 diverse analytics queries** covering multiple categories
- **Comprehensive grading scale** with nuanced scoring
- **Real market data** from SOL, ETH, and TAO tokens
- **Automated testing** and performance analysis

## 📁 System Components

### Core Files
- `eval.py` - Main evaluation engine with LLM-based extraction
- `grading_scale.py` - Comprehensive grading system
- `data/queries.yaml` - 30 analytics queries with truth values
- `data/*.csv` - Historical market data for SOL, ETH, TAO

### Test Files
- `test/test_llm_eval.py` - LLM evaluation testing
- `test/test_new_queries.py` - New queries validation
- `test/test_grading_scale.py` - Grading system testing
- `test/perplexity_evaluation_results.json` - Sample results

### Scripts
- `scripts/calculate_new_queries.py` - Truth value calculation
- `run_evaluations.py` - Main evaluation runner

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Install dependencies
pip install -r requirements.txt

# Set OpenAI API key (optional, for LLM extraction)
export OPENAI_API_KEY="your-api-key-here"
```

### 2. Run Complete Evaluation
```bash
# Run evaluation with grading
python run_evaluations.py --agent-name "Your Agent" --output results.json
```

### 3. Test Individual Components
```bash
# Test LLM evaluation
python test/test_llm_eval.py

# Test new queries
python test/test_new_queries.py

# Test grading scale
python test/test_grading_scale.py
```

## 📊 Query Categories

### Percentage Threshold (6 queries)
- Days above/below price thresholds
- Conditional percentage calculations
- Example: "What percentage of days was SOL below $140?"

### Price Change (4 queries)
- Period-over-period price changes
- First/second half comparisons
- Example: "What was SOL's price change during the first half?"

### Volatility Analysis (4 queries)
- Intraday ranges and swings
- Standard deviation calculations
- Example: "How many days did ETH's range exceed 5%?"

### Performance Comparison (6 queries)
- Ranking by various metrics
- Sharpe ratios, returns, volatility
- Example: "Rank SOL, ETH, TAO by 30-day Sharpe ratio"

### Rolling Statistics (4 queries)
- Moving averages and rolling returns
- Streak analysis and patterns
- Example: "What was TAO's highest 5-day rolling return?"

### Volume Analysis (3 queries)
- Volume patterns and correlations
- Conditional volume calculations
- Example: "What was ETH's average volume when SOL dropped >5%?"

### Conditional Analysis (3 queries)
- Multi-token conditional logic
- Cross-asset correlations
- Example: "What percentage of days did SOL close above $160 when ETH was above $2700?"

## 🎓 Grading Scale

### Grade Levels
- **A+ (95-100)**: Excellent accuracy and precision
- **A (90-94)**: Very good performance
- **A- (85-89)**: Good performance with minor errors
- **B+ (80-84)**: Above average
- **B (75-79)**: Average performance
- **B- (70-74)**: Below average
- **C+ (65-69)**: Marginal performance
- **C (60-64)**: Acceptable
- **C- (55-59)**: Poor performance
- **D+ (50-54)**: Very poor
- **D (45-49)**: Unsatisfactory
- **D- (40-44)**: Very unsatisfactory
- **F (0-39)**: Failing

### Scoring Components
1. **Accuracy Score (60%)**: Based on correctness and error magnitude
2. **Precision Score (25%)**: Specificity of response format
3. **Quality Score (15%)**: Response characteristics and penalties

### Error Penalties
- **Hallucination**: Automatic F grade
- **Missing Response**: 0% score
- **Type Mismatch**: 20% score
- **String Mismatch**: 30% score
- **List Mismatch**: 40% score

## 🔧 LLM-Based Evaluation

### Features
- **Robust Extraction**: Uses GPT-4o-mini for structured data extraction
- **Fallback System**: Regex-based extraction when LLM unavailable
- **Multi-format Support**: Numbers, percentages, dates, tokens, rankings
- **Error Handling**: Graceful degradation and detailed feedback

### Extraction Types
```python
# Numeric extraction
"SOL decreased by 13.57%" → 13.57

# Percentage extraction  
"40% of days" → 40.0

# Date extraction
"June 9, 2025" → "2025-06-09"

# Token extraction
"Ethereum had the highest volume" → "ETH"

# Ranking extraction
"ETH, SOL, TAO" → ["ETH", "SOL", "TAO"]
```

## 📈 Sample Results

### Perplexity AI Evaluation
```
📊 ANALYTICS GRADING REPORT
================================================================================
🎯 Overall Grade: F (24.2/100)
📝 Total Questions: 20

📈 Grade Distribution:
   F: 20 questions (100.0%)

📊 Performance by Category:
   • Percentage Threshold: F (24.2/100) - 6 questions
   • Price Change: F (24.2/100) - 4 questions
   • Volatility: F (24.2/100) - 4 questions
   • Performance Comparison: F (24.2/100) - 6 questions

📋 Summary Statistics:
   • Average Accuracy Score: 24.2/100
   • Average Precision Score: 24.2/100
   • Average Quality Score: 24.2/100
   • Questions with Penalties: 20
   • Questions with Bonuses: 0
```

## 🛠️ Advanced Usage

### Custom Agent Integration
```python
from eval import TokenAnalyticsEvaluator
from grading_scale import AnalyticsGradingScale

# Initialize evaluator
evaluator = TokenAnalyticsEvaluator()

# Your agent responses
agent_responses = {
    'pct_sol_below_140_30d': "SOL was below $140 for 9.68% of days",
    'sol_price_change_first_half': "SOL decreased by 13.57%",
    # ... more responses
}

# Run evaluation
summary = evaluator.run_evaluation(agent_responses, "Your Agent")

# Apply grading scale
grader = AnalyticsGradingScale()
grading_report = grader.grade_evaluation(summary['results'])

# Print results
grader.print_grading_report(grading_report)
```

### Custom Query Addition
```python
# Add new query to queries.yaml
new_query = {
    'id': 'custom_query',
    'question': 'What was the average daily volume of SOL?',
    'category': 'volume_analysis',
    'truth': 15000000000.0,
    'explanation': 'Calculated from historical data'
}

# Calculate truth values
python scripts/calculate_new_queries.py
```

### Batch Evaluation
```python
# Evaluate multiple agents
agents = {
    'Agent A': agent_a_responses,
    'Agent B': agent_b_responses,
    'Agent C': agent_c_responses
}

for agent_name, responses in agents.items():
    summary = evaluator.run_evaluation(responses, agent_name)
    grading_report = grader.grade_evaluation(summary['results'])
    print(f"\n{agent_name}: {grading_report['overall_grade']} ({grading_report['overall_score']:.1f}/100)")
```

## 📊 Performance Metrics

### Accuracy Metrics
- **Correct Answers**: Exact matches within tolerance
- **Absolute Error**: Magnitude of numeric errors
- **Error Types**: Classification of error types

### Quality Metrics
- **Hallucination Rate**: Percentage of fabricated responses
- **Precision Rate**: Specificity of responses
- **Completeness**: Coverage of all queries

### Category Performance
- **Per-category accuracy**: Performance breakdown
- **Difficulty analysis**: Which categories are hardest
- **Improvement tracking**: Progress over time

## 🔍 Troubleshooting

### Common Issues
1. **LLM API Errors**: Check API key and network connection
2. **Data Loading**: Verify CSV files are present
3. **Query Format**: Ensure YAML syntax is correct
4. **Memory Issues**: Large datasets may require optimization

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual components
evaluator = TokenAnalyticsEvaluator()
result = evaluator.evaluate_agent_response('pct_sol_below_140_30d', "test response")
print(result)
```

## 📚 API Reference

### TokenAnalyticsEvaluator
```python
evaluator = TokenAnalyticsEvaluator(queries_file='data/queries.yaml', llm_api_key='your-key')

# Evaluate single response
result = evaluator.evaluate_agent_response(query_id, agent_response, agent_name)

# Run full evaluation
summary = evaluator.run_evaluation(agent_responses, agent_name)

# Print summary
evaluator.print_summary(summary)
```

### AnalyticsGradingScale
```python
grader = AnalyticsGradingScale()

# Grade single question
score_info = grader.calculate_question_score(evaluation_result)

# Grade full evaluation
grading_report = grader.grade_evaluation(evaluation_results)

# Print report
grader.print_grading_report(grading_report)
```

## 🎯 Best Practices

### For Agent Developers
1. **Provide specific numbers**: Avoid vague responses
2. **Use correct units**: Percentages, dates, token symbols
3. **Handle uncertainty**: Acknowledge when data is unavailable
4. **Test thoroughly**: Use the test scripts before deployment

### For Evaluators
1. **Use consistent data**: Ensure all agents use same time period
2. **Track improvements**: Monitor performance over time
3. **Analyze patterns**: Identify common failure modes
4. **Customize thresholds**: Adjust tolerance based on use case

## 🔄 Continuous Improvement

### Adding New Queries
1. Define query in `data/queries.yaml`
2. Calculate truth values using historical data
3. Test with `test/test_new_queries.py`
4. Update documentation

### Enhancing Grading
1. Modify weights in `grading_scale.py`
2. Add new error types as needed
3. Test with sample data
4. Validate with real results

### Performance Optimization
1. Cache LLM responses for repeated queries
2. Batch API calls for efficiency
3. Use async processing for large datasets
4. Implement result caching

## 📄 License

This project is open source and available under the MIT License.

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📞 Support

For questions or issues:
1. Check the troubleshooting section
2. Review test examples
3. Open an issue on GitHub
4. Contact the development team

---

**Happy Evaluating! 🚀** 