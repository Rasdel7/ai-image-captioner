import streamlit as st
import google.generativeai as genai
from PIL import Image
import io
import base64
import json
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="AI Image Captioner",
    page_icon="🖼️",
    layout="wide"
)

st.title("🖼️ AI Image Caption Generator")
st.markdown("Upload any image and get intelligent "
            "AI-powered descriptions, tags and analysis.")
st.markdown("---")

# API Key
try:
    api_key = st.secrets["GEMINI_API_KEY"]
except:
    api_key = st.sidebar.text_input(
        "Gemini API Key:",
        type="password",
        placeholder="Get free key at aistudio.google.com"
    )

if api_key:
    genai.configure(api_key=api_key)

# Sidebar
st.sidebar.header("⚙️ Settings")

caption_style = st.sidebar.selectbox(
    "Caption Style:",
    [
        "Descriptive — detailed scene description",
        "Social Media — Instagram-ready caption",
        "Professional — formal alt text",
        "Creative — poetic and expressive",
        "Technical — object and attribute analysis",
        "Story — tell a story from the image"
    ]
)

caption_length = st.sidebar.radio(
    "Caption Length:",
    ["Short (1-2 sentences)",
     "Medium (3-4 sentences)",
     "Long (detailed paragraph)"]
)

include_tags   = st.sidebar.checkbox(
    "Generate hashtags", value=True)
include_mood   = st.sidebar.checkbox(
    "Detect mood/emotion", value=True)
include_colors = st.sidebar.checkbox(
    "Analyze dominant colors", value=True)
include_objects = st.sidebar.checkbox(
    "List detected objects", value=True)

language = st.sidebar.selectbox(
    "Caption Language:",
    ["English", "Hindi", "Telugu",
     "Tamil", "Bengali", "French",
     "Spanish", "German"]
)

st.sidebar.markdown("---")
st.sidebar.markdown("### 💡 Best Images")
st.sidebar.markdown("""
- Nature and landscapes
- Food and cooking
- People and portraits
- Architecture
- Products
- Events and celebrations
""")

# History
if 'caption_history' not in st.session_state:
    st.session_state.caption_history = []

# Prompt builder
def build_prompt(style, length, language,
                 tags, mood, colors, objects):
    style_map = {
        "Descriptive — detailed scene description":
            "Write a detailed descriptive caption "
            "explaining what is happening in this image.",
        "Social Media — Instagram-ready caption":
            "Write an engaging Instagram-style caption "
            "with emojis that would get lots of likes.",
        "Professional — formal alt text":
            "Write a professional, neutral alt text "
            "description suitable for accessibility.",
        "Creative — poetic and expressive":
            "Write a creative, poetic caption that "
            "captures the emotion and beauty of the image.",
        "Technical — object and attribute analysis":
            "Provide a technical analysis describing "
            "objects, attributes, spatial relationships.",
        "Story — tell a story from the image":
            "Tell a short creative story inspired "
            "by what you see in this image."
    }

    length_map = {
        "Short (1-2 sentences)":    "Keep it to 1-2 sentences.",
        "Medium (3-4 sentences)":   "Write 3-4 sentences.",
        "Long (detailed paragraph)":"Write a detailed paragraph."
    }

    prompt = f"{style_map[style]} {length_map[length]}"

    extras = []
    if tags:
        extras.append(
            "Also provide 10 relevant hashtags.")
    if mood:
        extras.append(
            "Detect the overall mood or emotion.")
    if colors:
        extras.append(
            "List the 3 dominant colors.")
    if objects:
        extras.append(
            "List the main objects detected.")

    if extras:
        prompt += "\n\nAlso provide:\n" + \
                  "\n".join(f"- {e}"
                            for e in extras)

    prompt += f"\n\nRespond in {language}."
    prompt += (
        "\n\nFormat your response as JSON with keys: "
        "'caption', 'hashtags' (list), "
        "'mood', 'colors' (list), 'objects' (list). "
        "Only return valid JSON, no markdown."
    )

    return prompt

