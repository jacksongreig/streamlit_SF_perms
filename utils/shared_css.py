import streamlit as st

def inject_shared_css():
    st.markdown("""
        <style>

        /* ───────────── App Background ───────────── */
        [data-testid="stAppViewContainer"] {
            background-color: #f0f2f6;
        }

        /* ───────────── Headings ───────────── */
        h1, h2, h3 {
            color: #003366 !important;
            font-weight: 700 !important;
        }

        /* ───────────── Form Labels ───────────── */
        label,
        .stTextInput > label,
        .stSelectbox > label,
        .stTextArea > label,
        .stCheckbox > label,
        .stCheckbox span {
            color: #003366 !important;
            font-weight: 600 !important;
            font-size: 0.95rem !important;
        }

        /* ───────────── Buttons ───────────── */
        .stButton > button {
            width: 100%;
            min-height: 60px;
            background-color: #003366 !important;
            color: white !important;
            font-size: 1.05rem;
            font-weight: 600;
            border-radius: 10px;
            border: none;
            transition: background-color 0.3s ease;
        }

        .stButton > button:hover {
            background-color: #005599 !important;
        }

        /* ───────────── Code Blocks (YAML) ───────────── */
        .stCodeBlock pre {
            background-color: #1e1e1e !important;
            color: #f8f8f2 !important;
            font-size: 0.9rem;
            padding: 1.25rem;
            border-radius: 12px;
        }

        /* ───────────── Page Containers ───────────── */
        .tool-container, .home-container {
            max-width: 800px;
            margin: 0 auto;
            background-color: #ffffff;
            padding: 2.5rem;
            border-radius: 16px;
            box-shadow: 0 4px 20px rgba(0, 0, 0, 0.1);
        }

        </style>
    """, unsafe_allow_html=True)