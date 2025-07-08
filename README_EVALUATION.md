# 🚀 Token Analytics Evaluation System

A comprehensive benchmark system for evaluating AI agents on real crypto token analytics questions using actual market data from CoinGecko API.

## 📋 Overview

This system provides:
- **15 benchmark queries** across 6 categories
- **Real market data** (SOL, ETH, TAO - 30 days)
- **Automated evaluation** with accuracy metrics
- **Hallucination detection** and error analysis
- **Versioned truth values** calculated from actual data

## 🎯 Benchmark Queries

### Percentage Threshold (3 queries)
- What % of days was TAO above $400? → **9.68%**
- What % of days was SOL above $150? → **45.16%**
- What % of days was ETH above $2500? → **64.52%**

### Price Change (3 queries)
- SOL's 30-day price change → **-1.16%**
- ETH's 30-day price change → **+2.31%**
- TAO's 30-day price change → **-16.59%**

### Volume Analysis (2 queries)
- Highest average daily volume → **ETH**
- Volume ranking → **ETH, SOL, TAO**

### Price Analysis (3 queries)
- ETH highest close date → **2025-06-11**
- SOL lowest close date → **2025-06-23**
- Average close ranking → **ETH, TAO, SOL**

### Volatility (2 queries)
- Most volatile token → **TAO**
- SOL price range → **$33.15**

### Performance Comparison (2 queries)
- Best 30-day performer → **ETH**
- Worst 30-day performer → **TAO**

## 📊 Evaluation Metrics

The system tracks:
- **Accuracy percentage** - % of correct answers
- **Average absolute error** - For numeric responses
- **Hallucination count** - Completely wrong responses
- **Category breakdown** - Performance by query type

## 🛠️ Usage

### 1. Test the System
```bash
python test_eval.py
```

### 2. Evaluate Your Agent
```python
from eval import TokenAnalyticsEvaluator

# Initialize evaluator
evaluator = TokenAnalyticsEvaluator()

# Your agent responses
agent_responses = {
    'pct_tao_above_400': "TAO was above $400 for 9.7% of days.",
    'sol_price_change_30d': "SOL decreased by 1.2%.",
    # ... add all 15 responses
}

# Run evaluation
summary = evaluator.run_evaluation(agent_responses, "Your Agent Name")

# Print results
evaluator.print_summary(summary)

# Save results
evaluator.save_results(summary)
```

### 3. Compare Multiple Agents
```python
# Test ChatGPT
chatgpt_responses = {...}
chatgpt_summary = evaluator.run_evaluation(chatgpt_responses, "ChatGPT")

# Test Perplexity
perplexity_responses = {...}
perplexity_summary = evaluator.run_evaluation(perplexity_responses, "Perplexity")

# Test Your Agent
your_agent_responses = {...}
your_summary = evaluator.run_evaluation(your_agent_responses, "Your Agent")
```

## 📁 File Structure

```
testdataset/
├── queries.yaml              # Benchmark queries & truth values
├── eval.py                   # Main evaluation engine
├── calculate_truth.py        # Verify truth values from data
├── test_eval.py             # Test the evaluation system
├── sol_daily.csv            # Solana OHLCV data
├── eth_daily.csv            # Ethereum OHLCV data
├── tao_daily.csv            # Bittensor OHLCV data
└── README_EVALUATION.md     # This file
```

## 🔍 Data Verification

To verify the truth values are correct:
```bash
python calculate_truth.py
```

This will:
- Calculate all metrics from the actual CSV data
- Compare against queries.yaml
- Show any discrepancies

## 📈 Example Results

```
📊 EVALUATION SUMMARY: Test Agent
================================================================================
✅ Correct Answers: 5/15 (33.3%)
❌ Hallucinations: 2 (13.3%)
📏 Avg Absolute Error: 423.74
⏰ Evaluation Time: 2025-07-08T11:30:39.433929

📈 Performance by Category:
   • Percentage Threshold: 0/3 (0.0%)
   • Price Change: 1/3 (33.3%)
   • Volume Analysis: 1/2 (50.0%)
   • Price Analysis: 0/3 (0.0%)
   • Volatility: 1/2 (50.0%)
   • Performance Comparison: 2/2 (100.0%)
```

## 🎯 Why This Matters

### Real Data, Not Synthetic
- Uses actual CoinGecko market data
- Real price movements and volumes
- Authentic market patterns

### Comprehensive Coverage
- Percentage calculations
- Time-based analysis
- Multi-token comparisons
- Volatility metrics
- Performance rankings

### Actionable Insights
- Identify agent strengths/weaknesses
- Compare against ChatGPT/Perplexity
- Track improvements over time
- Detect hallucination patterns

## 🚀 Next Steps

1. **Test your current agent** against these benchmarks
2. **Compare with ChatGPT/Perplexity** responses
3. **Identify improvement areas** based on category performance
4. **Iterate and retest** as you improve your agent
5. **Expand the dataset** with more tokens/timeframes

## 💡 Pro Tips

- **Be precise** - The system expects exact numbers (within 1% tolerance)
- **Include context** - Mention the 30-day period when relevant
- **Use correct dates** - Format as YYYY-MM-DD
- **Rank properly** - Use exact token order for rankings
- **Avoid hallucinations** - Don't make up data not in the CSV files

## 🔧 Customization

To add more queries:
1. Add to `queries.yaml`
2. Update `calculate_truth.py` to calculate the truth value
3. Test with `test_eval.py`

To add more tokens:
1. Generate new CSV data
2. Update queries to include new tokens
3. Recalculate all truth values

---

**🎉 You now have a real 30-day OHLCV benchmark for SOL, ETH, TAO — ready to test % thresholds, timeframes, and multi-token comparisons so you can score your crypto agent vs. generic LLMs!** 