def analyze_image(image, prompt, api_key):
    try:
        model = genai.GenerativeModel(
            'gemini-1.5-flash')

        # Convert to bytes
        buf = io.BytesIO()
        image.save(buf, format='JPEG',
                   quality=85)
        buf.seek(0)

        response = model.generate_content([
            prompt,
            {
                "mime_type": "image/jpeg",
                "data": base64.b64encode(
                    buf.read()).decode()
            }
        ])
        return response.text
    except Exception as e:
        return json.dumps({
            "caption": f"Error: {str(e)}",
            "hashtags": [],
            "mood": "Unknown",
            "colors": [],
            "objects": []
        })

def parse_response(text):
    try:
        # Clean markdown if present
        clean = text.strip()
        if clean.startswith('```'):
            clean = '\n'.join(
                clean.split('\n')[1:-1])
        return json.loads(clean)
    except:
        return {
            "caption":  text,
            "hashtags": [],
            "mood":     "Unknown",
            "colors":   [],
            "objects":  []
        }

# Tabs
tab1, tab2, tab3 = st.tabs([
    "🖼️ Caption Generator",
    "📊 Batch Analysis",
    "📚 History"
])

# Tab 1 — Single Image
with tab1:
    st.markdown("### Upload an Image")

    uploaded = st.file_uploader(
        "Choose an image:",
        type=['jpg', 'jpeg', 'png',
              'webp', 'bmp', 'gif']
    )

    if uploaded:
        image = Image.open(uploaded)
        if image.mode != 'RGB':
            image = image.convert('RGB')

        col1, col2 = st.columns([1, 1])

        with col1:
            st.markdown("#### 📷 Your Image")
            st.image(image,
                     use_column_width=True)
            st.caption(
                f"Size: {image.size[0]}×"
                f"{image.size[1]} | "
                f"Mode: {image.mode}")

        with col2:
            st.markdown("#### 🤖 AI Analysis")

            if not api_key:
                st.warning(
                    "Enter your Gemini API key "
                    "in the sidebar to analyze!")
            else:
                if st.button(
                    "🚀 Analyze Image",
                    type="primary",
                    use_container_width=True
                ):
                    prompt = build_prompt(
                        caption_style,
                        caption_length,
                        language,
                        include_tags,
                        include_mood,
                        include_colors,
                        include_objects
                    )

                    with st.spinner(
                        "🤖 Gemini is analyzing "
                        "your image..."
                    ):
                        raw = analyze_image(
                            image, prompt,
                            api_key)
                        result = parse_response(
                            raw)

                    # Caption
                    st.markdown(
                        "#### 📝 Caption")
                    st.success(
                        result.get(
                            'caption', ''))

                    # Copy button area
                    st.code(
                        result.get(
                            'caption', ''),
                        language=None
                    )

                    # Mood
                    if include_mood and \
                            result.get('mood'):
                        st.markdown(
                            "#### 😊 Mood")
                        mood_colors = {
                            'happy':   '🟢',
                            'sad':     '🔵',
                            'exciting':'🟡',
                            'calm':    '🟣',
                            'tense':   '🔴',
                            'peaceful':'🟢',
                            'energetic':'🟡'
                        }
                        mood_val = result[
                            'mood'].lower()
                        emoji = next(
                            (v for k, v in
                             mood_colors.items()
                             if k in mood_val),
                            '⚪'
                        )
                        st.markdown(
                            f"{emoji} **"
                            f"{result['mood']}**")

                    # Colors
                    if include_colors and \
                            result.get('colors'):
                        st.markdown(
                            "#### 🎨 Dominant Colors")
                        cols = st.columns(
                            len(result['colors']))
                        for col, color in zip(
                            cols,
                            result['colors']
                        ):
                            col.markdown(
                                f"🎨 {color}")

                    # Objects
                    if include_objects and \
                            result.get('objects'):
                        st.markdown(
                            "#### 🔍 Detected Objects")
                        objs = result['objects']
                        obj_text = " • ".join(
                            objs[:10])
                        st.info(obj_text)

                    # Hashtags
                    if include_tags and \
                            result.get('hashtags'):
                        st.markdown(
                            "#### # Hashtags")
                        tags = result['hashtags']
                        tags_str = " ".join([
                            t if t.startswith('#')
                            else f"#{t}"
                            for t in tags
                        ])
                        st.markdown(
                            f"`{tags_str}`")

                    # Save to history
                    st.session_state\
                        .caption_history.append({
                        'timestamp': str(
                            datetime.now()),
                        'style':     caption_style,
                        'caption':   result.get(
                            'caption', ''),
                        'mood':      result.get(
                            'mood', ''),
                        'hashtags':  result.get(
                            'hashtags', []),
                        'objects':   result.get(
                            'objects', [])
                    })

                    st.success(
                        "✅ Saved to history!")

