# Text Image Generator

Simple Streamlit app that turns text prompts into AI-generated images with Stability AI.

## Features

- Spanish by default with an English/Spanish switch
- Text prompt input
- Stability AI text-to-image integration
- Inline image preview
- Download button for generated PNGs
- Environment-variable based API key loading

## Setup

1. Install dependencies:

```bash
python -m venv .venv
.venv\Scripts\python -m pip install -r requirements.txt
```

2. Create a local `.env` file or set environment variables in your shell.
   Copy `.env.example` to `.env` and fill in your values.

```bash
copy .env.example .env
```

3. Set your API key:

```bash
set STABILITY_API_KEY=your_key_here
```

Optional:

```bash
set STABILITY_ORG_ID=your_org_id_here
```

4. Run the app:

```bash
.venv\Scripts\streamlit run app.py
```

## Security Notes

- Do not commit `.env`, `.streamlit/secrets.toml`, or any file containing API keys.
- Keep `.venv/` out of Git. The included `.gitignore` already excludes it.
- If you need to share configuration, update `.env.example` instead of real secrets.

## Example prompts

- A cute robot painting a picture
- A futuristic city with flying cars
- A cozy coffee shop on a rainy day
