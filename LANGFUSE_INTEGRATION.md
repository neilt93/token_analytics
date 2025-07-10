# 🚀 Langfuse Integration Guide

## Overview

This guide shows you how to integrate your Token Analytics Evaluation System with Langfuse for comprehensive AI performance tracking and monitoring.

## 📋 Prerequisites

1. **Langfuse Account**: Sign up at [langfuse.com](https://langfuse.com)
2. **Python Environment**: Ensure you have the required packages
3. **API Keys**: Get your Langfuse credentials

## 🔧 Setup

### 1. Install Langfuse

```bash
pip install langfuse
```

### 2. Configure Environment Variables

Add to your `.env` file:

```env
# Langfuse Configuration
LANGFUSE_PUBLIC_KEY=your_public_key_here
LANGFUSE_SECRET_KEY=your_secret_key_here
LANGFUSE_HOST=https://cloud.langfuse.com
```

### 3. Get Your Langfuse Credentials

1. Go to [Langfuse Dashboard](https://cloud.langfuse.com)
2. Create a new project or use existing one
3. Go to Settings → API Keys
4. Copy your Public Key and Secret Key

## 🎯 Features

### What Gets Tracked

1. **Complete Evaluations**
   - Overall accuracy scores
   - Hallucination rates
   - Per-question performance
   - Error analysis

2. **Agent Comparisons**
   - Side-by-side performance
   - Best agent identification
   - Performance trends

3. **Difficulty Analysis**
   - Easy vs hard question performance
   - Category-specific metrics
   - Learning curve analysis

4. **Detailed Traces**
   - Individual question responses
   - AI model outputs
   - Ground truth comparisons
   - Error categorization

## 🚀 Usage

### Basic Integration

```python
from scripts.langfuse_integration import LangfuseTokenAnalyticsTracker

# Initialize tracker
tracker = LangfuseTokenAnalyticsTracker()

# Track an evaluation
trace_id = tracker.create_evaluation_trace(
    agent_name="Your AI Agent",
    evaluation_results=your_results,
    agent_responses=your_responses
)
```

### Run Integration with Existing Data

```bash
python scripts/langfuse_integration.py
```

This will automatically integrate your existing ChatGPT and Perplexity evaluations.

### Custom Integration

```python
# Track agent comparison
comparison_trace = tracker.track_agent_comparison(
    comparison_results=your_comparison_data,
    agent_names=["GPT-4", "Claude", "Perplexity"]
)

# Track difficulty analysis
difficulty_trace = tracker.track_easy_vs_hard_performance(
    evaluation_results=your_results,
    agent_name="Your Agent"
)
```

## 📊 Dashboard Features

### 1. Performance Monitoring

- **Real-time accuracy tracking**
- **Hallucination rate alerts**
- **Performance degradation detection**
- **A/B testing results**

### 2. Agent Comparison

- **Multi-agent performance charts**
- **Best agent identification**
- **Performance trends over time**
- **Cost vs performance analysis**

### 3. Question Analysis

- **Per-question performance**
- **Category-specific metrics**
- **Error pattern analysis**
- **Difficulty progression**

### 4. Custom Dashboards

Create custom dashboards for:
- **Daily performance summaries**
- **Weekly trend analysis**
- **Monthly agent comparisons**
- **Alert configurations**

## 🔍 Trace Structure

### Main Trace
```
Token Analytics Evaluation - [Agent Name]
├── Overall Accuracy Score
├── Hallucination Rate Score
└── Question Spans
    ├── Question: [query_id]
    │   ├── AI Response Generation
    │   ├── Correctness Score
    │   ├── Hallucination Score
    │   └── Precision Score
    └── ...
```

### Comparison Trace
```
Token Analytics Agent Comparison
├── [Agent1]_accuracy
├── [Agent1]_hallucination
├── [Agent2]_accuracy
├── [Agent2]_hallucination
└── best_agent
```

### Difficulty Analysis Trace
```
Difficulty Analysis - [Agent Name]
├── easy_questions_accuracy
├── easy_questions_hallucination
├── hard_questions_accuracy
└── hard_questions_hallucination
```

## 📈 Metrics Tracked

### Accuracy Metrics
- **Overall accuracy percentage**
- **Per-category accuracy**
- **Easy vs hard question accuracy**
- **Trend analysis over time**

### Quality Metrics
- **Hallucination rate**
- **Error type distribution**
- **Precision scores**
- **Response quality**

### Performance Metrics
- **Response time analysis**
- **Cost per evaluation**
- **Success rate trends**
- **Model comparison scores**

## 🚨 Alerts & Monitoring

### Set Up Alerts

1. **Performance Drop Alerts**
   - Alert when accuracy drops below threshold
   - Monitor hallucination rate increases
   - Track error rate spikes

2. **Model Comparison Alerts**
   - Alert when one model significantly outperforms others
   - Monitor cost vs performance ratios
   - Track A/B test results

3. **Custom Alerts**
   - Category-specific performance alerts
   - Difficulty-based alerts
   - Trend-based notifications

### Monitoring Dashboard

Create custom dashboards for:
- **Daily performance summaries**
- **Weekly trend analysis**
- **Monthly agent comparisons**
- **Real-time monitoring**

## 🔄 Continuous Integration

### Automated Tracking

```python
# In your evaluation scripts
from scripts.langfuse_integration import LangfuseTokenAnalyticsTracker

def run_evaluation_with_tracking():
    # Run your evaluation
    results = run_evaluation()
    
    # Track in Langfuse
    tracker = LangfuseTokenAnalyticsTracker()
    trace_id = tracker.create_evaluation_trace(
        agent_name="Your Agent",
        evaluation_results=results,
        agent_responses=responses
    )
    
    return results, trace_id
```

### Scheduled Monitoring

```python
# Daily monitoring script
def daily_monitoring():
    tracker = LangfuseTokenAnalyticsTracker()
    
    # Run evaluations
    for agent in ["GPT-4", "Claude", "Perplexity"]:
        results = evaluate_agent(agent)
        tracker.create_evaluation_trace(agent, results, responses)
    
    # Create comparison
    tracker.track_agent_comparison(comparison_data, agent_names)
```

## 📊 Advanced Analytics

### Custom Metrics

```python
# Track custom metrics
trace.score(
    name="custom_metric",
    value=your_calculation,
    comment="Custom metric description"
)
```

### Performance Trends

```python
# Track performance over time
def track_performance_trend(agent_name, results):
    tracker = LangfuseTokenAnalyticsTracker()
    
    # Add trend analysis
    trend_score = calculate_trend(results)
    tracker.langfuse.score(
        name=f"{agent_name}_trend",
        value=trend_score,
        comment="Performance trend analysis"
    )
```

## 🎯 Best Practices

### 1. Consistent Naming
- Use consistent agent names
- Standardize query IDs
- Maintain category naming

### 2. Regular Monitoring
- Set up daily/weekly evaluations
- Monitor performance trends
- Track model improvements

### 3. Alert Configuration
- Set appropriate thresholds
- Configure escalation rules
- Monitor cost vs performance

### 4. Data Retention
- Configure appropriate retention periods
- Archive old traces
- Maintain data quality

## 🔧 Troubleshooting

### Common Issues

1. **Authentication Errors**
   - Verify API keys in .env
   - Check Langfuse project settings
   - Ensure correct host URL

2. **Missing Data**
   - Verify evaluation files exist
   - Check file permissions
   - Validate JSON format

3. **Performance Issues**
   - Batch trace creation
   - Use async operations
   - Monitor API rate limits

### Debug Mode

```python
# Enable debug logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Test connection
tracker = LangfuseTokenAnalyticsTracker()
print(f"Langfuse connection: {tracker.langfuse is not None}")
```

## 📚 Next Steps

1. **Set up your Langfuse account**
2. **Configure environment variables**
3. **Run the integration script**
4. **Explore the dashboard**
5. **Set up alerts and monitoring**
6. **Create custom dashboards**
7. **Implement continuous tracking**

## 🎉 Benefits

- **Real-time performance monitoring**
- **Comprehensive AI evaluation tracking**
- **Multi-agent comparison capabilities**
- **Advanced analytics and insights**
- **Automated alerting system**
- **Historical performance analysis**
- **A/B testing support**
- **Cost optimization insights**

---

**Ready to track your AI performance? Start with the basic integration and build up to advanced monitoring!** 