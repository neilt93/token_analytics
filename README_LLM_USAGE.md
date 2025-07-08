# 🤖 How to Use This System for LLM Evaluation

This guide shows you how to evaluate real LLMs (ChatGPT, Perplexity, Claude, etc.) using our token analytics benchmark.

## 🚀 Quick Start

### Step 1: Install Dependencies
```bash
pip install openai anthropic requests pandas numpy
```

### Step 2: Get Your API Keys
- **OpenAI (ChatGPT)**: Get from [OpenAI Platform](https://platform.openai.com/api-keys)
- **Perplexity**: Get from [Perplexity API](https://www.perplexity.ai/settings/api)
- **Anthropic (Claude)**: Get from [Anthropic Console](https://console.anthropic.com/)

### Step 3: Configure and Run
Edit `test/real_llm_integration.py` and add your API keys:

```python
llm_configs = [
    {"name": "ChatGPT", "api_key": "sk-your-openai-key-here"},
    {"name": "Perplexity", "api_key": "pplx-your-perplexity-key-here"},
    {"name": "Claude", "api_key": "sk-ant-your-anthropic-key-here"},
]
```

Then run:
```bash
cd token_analytics
python test/real_llm_integration.py
```

## 📊 What You'll Get

### 1. Individual LLM Results
- **Accuracy percentage** for each LLM
- **Correct vs incorrect answers** breakdown
- **Hallucination detection** (when LLMs make up data)
- **Average error** for numerical questions

### 2. Comparison Reports
- **Side-by-side comparison** of all LLMs
- **Winner determination** based on accuracy
- **Detailed breakdown** by question category

### 3. Saved Files
- `test/chatgpt_evaluation_results.json` - ChatGPT results
- `test/perplexity_evaluation_results.json` - Perplexity results
- `test/llm_comparison_report.json` - Overall comparison

## 🔧 Manual Evaluation (No API Keys Needed)

If you don't have API keys, you can manually test LLMs:

### Step 1: Get LLM Responses
Ask each of these 15 questions to your LLM:

1. **Percentage Questions:**
   - "What percentage of days was TAO above $400 in the last 30 days?"
   - "What percentage of days was SOL above $150 in the last 30 days?"
   - "What percentage of days was ETH above $2500 in the last 30 days?"

2. **Price Change Questions:**
   - "What was SOL's price change percentage over the last 30 days?"
   - "What was ETH's price change percentage over the last 30 days?"
   - "What was TAO's price change percentage over the last 30 days?"

3. **Volume Analysis:**
   - "Which token had the highest average daily volume?"
   - "Rank the tokens by total volume (highest to lowest)."

4. **Date Questions:**
   - "On what date did ETH have its highest closing price?"
   - "On what date did SOL have its lowest closing price?"

5. **Ranking Questions:**
   - "Rank the tokens by average closing price (highest to lowest)."
   - "Which token was the most volatile?"
   - "What was SOL's price range over the period?"
   - "Which token was the best performer over the 30 days?"
   - "Which token was the worst performer over the 30 days?"

### Step 2: Create Response Dictionary
```python
responses = {
    'pct_tao_above_400': "LLM's answer here",
    'pct_sol_above_150': "LLM's answer here",
    'pct_eth_above_2500': "LLM's answer here",
    # ... add all 15 responses
}
```

### Step 3: Run Evaluation
```python
from eval import TokenAnalyticsEvaluator

evaluator = TokenAnalyticsEvaluator()
summary = evaluator.run_evaluation(responses, "Your LLM Name")
evaluator.print_summary(summary)
```

## 📈 Understanding the Results

### Accuracy Metrics
- **Overall Accuracy**: Percentage of correct answers
- **Category Accuracy**: Performance by question type
- **Hallucination Rate**: How often the LLM makes up data

### Error Analysis
- **Numerical Errors**: How far off are percentage/price predictions
- **Ranking Errors**: Wrong order in ranking questions
- **Date Errors**: Incorrect date identification

### Sample Output
```
📊 EVALUATION RESULTS for ChatGPT
====================================
✅ Overall Accuracy: 86.7% (13/15 correct)
❌ Hallucinations: 1 (6.7%)
📊 Average Error: 0.23%

📋 DETAILED BREAKDOWN:
✅ Percentage Questions: 100% (3/3)
✅ Price Changes: 100% (3/3)
✅ Volume Analysis: 100% (2/2)
✅ Date Questions: 50% (1/2)
✅ Rankings: 80% (4/5)
```

## 🎯 Use Cases

### 1. **LLM Comparison**
Compare different models side-by-side:
```python
llm_integration.compare_multiple_llms([
    {"name": "GPT-4", "api_key": "..."},
    {"name": "Claude-3", "api_key": "..."},
    {"name": "Perplexity", "api_key": "..."}
])
```

### 2. **Model Fine-tuning Validation**
Test your fine-tuned model against benchmarks:
```python
summary = evaluator.run_evaluation(your_model_responses, "Fine-tuned Model")
```

### 3. **Prompt Engineering**
Test different prompts with the same model:
```python
# Test different system prompts
prompt_variations = [
    "You are a financial analyst...",
    "You are a data scientist...",
    "You are a crypto expert..."
]
```

### 4. **Continuous Monitoring**
Run regular evaluations to track model performance:
```python
# Run weekly evaluations
import schedule
schedule.every().monday.do(run_evaluation)
```

## 🔍 Advanced Usage

### Custom Evaluation Metrics
```python
# Add custom scoring
def custom_scorer(predicted, actual, category):
    if category == "percentage":
        return 1.0 if abs(predicted - actual) < 1.0 else 0.0
    return predicted == actual

evaluator.custom_scorer = custom_scorer
```

### Batch Processing
```python
# Evaluate multiple models in parallel
import concurrent.futures

def evaluate_model(model_name, api_key):
    return llm_integration.run_full_evaluation(model_name, api_key)

with concurrent.futures.ThreadPoolExecutor(max_workers=3) as executor:
    futures = [
        executor.submit(evaluate_model, "ChatGPT", openai_key),
        executor.submit(evaluate_model, "Claude", anthropic_key),
        executor.submit(evaluate_model, "Perplexity", perplexity_key)
    ]
    results = [future.result() for future in futures]
```

## 🚨 Troubleshooting

### Common Issues
1. **API Rate Limits**: Add delays between requests
2. **Authentication Errors**: Check API key format
3. **Parsing Errors**: LLM responses might be in unexpected format

### Debug Mode
```python
# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test individual parsing
evaluator.debug_mode = True
result = evaluator.evaluate_agent_response("pct_tao_above_400", "TAO was above $400 for 9.7% of days")
```

## 📚 Next Steps

1. **Extend the Dataset**: Add more tokens or time periods
2. **Add More Queries**: Create new question categories
3. **Custom Metrics**: Implement domain-specific scoring
4. **Real-time Evaluation**: Set up automated monitoring
5. **Multi-language Support**: Test LLMs in different languages

---

**Need Help?** Check the example files in the `test/` directory or run the demo scripts to see the system in action! 