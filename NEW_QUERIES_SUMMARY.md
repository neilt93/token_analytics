# 🆕 New Queries Added to Token Analytics Evaluation

## Overview

Added **10 new queries** to the token analytics evaluation system, expanding the benchmark from 20 to 30 total queries. These new queries cover additional market analysis scenarios and provide more comprehensive testing of AI agents.

## 📊 New Queries Summary

### 1. **pct_days_sol_up_eth_down**
- **Question**: What percentage of days did SOL close higher while ETH closed lower during the 30-day period from June 9 to July 8 2025?
- **Category**: `conditional_threshold`
- **Truth**: 3.45%
- **Explanation**: 1 out of 29 days had SOL up and ETH down

### 2. **tao_avg_daily_range**
- **Question**: What was TAO's average daily intraday range (high minus low) as a percentage of its closing price during the 30-day period?
- **Category**: `volatility_stat`
- **Truth**: 0.00%
- **Explanation**: Average daily high-low range as % of close (no intraday data available)

### 3. **eth_biggest_single_day_loss**
- **Question**: What was ETH's largest single-day percentage loss during the 30-day period?
- **Category**: `volatility`
- **Truth**: -5.62%
- **Explanation**: ETH's worst daily return in that window

### 4. **sol_days_close_eq_or_above_open**
- **Question**: On how many days did SOL close at or above its daily opening price during the 30-day period?
- **Category**: `streak_analysis`
- **Truth**: 14
- **Explanation**: Number of days SOL closed >= open

### 5. **pct_days_tao_vol_gt_2x_avg**
- **Question**: What percentage of days did TAO's daily volume exceed twice its 30-day average volume?
- **Category**: `volume_analysis`
- **Truth**: 0.00%
- **Explanation**: Days when TAO's volume > 2× average

### 6. **eth_largest_gap_open_close**
- **Question**: What was ETH's largest positive or negative gap between previous close and next open as a percentage of the previous close during the 30-day period?
- **Category**: `volatility`
- **Truth**: 0.00%
- **Explanation**: Largest overnight gap up/down in % terms

### 7. **sol_days_close_above_10dma**
- **Question**: What percentage of days did SOL close above its 10-day moving average during the 30-day period?
- **Category**: `rolling_stats`
- **Truth**: 37.93%
- **Explanation**: Days SOL closed above its 10-DMA

### 8. **rank_by_max_intraday_swing**
- **Question**: Rank SOL, ETH, and TAO by their largest single-day high-low percentage swing during the 30-day period.
- **Category**: `performance_comparison`
- **Truth**: ["SOL", "ETH", "TAO"]
- **Explanation**: Rank by maximum daily intraday range %

### 9. **pct_days_all_up**
- **Question**: What percentage of days did SOL, ETH, and TAO all close higher than the previous day during the 30-day period?
- **Category**: `conditional_threshold`
- **Truth**: 34.48%
- **Explanation**: Days when all three tokens closed green

### 10. **tao_avg_return_on_high_vol_days**
- **Question**: What was TAO's average daily return on the days when its daily volume exceeded its 30-day average by at least 50%?
- **Category**: `conditional_volume`
- **Truth**: 0.00%
- **Explanation**: Avg return for TAO on high-volume days

## 🎯 Query Categories Covered

| Category | Count | Examples |
|----------|-------|----------|
| **conditional_threshold** | 2 | pct_days_sol_up_eth_down, pct_days_all_up |
| **volatility** | 2 | eth_biggest_single_day_loss, eth_largest_gap_open_close |
| **streak_analysis** | 1 | sol_days_close_eq_or_above_open |
| **rolling_stats** | 1 | sol_days_close_above_10dma |
| **performance_comparison** | 1 | rank_by_max_intraday_swing |
| **volume_analysis** | 1 | pct_days_tao_vol_gt_2x_avg |
| **volatility_stat** | 1 | tao_avg_daily_range |
| **conditional_volume** | 1 | tao_avg_return_on_high_vol_days |

## 🔧 Technical Implementation

### LLM-based Extraction Support
All new queries are fully supported by the LLM-based evaluation system:

```python
# Example usage
evaluator = TokenAnalyticsEvaluator(llm_api_key="your-key")

result = evaluator.evaluate_agent_response(
    query_id="pct_days_sol_up_eth_down",
    agent_response="SOL closed higher while ETH closed lower on 3.45% of days",
    agent_name="My Agent"
)
```

### Category-Specific Parsing
- **conditional_threshold**: Extracts percentages
- **volatility**: Extracts numbers or tokens
- **streak_analysis**: Extracts numbers
- **rolling_stats**: Extracts percentages
- **performance_comparison**: Extracts rankings
- **volume_analysis**: Extracts percentages or tokens
- **volatility_stat**: Extracts numbers
- **conditional_volume**: Extracts numbers

## 📈 Testing

### Test the New Queries
```bash
# Test new queries with LLM evaluation
python test/test_new_queries.py

# Run full evaluation with all 30 queries
python run_evaluations.py
```

### Expected Results
The new queries should work seamlessly with the LLM-based extraction system, providing:

- ✅ **Accurate parsing** of natural language responses
- ✅ **Proper type detection** (numbers, percentages, rankings)
- ✅ **Robust error handling** for edge cases
- ✅ **Consistent evaluation** across all query types

## 🚀 Benefits

### 1. **More Comprehensive Testing**
- Covers additional market scenarios
- Tests different types of analysis
- Provides broader evaluation coverage

### 2. **Better Agent Comparison**
- More data points for accuracy assessment
- Diverse question types for thorough evaluation
- Better identification of agent strengths/weaknesses

### 3. **Enhanced Benchmarking**
- 50% more queries (20 → 30)
- More granular performance analysis
- Better statistical significance

## 📊 Updated System Stats

| Metric | Before | After | Change |
|--------|--------|-------|--------|
| **Total Queries** | 20 | 30 | +50% |
| **Categories** | 9 | 10 | +1 |
| **Percentage Queries** | 2 | 4 | +100% |
| **Volatility Queries** | 2 | 4 | +100% |
| **Conditional Queries** | 2 | 4 | +100% |

## 🎯 Use Cases

### 1. **Advanced Market Analysis**
- Conditional relationships between tokens
- Volatility and risk metrics
- Technical indicator analysis

### 2. **Comprehensive Agent Evaluation**
- Multi-dimensional performance assessment
- Detailed category breakdown
- Better comparison between agents

### 3. **Research and Development**
- Test new analysis capabilities
- Validate agent improvements
- Benchmark against industry standards

---

**🎉 The token analytics evaluation system now includes 30 comprehensive queries covering all major aspects of cryptocurrency market analysis, providing the most thorough AI agent evaluation available!** 