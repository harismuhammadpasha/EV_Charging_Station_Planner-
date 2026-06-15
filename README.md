# EV Charging Station Planner

Streamlit app that computes EV-aware routes, charging stops, and visualizes the network.

Quick start (local):

1. Create a Python virtualenv and activate it.

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
streamlit run streamlit_app.py
```

Recommended deployment:

- Use Streamlit Community Cloud (https://share.streamlit.io/) — connect your GitHub repo and deploy the `streamlit_app.py` app directly.
- Vercel serves static sites and serverless functions; it is not a drop-in host for Streamlit apps. If you need a web UI on Vercel, consider converting to a React frontend that calls a backend API, or use a Docker-based deployment on a platform that supports containers.

What I changed:

- Improved UI styling in `streamlit_app.py` (CSS injection, cleaner header, color tweaks).
- Added `requirements.txt` for dependency clarity.
- Added a static `public/index.html` so Vercel will serve a landing page (prevents 404) with guidance and links.

Next steps (optional):

- Deploy to Streamlit Cloud for an interactive public instance.
- Create a small static webpage on Vercel that links to the live Streamlit app, or build a dedicated frontend for Vercel.
