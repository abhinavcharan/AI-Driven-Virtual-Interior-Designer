import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from PIL import Image, ImageOps, ImageFilter, ImageDraw, ImageEnhance, ImageFont
import cv2
import io
import os
import base64
import random

st.set_page_config(page_title="🌿 AI Interior Design Assistant", layout="wide")

# Soft Earthy gradients for main background
background_gradients = [
    "linear-gradient(135deg, #F0EAD6 0%, #C8B69E 100%)",  # Sandstone cream to warm clay
    "linear-gradient(135deg, #E4DCCF 0%, #A89F91 100%)",  # Desert beige to muted stone
    "linear-gradient(135deg, #D7C4A3 0%, #947E64 100%)",  # Fawn to light mocha
    "linear-gradient(135deg, #C9C1A6 0%, #8A8371 100%)",  # Soft olive to ash brown
    "linear-gradient(135deg, #E6D3B3 0%, #BBA17B 100%)",  # Peach sand to driftwood
]

chosen_gradient = random.choice(background_gradients)

# Sidebar background soft earthy gradient
sidebar_gradient = "linear-gradient(135deg, #E8D8C3, #B59E85)"  # Warm almond to vintage tan

# Inject CSS styles for earthy tones and sidebar background
st.markdown(f"""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600&display=swap');

    html, body, [class*="css"] {{
        font-family: 'Montserrat', sans-serif;
    }}

    .stApp {{
        background: {chosen_gradient};
        background-attachment: fixed;
        min-height: 100vh;
    }}

    section[data-testid="stSidebar"] {{
        background: {sidebar_gradient};
        padding: 20px;
        border-top-right-radius: 16px;
        border-bottom-right-radius: 16px;
        box-shadow: 2px 0 15px rgba(0,0,0,0.08);
        color: #4B3B2B;
    }}

    section[data-testid="stSidebar"] h1, h2, h3, label, div {{
        color: #4B3B2B;
    }}

    .stTextInput > div > input,
    .stTextArea > div > textarea,
    .stSelectbox > div,
    .stSlider > div,
    .stNumberInput > div {{
        border-radius: 10px;
        padding: 8px;
        background-color: #FFF9F0CC;  /* soft creamy white */
        color: #4B3B2B;
    }}

    .stButton>button {{
        background-color: #A1866F;
        color: white;
        border: none;
        border-radius: 8px;
        padding: 0.5em 1em;
        font-weight: 600;
        transition: all 0.3s ease;
        cursor: pointer;
    }}
    .stButton>button:hover {{
        background-color: #C4A484;
        transform: scale(1.02);
    }}

    .stRadio > div > label {{
        background: #EFE7D5;
        padding: 5px 10px;
        border-radius: 8px;
        margin-right: 10px;
        color: #4B3B2B;
    }}

    /* Scrollbar for sidebar */
    section[data-testid="stSidebar"]::-webkit-scrollbar {{
        width: 8px;
    }}
    section[data-testid="stSidebar"]::-webkit-scrollbar-thumb {{
        background-color: #A1866F;
        border-radius: 10px;
    }}
    </style>
""", unsafe_allow_html=True)

# Helper: multiply image channel with clipping
def safe_multiply_uint8(img_channel, factor):
    return np.clip(img_channel.astype(np.float32) * factor, 0, 255).astype(np.uint8)

def process_image(image, style):
    img = np.array(image.convert("RGB"))
    if style == "Modern":
        # Slight brightness boost and blur
        for i in range(3):
            img[:, :, i] = safe_multiply_uint8(img[:, :, i], 1.2)
        img = cv2.GaussianBlur(img, (3, 3), 0)
    elif style == "Traditional":
        img[:, :, 0] = safe_multiply_uint8(img[:, :, 0], 0.9)  # Red down
        img[:, :, 1] = safe_multiply_uint8(img[:, :, 1], 1.1)  # Green up
        img[:, :, 2] = safe_multiply_uint8(img[:, :, 2], 1.1)  # Blue up
        img = cv2.GaussianBlur(img, (5, 5), 0)
    elif style == "Industrial":
        gray = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        img[:, :, 0] = safe_multiply_uint8(gray, 0.8)
        img[:, :, 1] = safe_multiply_uint8(gray, 0.9)
        img[:, :, 2] = gray.astype(np.uint8)
    elif style == "Scandinavian":
        pil_img = Image.fromarray(img)
        pil_img = ImageOps.autocontrast(pil_img)
        pil_img = ImageEnhance.Brightness(pil_img).enhance(1.3)
        return pil_img
    elif style == "Bohemian":
        img[:, :, 0] = safe_multiply_uint8(img[:, :, 0], 1.1)  # Warm red boost
        img[:, :, 1] = safe_multiply_uint8(img[:, :, 1], 0.95)
        img[:, :, 2] = safe_multiply_uint8(img[:, :, 2], 0.9)
        img = cv2.GaussianBlur(img, (3, 3), 0)
    elif style == "Minimalist":
        img = cv2.cvtColor(img, cv2.COLOR_RGB2HSV)
        img[:, :, 1] = safe_multiply_uint8(img[:, :, 1], 0.5)  # Reduce saturation
        img[:, :, 2] = safe_multiply_uint8(img[:, :, 2], 1.1)  # Boost brightness
        img = cv2.cvtColor(img, cv2.COLOR_HSV2RGB)
    return Image.fromarray(img)

