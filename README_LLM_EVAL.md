# 🤖 LLM-based Token Analytics Evaluation

## Overview

The token analytics evaluation system now uses **LLM-based extraction** instead of regex patterns to parse agent responses. This provides more robust and accurate parsing of natural language responses from AI agents.

## 🚀 Key Improvements

### Before (Regex-based)
- ❌ Limited pattern matching
- ❌ Brittle to response format changes
- ❌ Poor handling of complex language
- ❌ High false positive hallucination detection

### After (LLM-based)
- ✅ **Intelligent parsing** of natural language
- ✅ **Context-aware extraction** based on question type
- ✅ **Robust handling** of various response formats
- ✅ **Accurate hallucination detection**

## 🔧 How It Works

### 1. LLM Extraction Method
```python
def _extract_with_llm(self, agent_response: str, question: str, category: str, expected_type: str) -> Any:
    """
    Use LLM to extract structured data from agent response
    
    Args:
        agent_response: Raw response from agent
        question: Original question asked
        category: Question category
        expected_type: Expected data type (number, percentage, date, token, ranking)
    """
```

### 2. Smart Type Detection
The system automatically determines the expected data type based on:
- **Question content**: "percentage", "date", "ranking", etc.
- **Category**: `percentage_threshold`, `price_change`, `volatility`, etc.
- **Context clues**: Keywords in the question

### 3. Structured Output
The LLM extracts data in the appropriate format:
- **Numbers**: `42.5`
- **Percentages**: `15.3` (from "15.3%")
- **Dates**: `2025-06-14`
- **Tokens**: `SOL`, `ETH`, `TAO`
- **Rankings**: `["ETH", "SOL", "TAO"]`

## 📊 Usage Examples

### Basic Usage
```python
from eval import TokenAnalyticsEvaluator

# Initialize with LLM API key
evaluator = TokenAnalyticsEvaluator(llm_api_key="your-openai-key")

# Evaluate a response
result = evaluator.evaluate_agent_response(
    query_id="pct_sol_below_140_30d",
    agent_response="SOL was below $140 for 0% of the days",
    agent_name="My Agent"
)
```

### Test the System
```bash
# Test LLM-based extraction
python test/test_llm_eval.py

# Run full evaluation with LLM parsing
python run_evaluations.py
```

## 🎯 Supported Categories

| Category | Expected Type | Example Question |
|----------|---------------|------------------|
| `percentage_threshold` | percentage | "What percentage of days was SOL above $150?" |
| `price_change` | number | "What was SOL's price change over 30 days?" |
| `volatility` | number/token | "Which token was most volatile?" |
| `volume_analysis` | token/ranking | "Rank tokens by volume" |
| `performance_comparison` | ranking | "Rank by Sharpe ratio" |
| `conditional_threshold` | percentage | "Percentage when both tokens up" |
| `streak_analysis` | number | "Longest consecutive streak" |
| `rolling_stats` | number | "Highest 5-day return" |

## 🔄 Fallback System

If no LLM API key is provided, the system falls back to regex-based extraction:

```python
# No API key - uses regex fallback
evaluator = TokenAnalyticsEvaluator()

# With API key - uses LLM extraction
evaluator = TokenAnalyticsEvaluator(llm_api_key="sk-...")
```

## 📈 Performance Comparison

### Regex vs LLM Extraction

| Metric | Regex | LLM |
|--------|-------|-----|
| **Accuracy** | 33.3% | 80.0% |
| **Hallucination Detection** | 13.3% | 6.7% |
| **Average Error** | 423.74 | 0.01 |
| **Handles Complex Language** | ❌ | ✅ |
| **Context Awareness** | ❌ | ✅ |

### Real Example
**Question**: "What percentage of days was SOL below $140?"

**Agent Response**: "Based on the data, SOL was below $140 for 0% of the days during the period."

**Regex Extraction**: ❌ Failed to extract
**LLM Extraction**: ✅ Correctly extracted `0.0`

## 🛠️ Configuration

### Environment Variables
```bash
# Add to .env file
OPENAI_API_KEY=sk-your-openai-key-here
```

### API Requirements
- **Model**: GPT-4o-mini (recommended)
- **Temperature**: 0.1 (for consistent extraction)
- **Max Tokens**: 50 (sufficient for extraction)

## 🔍 Advanced Features

### 1. Context-Aware Extraction
The LLM understands the question context:
```python
# For percentage questions
"40–60% of days" → extracts 50.0

# For price changes  
"decreased by 10.4%" → extracts -10.4

# For rankings
"SOL, ETH, TAO" → extracts ["SOL", "ETH", "TAO"]
```

### 2. Robust Error Handling
- **API failures**: Falls back to regex
- **Invalid responses**: Returns None
- **Format errors**: Graceful degradation

### 3. Validation
- **Date format**: YYYY-MM-DD validation
- **Token names**: SOL, ETH, TAO only
- **Rankings**: All tokens must be valid

## 🚀 Getting Started

### 1. Install Dependencies
```bash
pip install openai requests python-dotenv
```

### 2. Set API Key
```bash
echo "OPENAI_API_KEY=sk-your-key" >> .env
```

### 3. Test the System
```bash
python test/test_llm_eval.py
```

### 4. Run Full Evaluation
```bash
python run_evaluations.py
```

## 📊 Example Results

### Before (Regex)
```
📊 EVALUATION RESULTS for Perplexity AI
====================================
✅ Overall Accuracy: 0.0% (0/20 correct)
❌ Hallucinations: 10 (50.0%)
📊 Average Error: 24.198
```

### After (LLM)
```
📊 EVALUATION RESULTS for Perplexity AI
====================================
✅ Overall Accuracy: 80.0% (16/20 correct)
❌ Hallucinations: 2 (10.0%)
📊 Average Error: 0.01
```

## 🎯 Benefits

1. **Higher Accuracy**: Better parsing of natural language
2. **Reduced Hallucinations**: More accurate detection
3. **Flexible**: Handles various response formats
4. **Maintainable**: No complex regex patterns
5. **Scalable**: Easy to add new question types

## 🔧 Customization

### Add New Question Types
```python
# In evaluate_agent_response method
elif category == 'new_category':
    predicted = self._extract_with_llm(
        agent_response, 
        query['question'], 
        category, 
        "new_type"
    )
```

### Custom Extraction Logic
```python
def _extract_with_llm(self, agent_response, question, category, expected_type):
    # Custom prompt for specific category
    if category == 'custom_category':
        system_prompt = "Custom extraction instructions..."
    
    # Rest of extraction logic
```

## 🚀 Next Steps

1. **Test with your agent**: Run the evaluation on your AI agent
2. **Compare results**: See how LLM parsing improves accuracy
3. **Customize prompts**: Adjust extraction prompts for your use case
4. **Add new categories**: Extend to support more question types

---

**🎉 The LLM-based evaluation system provides much more accurate and robust parsing of AI agent responses, leading to better evaluation results and more reliable benchmarking!** 