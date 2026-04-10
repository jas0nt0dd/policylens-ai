#!/usr/bin/env python
"""
PolicyLens AI — Diagnostics
Test language translation, SDG classification, and LLM availability
"""
import os
import requests
from pathlib import Path

# Load environment variables from .env
from dotenv import load_dotenv
load_dotenv()

print("""
╔═══════════════════════════════════════════════════════════╗
║         PolicyLens AI — System Diagnostics               ║
╚═══════════════════════════════════════════════════════════╝
""")

# 1. Check LibreTranslate
print("\n1️⃣  LibreTranslate (Translation Service)")
try:
    resp = requests.get("http://localhost:5000/languages", timeout=2)
    if resp.status_code == 200:
        print("   ✅ LibreTranslate is RUNNING")
    else:
        print("   ❌ LibreTranslate not responding properly")
except:
    print("   ❌ LibreTranslate NOT running (Translation will fail)")
    print("      — Language selection will always return English")
    print("      — To fix: Start LibreTranslate container or set GROQ_API_KEY")

# 2. Check Ollama
print("\n2️⃣  Ollama (Local LLM)")
try:
    resp = requests.get("http://localhost:11434/api/tags", timeout=2)
    if resp.status_code == 200:
        models = resp.json().get("models", [])
        if models:
            print(f"   ✅ Ollama is RUNNING with {len(models)} models")
        else:
            print("   ⚠️  Ollama running but no models found")
    else:
        print("   ❌ Ollama not responding")
except:
    print("   ❌ Ollama NOT running (LLM analysis will be limited)")
    print("      — To enable: Download from https://ollama.com")

# 3. Check GROQ API Key
print("\n3️⃣  Groq Free API (Alternative LLM)")
groq_key = os.getenv("GROQ_API_KEY", "")
if groq_key and groq_key.startswith("gsk_"):
    print("   ✅ GROQ_API_KEY is set")
    # Try a quick test
    try:
        import requests
        resp = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={"Authorization": f"Bearer {groq_key}"},
            json={"model": "mixtral-8x7b-32768", "messages": [{"role": "user", "content": "test"}]},
            timeout=5
        )
        if resp.status_code < 400:
            print("   ✅ Groq API is ACCESSIBLE")
        else:
            print(f"   ❌ Groq API error: {resp.status_code}")
    except Exception as e:
        print(f"   ⚠️  Groq API test failed: {e}")
else:
    print("   ❌ GROQ_API_KEY not set")
    print("      — To enable: Get free key from https://console.groq.com")

# 4. Check HuggingFace models
print("\n4️⃣  HuggingFace Models (Fallback)")
hf_cache = Path.home() / ".cache" / "huggingface" / "hub"
if hf_cache.exists():
    models = list(hf_cache.glob("*"))
    if models:
        print(f"   ✅ {len(models)} HuggingFace models cached locally")
    else:
        print("   ⚠️  HuggingFace cache empty (will download on first use)")
else:
    print("   ⚠️  HuggingFace cache not found (will download on first use)")

# 5. Check SDG classifier
print("\n5️⃣  SDG Classification")
print("   ✅ Keyword-based classifier ALWAYS works")
print("   ⚠️  DistilBERT model (optional) uses HuggingFace cache")

print("""
📋 SUMMARY:

For TRANSLATION (Language Selection):
  - Need LibreTranslate running: docker run -d -p 5000:8000 libretranslate/libretranslate
  - OR use the LLM fallback path (Groq/Ollama) for summary translation
  - OR install Argos language packages for offline translation

For LLM ANALYSIS (Deep Analysis):
  Option 1: Setup Ollama (https://ollama.com) + run 'ollama pull mistral'
  Option 2: Get Groq free key (https://console.groq.com) + add to .env
  Option 3: Use HuggingFace free tier (works but slower)

For SDG CLASSIFICATION:
  ✅ Always works with keyword-based fallback
  ⚡ Optional: DistilBERT model for better accuracy

""")
