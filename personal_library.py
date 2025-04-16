import streamlit as st
from PIL import Image
import json
import os

# Initialize session state
if 'books' not in st.session_state:
    st.session_state.books = []

# Page config
st.set_page_config(page_title="Personal Library Manager", page_icon="📚", layout="centered")

# --- Custom Styling ---
st.markdown("""
<style>
    html, body, [class*="css"] {
        font-family: 'Segoe UI', sans-serif;
        background-color: #F9FAFB;
    }

    .main-header {
        font-size: 3.2rem !important;
        color: #111827;
        font-weight: 800;
        text-align: center;
        margin-bottom: 2rem;
    }

    .sub-header {
        font-size: 1.6rem !important;
        color: #2563EB;
        font-weight: 600;
        margin-bottom: 1.5rem;
    }

    .success-message, .warning-message {
        border-radius: 12px;
        padding: 1.2rem;
        font-weight: 500;
        font-size: 1rem;
    }

    .success-message {
        background-color: #DCFCE7;
        color: #065F46;
        border-left: 6px solid #34D399;
    }

    .warning-message {
        background-color: #FEF9C3;
        color: #92400E;
        border-left: 6px solid #FBBF24;
    }

    .book-card {
        background-color: #FFFFFF;
        border-radius: 12px;
        padding: 1rem 1.25rem;
        margin-bottom: 1.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.03);
        transition: all 0.3s ease;
    }

    .book-card:hover {
        transform: translateY(-3px);
        box-shadow: 0 10px 20px rgba(0, 0, 0, 0.05);
    }

    .read-badge, .unread-badge {
        font-size: 0.875rem;
        font-weight: 600;
        padding: 0.35rem 0.85rem;
        border-radius: 20px;
        display: inline-block;
    }

    .read-badge {
        background-color: #4ADE80;
        color: #065F46;
    }

    .unread-badge {
        background-color: #FCA5A5;
        color: #7F1D1D;
    }

    .stButton>button {
        background-color: #2563EB;
        color: white;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        transition: background 0.3s ease;
    }

    .stButton>button:hover {
        background-color: #1E40AF;
    }

    .stTextInput>div>input, .stNumberInput input, .stSelectbox div, .stRadio div {
        border-radius: 8px !important;
        padding: 0.5rem !important;
        background-color: #FFFFFF;
        border: 1px solid #D1D5DB;
    }

    h3 {
        color: #1F2937;
        margin-bottom: 0.3rem;
    }

    p {
        color: #4B5563;
        margin: 0.25rem 0;
    }

    footer {
        margin-top: 3rem;
        font-size: 0.9rem;
        color: #6B7280;
        text-align: center;
    }
</style>
""", unsafe_allow_html=True)

# --- Header ---
st.markdown("<h1 class='main-header'>📚 Welcome to Your Personal Library</h1>", unsafe_allow_html=True)
st.markdown("<div class='sub-header'>Curated by Zameer Ahmed</div>", unsafe_allow_html=True)

# --- Add Book Form ---
with st.form("add_book_form"):
    st.subheader("➕ Add a New Book")
    title = st.text_input("Book Title")
    author = st.text_input("Author")
    year = st.number_input("Year Published", min_value=0, max_value=9999, step=1)
    status = st.radio("Read Status", ("Read", "Unread"))
    submit = st.form_submit_button("Add Book")

    if submit:
        if title and author and year:
            book = {"title": title, "author": author, "year": year, "status": status}
            st.session_state.books.append(book)
            st.toast("Nice! That book is in your library now ✅", icon="📘")
        else:
            st.warning("Please fill in all fields before submitting.", icon="⚠️")

# --- Display Library ---
st.subheader("📖 Your Library Collection")

if st.session_state.books:
    for idx, book in enumerate(st.session_state.books):
        st.markdown(f"""
        <div class='book-card'>
            <h3>{book['title']}</h3>
            <p>✍️ <b>Author:</b> {book['author']}</p>
            <p>📅 <b>Year:</b> {book['year']}</p>
            <p>Status: <span class="{ 'read-badge' if book['status'] == 'Read' else 'unread-badge' }">{book['status']}</span></p>
        </div>
        """, unsafe_allow_html=True)
else:
    st.info("No books yet. Start adding some to build your collection!", icon="📂")

# --- Footer ---
st.markdown("---")
st.markdown("© 2025 Zameer Ahmed — Personal Library Manager | Crafted with ❤️ and Streamlit", unsafe_allow_html=True)
