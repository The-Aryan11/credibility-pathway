---
title: Credibility Backend
emoji: 🧠
colorFrom: blue
colorTo: indigo
sdk: docker
app_port: 7860
pinned: false
---

# 🔍 Real-Time Credibility Engine

**Built with Pathway + Groq for Inter-IIT Hackathon**

## What It Doe

A real-time misinformation tracking system that:
1. Ingests live news articles using Pathway's streaming engine
2. Indexes them using vector embeddings
3. Analyzes claims against the knowledge base
4. Provides credibility scores with explanations

## Demo

1. Click "Fetch Latest News" to ingest articles
2. Enter a claim like "The earth is flat"
3. Get instant credibility analysis

## Tech Stack

- **Pathway** - Real-time data processing
- **Groq (Llama 3.1)** - AI fact-checking
- **Sentence Transformers** - Vector embeddings
- **Streamlit** - Frontend UI

## Real-Time Capability

The system updates automatically when new articles are added:
- Add a file to `data/articles/`
- The Pathway pipeline detects it instantly
- Vector store is updated in real-time
- Next query uses the new data

## Setup

```bash
pip install -r requirements.txt
streamlit run app.py