FURNITURE_DATA = {
    "Modern": [
        "🛋 Sleek sofa", "☕ Glass coffee table", "📚 Minimalist bookshelf",
        "🛏 Platform bed", "💡 LED floor lamp", "🪞 Frameless mirror"
    ],
    "Traditional": [
        "🪑 Wingback chair", "🍽 Wooden dining table", "🗄 Antique cabinet",
        "🕰 Grandfather clock", "🖼 Ornate picture frame", "🛋 Chesterfield sofa"
    ],
    "Industrial": [
        "🛋 Metal-framed couch", "🪵 Reclaimed wood table", "📚 Pipe shelving",
        "💡 Edison bulb pendant", "🛠 Gear wall clock", "🚪 Sliding barn door"
    ],
    "Scandinavian": [
        "🪑 Plywood chair", "🏓 Simple white desk", "📚 Light wood shelf",
        "🛏 Linen bedding", "🌿 Indoor plant stand", "🕯 Minimalist candle holder"
    ],
    "Bohemian": [
        "🧺 Rattan chair", "🌈 Patterned throw pillows", "🪔 Moroccan lantern",
        "🪴 Hanging plants", "🛏 Canopy bed", "🖼 Colorful wall tapestry"
    ],
    "Minimalist": [
        "🛋 Low-profile sofa", "🪟 Large windows", "🗄 Simple storage unit",
        "🛏 Platform bed", "💡 Pendant lighting", "🖼 Black & white prints"
    ],
}

COLOR_PALETTES = {
    "Modern": [
        ("#F4F4F4", "Soft White 🕊"), ("#1A1A1A", "Charcoal Black 🖤"), 
        ("#B0B0B0", "Urban Gray 🏙"), ("#3A86FF", "Electric Blue 🔷"), 
        ("#FF6B6B", "Modern Coral ❤")
    ],
    "Traditional": [
        ("#7C482B", "Earth Brown 🌰"), ("#EED9C4", "Antique Beige 🤎"), 
        ("#5A6536", "Olive Green 🌿"), ("#C68642", "Terracotta 🍂"), 
        ("#641E16", "Deep Maroon 🍷")
    ],
    "Industrial": [
        ("#333533", "Industrial Black ⚙"), ("#7D8597", "Iron Gray 🛠"),
        ("#A3A3A3", "Steel Silver 🧱"), ("#5C5C5C", "Smoky Gray 🔩"), 
        ("#C4C4C4", "Concrete Light 🧱")
    ],
    "Scandinavian": [
        ("#FAFAFA", "Snow White ❄"), ("#DAD7CD", "Moss Mist 🌿"), 
        ("#A3C1AD", "Pale Sage 🌱"), ("#C4D7E0", "Cool Sky 💧"), 
        ("#F2E8CF", "Soft Sand 🌾")
    ],
    "Bohemian": [
        ("#FF9770", "Sunset Coral 🌅"), ("#FFCB77", "Amber Gold 🌞"), 
        ("#A0613D", "Clay Brown 🧡"), ("#3E885B", "Forest Green 🌿"), 
        ("#927FBF", "Lilac Stone 💜")
    ],
    "Minimalist": [
        ("#FFFFFF", "Clean White ⚪"), ("#121212", "Graphite Black ⚫"), 
        ("#D6D6D6", "Fog Gray ☁"), ("#A8A8A8", "Ash Gray 🪨"), 
        ("#E0E0E0", "Pebble Silver 🌫")
    ],
}

# Initialize session state variables
if 'design_history' not in st.session_state:
    st.session_state.design_history = []
if 'uploaded_image' not in st.session_state:
    st.session_state.uploaded_image = None
if 'processed_image' not in st.session_state:
    st.session_state.processed_image = None

