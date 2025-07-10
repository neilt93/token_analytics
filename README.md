# 🚀 Token Analytics Evaluation System

A comprehensive benchmark system for evaluating AI agents on real crypto token analytics using actual market data from CoinGecko API.

## 📁 Directory Structure

```
token_analytics/
├── 📊 Data Files
│   └── data/
│       ├── sol_daily.csv      # Solana OHLCV data (31 days)
│       ├── eth_daily.csv      # Ethereum OHLCV data (31 days)
│       ├── tao_daily.csv      # Bittensor OHLCV data (31 days)
│       └── queries.yaml       # 15 benchmark queries with truth values
├── 🧪 Testing & Evaluation
│   └── test/
│       ├── test_eval.py       # Test the evaluation system
│       ├── example_usage.py   # Example usage
│       ├── run_perplexity_eval.py  # Perplexity AI evaluation
│       ├── real_llm_integration.py # Multi-LLM integration
│       └── llm_evaluation_example.py # LLM evaluation examples
├── 🔧 Scripts & Tools
│   └── scripts/
│       ├── token_analytics_dataset.py  # Generate CSV data from CoinGecko
│       ├── pretty_print_data.py       # Pretty print the data
│       └── calculate_truth.py         # Verify truth values from data
├── 🤖 Core System
│   ├── eval.py                # Main evaluation engine
│   ├── requirements.txt       # Dependencies
│   ├── setup_env.py           # Environment setup
│   ├── test_pplx.py           # Perplexity testing
│   └── run_eval.py            # Evaluation runner
└── 📋 Documentation
    ├── README.md              # This file
    ├── README_EVALUATION.md   # Detailed evaluation guide
    ├── README_LLM_USAGE.md    # LLM integration guide
    └── IMPROVEMENTS_SUMMARY.md # Performance improvements
```

## 🚀 Quick Start

### 1. Setup Environment

```bash
python setup_env.py
```

### 2. Configure API Keys

Copy the example file and add your API keys:

```bash
cp env_example.txt .env
```

Then edit `.env` and add your actual API keys:

```env
PERPLEXITY_API_KEY=your_key_here
OPENAI_API_KEY=your_key_here
ANTHROPIC_API_KEY=your_key_here
LANGFUSE_PUBLIC_KEY=your_langfuse_public_key
LANGFUSE_SECRET_KEY=your_langfuse_secret_key
```

### 3. Test the System

```bash
python test/test_eval.py
```

### 4. Evaluate Your Agent

```bash
python test/example_usage.py
```

### 5. Run Perplexity Evaluation

```bash
python test/run_perplexity_eval.py
```

### 6. Generate New Data

```bash
python scripts/token_analytics_dataset.py
```

### 7. Verify Truth Values

```bash
python scripts/calculate_truth.py
```

### 8. Track Performance with Langfuse

```bash
# Run Langfuse integration
python scripts/langfuse_integration.py

# Or run the example
python test/langfuse_example.py
```

## 🎯 What You Get

- **15 benchmark queries** across 6 categories
- **Real market data** (SOL, ETH, TAO - 30 days from CoinGecko)
- **80%+ accuracy** evaluation system
- **Category breakdown** performance tracking
- **Hallucination detection** and error analysis
- **Multiple AI service integration** (Perplexity, OpenAI, Anthropic)

## 📊 Example Results

```
📊 EVALUATION SUMMARY: Your Agent
✅ Correct Answers: 12/15 (80.0%)
❌ Hallucinations: 1 (6.7%)
📏 Avg Absolute Error: 0.01

📈 Performance by Category:
• Percentage Threshold: 3/3 (100.0%)
• Price Change: 3/3 (100.0%)
• Volume Analysis: 2/2 (100.0%)
• Market Cap: 2/3 (66.7%)
• Performance Ranking: 1/2 (50.0%)
• Technical Indicators: 1/2 (50.0%)
```

## 🔧 Key Features

- **Smart parsing** of AI responses with category-specific extractors
- **Context-aware** number extraction with unit handling
- **Robust ranking** normalization and comparison
- **Real data** validation against actual market data
- **JSON export** for tracking and analysis
- **Multiple AI service support** with easy integration
- **Comprehensive error analysis** and hallucination detection

## 🎉 Perfect For

- **Comparing your agent vs ChatGPT/Perplexity/Claude**
- **Tracking improvements** over time
- **Identifying strengths/weaknesses** by category
- **Proving your agent's superiority** with real data
- **Benchmarking different AI models** on crypto analytics
- **Research and development** of specialized crypto AI agents

## 📊 Evaluation Categories

The system evaluates AI models on 15 specific queries across 6 categories:

1. **Percentage Threshold** (3 queries) - Price change percentages
2. **Price Change** (3 queries) - Absolute price movements
3. **Volume Analysis** (2 queries) - Trading volume comparisons
4. **Market Cap** (3 queries) - Market capitalization analysis
5. **Performance Ranking** (2 queries) - Best/worst performing tokens
6. **Technical Indicators** (2 queries) - Moving averages and support/resistance

## 🔗 Integration Examples

### Perplexity AI

```bash
python test/run_perplexity_eval.py
```

### OpenAI ChatGPT

```bash
python test/real_llm_integration.py
```

### Langfuse Performance Tracking

```bash
# Track evaluations in Langfuse
python scripts/langfuse_integration.py

# Run example with sample data
python test/langfuse_example.py
```

### Custom AI Service

```python
# See test/real_llm_integration.py for examples
```

## 📁 File Organization

### Data Directory (`data/`)

- Raw CSV files with OHLCV data from CoinGecko
- Benchmark queries and truth values in YAML format
- All data files organized in one place

### Test Directory (`test/`)

- Test scripts and evaluation examples
- Pre-configured evaluation results
- Ready-to-run examples for different AI services

### Scripts Directory (`scripts/`)

- Data generation tools from CoinGecko API
- Data verification and validation scripts
- Utility functions for data processing
- Langfuse integration for performance tracking

### Core System

- Main evaluation engine with category-specific extractors
- Environment setup and dependency management
- Comprehensive documentation and guides

## 🛠️ Development

### Adding New AI Services

1. Create a new evaluation script in `test/`
2. Implement the AI service integration
3. Use the evaluation engine from `eval.py`
4. Follow the pattern in existing examples

### Extending Queries

1. Add new queries to `data/queries.yaml`
2. Update truth calculation in `scripts/calculate_truth.py`
3. Test with existing evaluation scripts

### Custom Extractors

1. Add new extractor classes to `eval.py`
2. Implement the `extract()` method
3. Register in the `ExtractorRegistry`

### Langfuse Integration

1. Set up Langfuse credentials in `.env`
2. Run `python scripts/langfuse_integration.py` to track existing evaluations
3. Use `LangfuseTokenAnalyticsTracker` in your custom scripts
4. View traces in Langfuse dashboard for performance monitoring

## 📚 Documentation

- **`README_EVALUATION.md`**: Detailed evaluation methodology
- **`README_LLM_USAGE.md`**: LLM integration guide
- **`IMPROVEMENTS_SUMMARY.md`**: Development roadmap and improvements
- **`LANGFUSE_INTEGRATION.md`**: Complete Langfuse integration guide

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Add tests for new functionality
4. Submit a pull request

## 📄 License

This project is open source. See individual files for specific licensing information.

---

**🎉 You now have a real 30-day OHLCV benchmark for SOL, ETH, TAO — ready to test percentage thresholds, timeframes, and multi-token comparisons so you can score your crypto agent vs. generic LLMs!**