# AI Image Caption Generator 🖼️

Upload any image and get AI-powered captions,
hashtags, mood detection and object analysis
using Google Gemini Vision.

## Live Demo
[Click here](YOUR_STREAMLIT_URL)

## Features
- 6 caption styles: Descriptive, Social Media,
  Professional, Creative, Technical, Story
- Mood and emotion detection
- Dominant color analysis
- Object detection list
- Hashtag generation
- 8 output languages including Hindi and Tamil
- Batch analysis — multiple images at once
- Caption history with export

## How It Works
Sends image to Google Gemini 1.5 Flash
via multimodal API. Returns structured
JSON with caption, tags, mood and objects.

## Tools Used
- Python, Streamlit, Google Gemini Vision API
- Pillow, Base64 encoding

## Setup
1. Get free API key at aistudio.google.com
2. Add to Streamlit secrets as GEMINI_API_KEY

## How to Run Locally
pip install streamlit google-generativeai Pillow
streamlit run app.py