def add_furniture_overlay(base_image, furniture_items, style):
    base_image = base_image.convert("RGBA")
    overlay = Image.new("RGBA", base_image.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(overlay)
    w, h = base_image.size
    positions = [(w//6, h//2), (w//2 - 50, h//2), (5*w//6 - 100, h//2)]
    try:
        font = ImageFont.truetype("arial.ttf", 20)
    except:
        font = ImageFont.load_default()
    for idx, (item, pos) in enumerate(zip(furniture_items, positions)):
        size = min(w, h) // 5
        hex_color = COLOR_PALETTES[style][idx % len(COLOR_PALETTES[style])][0]
        # Convert hex to RGBA with alpha
        rgba = tuple(int(hex_color[i:i+2], 16) for i in (1, 3, 5)) + (140,)
        rect_coords = [pos, (pos[0]+size, pos[1]+size)]
        draw.rounded_rectangle(rect_coords, radius=15, fill=rgba, outline=hex_color, width=3)
        draw.text((pos[0]+10, pos[1]+size//3), item, fill="black", font=font)
    combined = Image.alpha_composite(base_image, overlay).convert("RGB")
    return combined

st.title("🏡 AI Interior Design Assistant")
st.subheader("Upload your room photo and visualize different styles")

uploaded_file = st.file_uploader("📷 Upload a room photo", type=["jpg", "jpeg", "png"])
if uploaded_file:
    st.session_state.uploaded_image = uploaded_file
    st.success("✅ Image uploaded successfully!")

with st.sidebar:
    st.header("🎨 Design Preferences")
    style = st.selectbox("Choose your preferred style", list(FURNITURE_DATA.keys()))
    col1, col2 = st.columns(2)
    length = col1.number_input("Length (ft)", 5, 50, 12)
    width = col2.number_input("Width (ft)", 5, 50, 10)
    budget = st.slider("💰 Budget Range", 500, 10000, (1000, 5000))
    user_description = st.text_area("📝 Describe Your Vision")

tab1, tab2, tab3 = st.tabs(["🏠 Original & Styled", "🛋 Recommendations", "📚 History"])

with tab1:
    st.header("🖼 Room Visualization")
    if st.session_state.uploaded_image:
        col1, col2 = st.columns(2)
        col1.image(st.session_state.uploaded_image, caption="Original Room", use_container_width=True)
        img_pil = Image.open(st.session_state.uploaded_image)
        processed_img = process_image(img_pil, style)
        furniture = FURNITURE_DATA[style][:3]
        final_img = add_furniture_overlay(processed_img, furniture, style)
        col2.image(final_img, caption=f"{style} Style", use_container_width=True)
        st.session_state.processed_image = final_img
        if st.button("💾 Save This Design"):
            buffer = io.BytesIO()
            final_img.save(buffer, format='PNG')
            st.session_state.design_history.append({
                "style": style,
                "dimensions": f"{length}x{width}",
                "furniture": furniture,
                "description": user_description,
                "image": buffer.getvalue()
            })
            st.success("✅ Design saved!")

with tab2:
    st.header("🛋 Recommendations")
    if user_description:
        st.success(f"Your vision: '{user_description}' fits best with {style} style.")
    st.subheader("🪑 Furniture Suggestions")
    rows = (len(FURNITURE_DATA[style]) + 3) // 4
    for r in range(rows):
        cols = st.columns(4)
        for c in range(4):
            i = r*4 + c
            if i < len(FURNITURE_DATA[style]):
                hex_color = COLOR_PALETTES[style][i % len(COLOR_PALETTES[style])][0]
                cols[c].image(Image.new('RGB', (150, 150), color=hex_color))
                cols[c].caption(FURNITURE_DATA[style][i])
    st.subheader("🎨 Color Palette")
    cols = st.columns(len(COLOR_PALETTES[style]))
    for col, (hex_color, name) in zip(cols, COLOR_PALETTES[style]):
        col.image(Image.new('RGB', (100, 100), color=hex_color))
        col.markdown(f"<div style='text-align:center'><b>{name}</b></div>", unsafe_allow_html=True)
    st.subheader("📝 Space Tips")
    st.write(f"- 🛋 Focus on essentials for a {length}x{width} ft room")
    st.write(f"- 💸 Budget range: ${budget[0]} - ${budget[1]}")

with tab3:
    st.header("📚 Design History")
    if not st.session_state.design_history:
        st.info("No saved designs.")
    else:
        for i, d in reversed(list(enumerate(st.session_state.design_history, 1))):
            with st.expander(f"Design #{i}: {d['style']} | {d['dimensions']}"):
                c1, c2 = st.columns([1, 2])
                c1.image(d['image'], use_column_width=True)
                c2.write(f"*Description:* {d['description']}")
                c2.write("*Furniture:*")
                for item in d['furniture']:
                    c2.write(f"- {item}")
                # Delete button with key to avoid clashes
                if st.button(f"🗑 Delete #{i}", key=f"delete_{i}"):
                    st.session_state.design_history.pop(i - 1)
                    st.rerun()

st.subheader("💬 Feedback")
feedback = st.radio("How do you like the app?", ["😍 Love it!", "🙂 Okay", "😕 Needs work"])
if st.button("Submit Feedback"):
    st.toast("🙏 Thanks for your feedback!")
