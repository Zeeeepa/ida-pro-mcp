"""Configuration for the projector application."""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Slack configuration
SLACK_USER_TOKEN = os.getenv("SLACK_USER_TOKEN", "")
SLACK_DEFAULT_CHANNEL = os.getenv("SLACK_DEFAULT_CHANNEL", "general")

# GitHub configuration
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_USERNAME = os.getenv("GITHUB_USERNAME", "")
GITHUB_DEFAULT_REPO = os.getenv("GITHUB_DEFAULT_REPO", "")

# Model configuration
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")

# Application configuration
DEFAULT_DOCS_PATH = os.getenv("DEFAULT_DOCS_PATH", "docs")
MAX_THREADS = int(os.getenv("MAX_THREADS", "10"))
DEBUG_MODE = os.getenv("DEBUG_MODE", "false").lower() == "true"

# Try to load from Streamlit secrets if available
try:
    import streamlit as st
    
    if "SLACK_USER_TOKEN" in st.secrets:
        SLACK_USER_TOKEN = st.secrets["SLACK_USER_TOKEN"]
    
    if "SLACK_DEFAULT_CHANNEL" in st.secrets:
        SLACK_DEFAULT_CHANNEL = st.secrets["SLACK_DEFAULT_CHANNEL"]
    
    if "GITHUB_TOKEN" in st.secrets:
        GITHUB_TOKEN = st.secrets["GITHUB_TOKEN"]
    
    if "GITHUB_USERNAME" in st.secrets:
        GITHUB_USERNAME = st.secrets["GITHUB_USERNAME"]
    
    if "GITHUB_DEFAULT_REPO" in st.secrets:
        GITHUB_DEFAULT_REPO = st.secrets["GITHUB_DEFAULT_REPO"]
    
    if "ANTHROPIC_API_KEY" in st.secrets:
        ANTHROPIC_API_KEY = st.secrets["ANTHROPIC_API_KEY"]
    
    if "OPENAI_API_KEY" in st.secrets:
        OPENAI_API_KEY = st.secrets["OPENAI_API_KEY"]
except:
    pass