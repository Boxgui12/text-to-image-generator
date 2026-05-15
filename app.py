import base64
import json
import os
import re
from dataclasses import dataclass
from typing import Optional

import requests
import streamlit as st


APP_TITLE = "Text to Image Generator"
APP_ICON = "🎨"
ENGINE_ID = "stable-diffusion-xl-1024-v1-0"
API_URL = f"https://api.stability.ai/v1/generation/{ENGINE_ID}/text-to-image"
CLIENT_ID = "text-image-generator-streamlit"
CLIENT_VERSION = "1.0.0"

SPANISH_PROMPTS = [
    "• Un robot adorable pintando un cuadro",
    "• Una ciudad futurista con autos voladores",
    "• Una cafetería acogedora en un día lluvioso",
]

ENGLISH_PROMPTS = [
    "• A cute robot painting a picture",
    "• A futuristic city with flying cars",
    "• A cozy coffee shop on a rainy day",
]

TEXT = {
    "es": {
        "title": "Generador de texto a imagen",
        "switch": "English",
        "prompt_label": "Describe tu imagen:",
        "examples_title": "Prompts de ejemplo:",
        "button": "Generar imagen",
        "success": "¡Imagen generada correctamente!",
        "download": "Descargar imagen",
        "image_caption": "Imagen generada",
        "missing_key": "Falta la variable de entorno `STABILITY_API_KEY`.",
        "empty_prompt": "Escribe una descripción antes de generar la imagen.",
        "api_error": "No se pudo generar la imagen. Revisa tu API key y vuelve a intentarlo.",
        "network_error": "No se pudo conectar con Stability AI.",
        "generation_failed": "La API respondió, pero no devolvió una imagen válida.",
        "prompt_placeholder": "Escribe aquí la escena que quieres generar...",
        "helper": "Prueba uno de los prompts de abajo o escribe el tuyo propio.",
        "env_hint": "Configura `STABILITY_API_KEY` en tu entorno antes de ejecutar la app.",
        "error_details": "Detalles del error",
    },
    "en": {
        "title": "Text to Image Generator",
        "switch": "Español",
        "prompt_label": "Enter your image description:",
        "examples_title": "Example prompts:",
        "button": "Generate Image",
        "success": "Image generated successfully!",
        "download": "Download Image",
        "image_caption": "Generated Image",
        "missing_key": "Missing the `STABILITY_API_KEY` environment variable.",
        "empty_prompt": "Write a description before generating an image.",
        "api_error": "The image could not be generated. Check your API key and try again.",
        "network_error": "Could not connect to Stability AI.",
        "generation_failed": "The API responded, but it did not return a valid image.",
        "prompt_placeholder": "Describe the scene you want to generate...",
        "helper": "Try one of the prompts below or write your own.",
        "env_hint": "Set `STABILITY_API_KEY` in your environment before running the app.",
        "error_details": "Error details",
    },
}


@dataclass
class GenerationResult:
    image_bytes: bytes
    seed: Optional[int] = None


def get_language() -> str:
    if "language_is_english" not in st.session_state:
        st.session_state.language_is_english = False
    return "en" if st.session_state.language_is_english else "es"


def get_text(lang: str) -> dict:
    return TEXT[lang]


def get_default_prompt(lang: str) -> str:
    return SPANISH_PROMPTS[0] if lang == "es" else ENGLISH_PROMPTS[0]


def sanitize_filename(prompt: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", prompt.lower()).strip("-")
    if not slug:
        slug = "generated-image"
    return f"{slug[:40]}.png"


def build_headers(api_key: str) -> dict:
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Accept": "application/json",
        "Stability-Client-ID": CLIENT_ID,
        "Stability-Client-Version": CLIENT_VERSION,
    }
    org_id = os.getenv("STABILITY_ORG_ID", "").strip()
    if org_id:
        headers["Organization"] = org_id
    return headers


