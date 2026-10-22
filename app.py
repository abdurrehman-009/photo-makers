
import streamlit as st
import base64
from io import BytesIO
from google import genai
from PIL import Image

st.set_page_config(
    page_title="PixelForge AI",
    page_icon="🎨",
    layout="wide"
)

st.title("🎨 PixelForge AI")
st.write("Create beautiful AI images from your imagination.")

st.sidebar.header("Image Settings")

model = st.sidebar.selectbox(
    "Gemini Image Model",
    ["gemini-3.1-flash-image"]
)

aspect_ratio = st.sidebar.selectbox(
    "Image Ratio",
    ["1:1", "16:9", "9:16", "4:3", "3:4"]
)

image_size = st.sidebar.selectbox(
    "Image Resolution",
    ["1K", "2K", "4K"]
)

prompt = st.text_area(
    "Describe your image",
    placeholder="A cute orange cat playing with a colorful ball...",
    height=150
)

generate = st.button("✨ Generate Image", type="primary")

if generate:
    if not prompt.strip():
        st.warning("Please enter an image description.")
    else:
        try:
            api_key = st.secrets["GEMINI_API_KEY"]

            client = genai.Client(api_key=api_key)

            with st.spinner("Creating your image..."):
                result = client.interactions.create(
                    model=model,
                    input=prompt.strip(),
                    response_format={
                        "type": "image",
                        "mime_type": "image/png",
                        "aspect_ratio": aspect_ratio,
                        "image_size": image_size
                    }
                )

            output_image = getattr(result, "output_image", None)

            if output_image and output_image.data:
                image_bytes = base64.b64decode(output_image.data)
                image = Image.open(BytesIO(image_bytes)).convert("RGB")

                st.success("Image generated successfully!")
                st.image(image, caption="Your AI-generated image",
                         use_container_width=True)

                download_buffer = BytesIO()
                image.save(download_buffer, format="PNG")

                st.download_button(
                    label="⬇️ Download Image",
                    data=download_buffer.getvalue(),
                    file_name="pixelforge_image.png",
                    mime="image/png"
                )
            else:
                st.error("Gemini did not return an image.")
                if getattr(result, "output_text", None):
                    st.write(result.output_text)

        except KeyError:
            st.error(
                "API key missing. Add GEMINI_API_KEY in "
                "your Streamlit app Secrets."
            )

        except Exception as error:
            st.error("Image generation failed.")
            with st.expander("View error details"):
                st.code(str(error))

st.divider()
st.caption("PixelForge AI | Powered by Google Gemini")
