
import base64
from io import BytesIO

import streamlit as st
from google import genai
from PIL import Image, ImageOps


# =====================================================
# PAGE CONFIGURATION
# =====================================================
st.set_page_config(
    page_title="PixelForge AI | Image Studio",
    page_icon="🎨",
    layout="wide",
    initial_sidebar_state="expanded",
)


# =====================================================
# PROFESSIONAL STYLING
# =====================================================
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: Inter, sans-serif;
}

.stApp {
    background: #0b1020;
    color: #f8fafc;
}

[data-testid="stSidebar"] {
    background: #111827;
    border-right: 1px solid #293449;
}

.hero {
    padding: 32px;
    border-radius: 22px;
    border: 1px solid #334155;
    background: linear-gradient(125deg, #172554, #312e81, #1e293b);
    margin-bottom: 28px;
}

.hero h1 {
    font-size: 42px;
    font-weight: 800;
    color: white;
    margin: 0;
}

.hero p {
    color: #dbeafe;
    font-size: 16px;
    margin-top: 12px;
}

.section-heading {
    font-size: 23px;
    font-weight: 700;
    margin-bottom: 15px;
}

div.stButton > button,
div.stDownloadButton > button {
    width: 100%;
    min-height: 46px;
    border-radius: 12px;
    font-weight: 700;
}

div.stButton > button[kind="primary"] {
    background: linear-gradient(90deg, #6366f1, #8b5cf6);
    color: white;
    border: none;
}

div.stDownloadButton > button {
    background: #4f46e5;
    color: white;
    border: none;
}

div[data-testid="stTextArea"] textarea {
    border-radius: 12px;
}

.feature {
    padding: 17px;
    background: #111827;
    border: 1px solid #293449;
    border-radius: 14px;
    text-align: center;
}

.footer {
    text-align: center;
    color: #94a3b8;
    padding: 25px 0;
}
</style>
""", unsafe_allow_html=True)


# =====================================================
# SESSION STATE
# =====================================================
if "generated_image" not in st.session_state:
    st.session_state.generated_image = None

if "last_prompt" not in st.session_state:
    st.session_state.last_prompt = ""


# =====================================================
# HEADER
# =====================================================
st.markdown("""
<div class="hero">
    <h1>🎨 PixelForge AI</h1>
    <p>
        Turn your imagination into stunning images.
        Describe your idea, customize your style, and create.
    </p>
</div>
""", unsafe_allow_html=True)


# =====================================================
# SIDEBAR SETTINGS
# =====================================================
with st.sidebar:
    st.markdown("## 🎨 PixelForge AI")
    st.caption("Your personal AI image studio")
    st.divider()

    st.markdown("### Image settings")

    model = "gemini-3.1-flash-image"

    style = st.selectbox(
        "Choose an art style",
        [
            "Photorealistic",
            "3D Cartoon",
            "Anime",
            "Cinematic",
            "Digital Art",
            "Fantasy Art",
            "Watercolor Painting",
            "Product Photography",
            "Minimalist Illustration",
            "Children's Storybook",
        ],
    )

    aspect_ratio = st.selectbox(
        "Aspect ratio",
        ["1:1", "9:16", "16:9", "4:3", "3:4"],
    )

    image_size = st.selectbox(
        "Image resolution",
        ["1K", "2K", "4K"],
        index=0,
    )

    st.divider()
    st.caption("Model: Gemini 3.1 Flash Image")
    st.caption("Your API key stays in Streamlit Secrets.")


# =====================================================
# MAIN WORKSPACE
# =====================================================
left, right = st.columns([1, 1.05], gap="large")

with left:
    st.markdown(
        '<div class="section-heading">✍️ Create your image</div>',
        unsafe_allow_html=True,
    )

    prompt = st.text_area(
        "Describe your imagination",
        placeholder=(
            "Example: A cute orange kitten playing with "
            "a colorful ball in a magical garden, "
            "soft sunlight, beautiful details..."
        ),
        height=180,
        max_chars=4000,
    )

    negative_prompt = st.text_input(
        "Avoid these details (optional)",
        placeholder="Blurry, low quality, unwanted objects...",
    )

    st.caption(
        "Tip: Describe your subject, background, lighting, "
        "colors, and mood for a more detailed result."
    )

    generate = st.button(
        "✨ Generate AI Image",
        type="primary",
        use_container_width=True,
    )

    clear = st.button(
        "🧹 Clear workspace",
        use_container_width=True,
    )

    if clear:
        st.session_state.generated_image = None
        st.session_state.last_prompt = ""
        st.rerun()


# =====================================================
# IMAGE GENERATION
# =====================================================
if generate:
    if not prompt.strip():
        st.warning("Please enter a description first.")

    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            if not api_key.strip():
                st.error("Your Gemini API key is empty.")

            else:
                client = genai.Client(api_key=api_key)

                final_prompt = (
                    f"Create a high-quality {style} image. "
                    f"Image description: {prompt.strip()}. "
                    f"Use a {aspect_ratio} aspect ratio. "
                    "Create a polished, visually appealing composition."
                )

                if negative_prompt.strip():
                    final_prompt += (
                        " Avoid these unwanted details where possible: "
                        + negative_prompt.strip()
                    )

                with st.spinner(
                    "✨ Gemini is creating your masterpiece..."
                ):
                    result = client.interactions.create(
                        model=model,
                        input=final_prompt,
                        response_format={
                            "type": "image",
                            "mime_type": "image/png",
                            "aspect_ratio": aspect_ratio,
                            "image_size": image_size,
                        },
                    )

                output_image = getattr(
                    result, "output_image", None
                )

                image_data = (
                    getattr(output_image, "data", None)
                    if output_image else None
                )

                if image_data:
                    if isinstance(image_data, str):
                        image_bytes = base64.b64decode(image_data)
                    else:
                        image_bytes = image_data

                    generated = Image.open(
                        BytesIO(image_bytes)
                    )
                    generated.load()

                    st.session_state.generated_image = generated.copy()
                    st.session_state.last_prompt = prompt.strip()

                else:
                    st.error(
                        "No image was returned. Try another prompt "
                        "or check your model access."
                    )

                    output_text = getattr(
                        result, "output_text", None
                    )

                    if output_text:
                        st.write(output_text)

        except KeyError:
            st.error(
                "API key missing. Open Streamlit app settings, "
                "select Secrets, and add GEMINI_API_KEY."
            )

        except Exception as error:
            st.error(
                "Image generation failed. Check the technical "
                "details below to identify the cause."
            )

            with st.expander("Technical details"):
                st.code(str(error))


# =====================================================
# RESULTS AND DOWNLOAD
# =====================================================
with right:
    st.markdown(
        '<div class="section-heading">🖼️ Your masterpiece</div>',
        unsafe_allow_html=True,
    )

    if st.session_state.generated_image is not None:
        image = st.session_state.generated_image

        st.image(
            image,
            caption="Created with PixelForge AI",
            use_container_width=True,
        )

        image_buffer = BytesIO()
        image.convert("RGB").save(
            image_buffer,
            format="PNG",
        )

        st.download_button(
            label="⬇️ Download Image (PNG)",
            data=image_buffer.getvalue(),
            file_name="pixelforge_ai_image.png",
            mime="image/png",
            use_container_width=True,
        )

        with st.expander("View your prompt"):
            st.write(st.session_state.last_prompt)

    else:
        st.markdown("""
        <div style="
            min-height: 300px;
            border: 1px dashed #475569;
            border-radius: 18px;
            display: flex;
            align-items: center;
            justify-content: center;
            text-align: center;
            padding: 25px;
            background: #111827;
        ">
            <div>
                <div style="font-size: 55px;">🎨</div>
                <h3>Your canvas is ready</h3>
                <p style="color: #94a3b8;">
                    Your generated image will appear here.
                </p>
            </div>
        </div>
        """, unsafe_allow_html=True)


# =====================================================
# FOOTER
# =====================================================
st.divider()

st.markdown("""
<div class="footer">
    <strong>PixelForge AI</strong><br>
    Creative possibilities powered by Google Gemini
</div>
""", unsafe_allow_html=True)