def generate_image(prompt: str, api_key: str) -> GenerationResult:
    payload = {
        "text_prompts": [{"text": prompt, "weight": 1}],
        "cfg_scale": 7,
        "height": 1024,
        "width": 1024,
        "samples": 1,
        "steps": 30,
        "style_preset": "enhance",
    }

    response = requests.post(
        API_URL,
        headers=build_headers(api_key),
        json=payload,
        timeout=120,
    )

    if response.status_code >= 400:
        raise requests.HTTPError(response.text, response=response)

    try:
        data = response.json()
    except json.JSONDecodeError as exc:
        raise ValueError("Invalid JSON response from Stability AI.") from exc

    artifacts = data.get("artifacts") or []
    if not artifacts:
        raise ValueError("No artifacts returned by Stability AI.")

    artifact = artifacts[0]
    image_b64 = artifact.get("base64")
    if not image_b64:
        raise ValueError("Missing image data in Stability AI response.")

    return GenerationResult(
        image_bytes=base64.b64decode(image_b64),
        seed=artifact.get("seed"),
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
            .block-container {
                padding-top: 1.5rem;
                padding-bottom: 2rem;
                max-width: 860px;
            }

            h1 {
                letter-spacing: -0.04em;
            }

            .stToggle {
                padding-top: 0.45rem;
            }

            .stButton > button {
                border-radius: 0.7rem;
                border: 1px solid rgba(0, 0, 0, 0.12);
                padding: 0.7rem 1rem;
                font-weight: 700;
            }

            .stButton > button[kind="primary"] {
                background: linear-gradient(180deg, #ff685c 0%, #ff4b42 100%);
                border-color: #ff4b42;
                color: white;
            }

            .stDownloadButton > button {
                border-radius: 0.7rem;
            }

            textarea {
                border-radius: 0.85rem !important;
            }

        </style>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, page_icon=APP_ICON, layout="centered")
    inject_styles()

    lang = get_language()
    text = get_text(lang)

    if "prompt" not in st.session_state:
        st.session_state.prompt = get_default_prompt(lang)
    if "active_language" not in st.session_state:
        st.session_state.active_language = lang
    if st.session_state.active_language != lang:
        known_prompts = set(SPANISH_PROMPTS + ENGLISH_PROMPTS)
        if not st.session_state.prompt.strip() or st.session_state.prompt in known_prompts:
            st.session_state.prompt = get_default_prompt(lang)
        st.session_state.active_language = lang

    sidebar = st.sidebar
    sidebar.title("Settings" if lang == "en" else "Configuración")
    sidebar.caption(
        "Your API key stays in this browser session only."
        if lang == "en"
        else "Tu API key se mantiene solo en esta sesión del navegador."
    )
    sidebar_api_key = sidebar.text_input(
        "STABILITY_API_KEY",
        type="password",
        placeholder="sk-..." if lang == "en" else "sk-...",
        help="Set your Stability AI key here." if lang == "en" else "Ingresa aquí tu clave de Stability AI.",
        key="sidebar_stability_api_key",
    )
    api_key = sidebar_api_key.strip()

    if sidebar_api_key.strip():
        sidebar.success("API key loaded" if lang == "en" else "API key cargada")
    else:
        sidebar.warning(
            "Add your `STABILITY_API_KEY` to continue."
            if lang == "en"
            else "Agrega tu `STABILITY_API_KEY` para continuar."
        )

    header_left, header_right = st.columns([6, 1], vertical_alignment="center")
    with header_left:
        st.title(f"{APP_ICON} {text['title']}")
    with header_right:
        st.toggle(text["switch"], key="language_is_english")

    st.divider()

    st.write(text["prompt_label"])
    prompt = st.text_area(
        label="",
        key="prompt",
        height=100,
        placeholder=text["prompt_placeholder"],
    )
    st.caption(text["helper"])
    st.markdown(f"**{text['examples_title']}**")
    for example in SPANISH_PROMPTS if lang == "es" else ENGLISH_PROMPTS:
        st.markdown(example)

    generate_clicked = st.button(text["button"], type="primary")

    if generate_clicked:
        if not api_key:
            st.error(text["missing_key"])
            st.info(text["env_hint"])
            st.stop()

        if not prompt.strip():
            st.warning(text["empty_prompt"])
            st.stop()

        with st.spinner("Generating..." if lang == "en" else "Generando..."):
            try:
                result = generate_image(prompt.strip(), api_key)
            except requests.HTTPError as exc:
                st.error(text["api_error"])
                with st.expander(text["error_details"]):
                    st.code(str(exc))
                return
            except requests.RequestException as exc:
                st.error(text["network_error"])
                with st.expander(text["error_details"]):
                    st.code(str(exc))
                return
            except Exception as exc:
                st.error(text["generation_failed"])
                with st.expander(text["error_details"]):
                    st.code(str(exc))
                return

        st.session_state.generated_image = result.image_bytes
        st.session_state.generated_prompt = prompt.strip()
        st.success(text["success"])

    if "generated_image" in st.session_state:
        st.image(
            st.session_state.generated_image,
            caption=text["image_caption"],
            use_container_width=True,
        )
        st.download_button(
            text["download"],
            data=st.session_state.generated_image,
            file_name=sanitize_filename(st.session_state.get("generated_prompt", prompt)),
            mime="image/png",
        )


if __name__ == "__main__":
    main()