# Tab 2 — Batch Analysis
with tab2:
    st.markdown("### 📊 Batch Image Analysis")
    st.markdown(
        "Upload multiple images and get "
        "captions for all at once.")

    batch_files = st.file_uploader(
        "Upload multiple images:",
        type=['jpg', 'jpeg', 'png', 'webp'],
        accept_multiple_files=True
    )

    batch_style = st.selectbox(
        "Caption style for batch:",
        ["Descriptive — detailed scene description",
         "Social Media — Instagram-ready caption",
         "Professional — formal alt text"],
        key="batch_style"
    )

    if batch_files and api_key:
        if st.button("🚀 Analyze All Images",
                     type="primary"):
            results = []
            progress = st.progress(0)

            for i, f in enumerate(batch_files):
                with st.spinner(
                    f"Analyzing image "
                    f"{i+1}/{len(batch_files)}..."
                ):
                    img = Image.open(f)
                    if img.mode != 'RGB':
                        img = img.convert('RGB')

                    prompt = build_prompt(
                        batch_style,
                        "Short (1-2 sentences)",
                        "English",
                        False, False,
                        False, True
                    )
                    raw    = analyze_image(
                        img, prompt, api_key)
                    result = parse_response(raw)

                    col_img, col_cap = \
                        st.columns([1, 2])
                    with col_img:
                        st.image(img,
                                 width=200)
                    with col_cap:
                        st.markdown(
                            f"**{f.name}**")
                        st.write(
                            result.get(
                                'caption', ''))
                        if result.get('objects'):
                            st.caption(
                                "Objects: " +
                                ", ".join(
                                    result[
                                        'objects'
                                    ][:5])
                            )

                    results.append({
                        'File':    f.name,
                        'Caption': result.get(
                            'caption', ''),
                        'Objects': ', '.join(
                            result.get(
                                'objects', [])[:5])
                    })
                    progress.progress(
                        (i + 1) /
                        len(batch_files))

            if results:
                import pandas as pd
                results_df = pd.DataFrame(
                    results)
                st.download_button(
                    "⬇️ Download All Captions",
                    results_df.to_csv(
                        index=False),
                    "batch_captions.csv",
                    "text/csv"
                )
    elif batch_files and not api_key:
        st.warning(
            "Enter Gemini API key to analyze!")

# Tab 3 — History
with tab3:
    st.markdown("### 📚 Caption History")

    if not st.session_state.caption_history:
        st.info("No captions generated yet!")
    else:
        if st.button("🗑️ Clear History"):
            st.session_state\
                .caption_history = []
            st.rerun()

        for entry in reversed(
            st.session_state.caption_history
        ):
            with st.expander(
                f"📝 {entry['timestamp'][:19]}"
                f" — {entry['style'][:30]}"
            ):
                st.markdown(
                    f"**Caption:** "
                    f"{entry['caption']}")
                if entry.get('mood'):
                    st.markdown(
                        f"**Mood:** "
                        f"{entry['mood']}")
                if entry.get('hashtags'):
                    st.markdown(
                        "**Tags:** " +
                        " ".join([
                            f"#{t}" for t in
                            entry['hashtags']
                        ]))
                if entry.get('objects'):
                    st.markdown(
                        "**Objects:** " +
                        ", ".join(
                            entry['objects']))

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "AI Image Caption Generator | "
    "Powered by Google Gemini Vision"
)