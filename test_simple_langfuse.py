#!/usr/bin/env python3
"""
Simple Langfuse Test (using start_as_current_span)
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

try:
    from langfuse import Langfuse
    print("✅ Langfuse imported successfully")
    
    # Initialize Langfuse
    langfuse = Langfuse(
        public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
        secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
        host=os.getenv("LANGFUSE_HOST", "https://us.cloud.langfuse.com")
    )
    print("✅ Langfuse client created")
    
    # Test connection by creating a simple span (trace) with context
    with langfuse.start_as_current_span(name="Test Trace"):
        langfuse.score_current_trace(
            name="test_score",
            value=0.85,
            comment="Test score from token analytics"
        )
    print("✅ Test trace created and sent to Langfuse!")
    print("📊 Check your Langfuse dashboard to see the test trace")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
except Exception as e:
    print(f"❌ Error: {e}") 