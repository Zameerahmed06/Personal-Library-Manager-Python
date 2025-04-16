import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime
import time
import random
import plotly.express as px
import plotly.graph_objects as go
from streamlit_lottie import st_lottie
import requests

# Updated Page Configuration
st.set_page_config(
    page_title="Sterling Library Hub",
    page_icon="📖",  # Changed icon
    layout="wide",
    initial_sidebar_state="expanded"
)

# Updated Custom CSS for a fresh UI feel
st.markdown("""
<style>
    .main-header {
        font-size: 3rem !important;
        color: #6D28D9;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.1);
    }
    .sub-header {
        font-size: 1.8rem !important;
        color: #8B5CF6;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1rem;
    }
    .success-message {
        padding: 1rem;
        background-color: #ECFDF5;
        border-left: 5px solid #14B8A6;
        border-radius: 0.375rem;
    }
    .warning-message {
        padding: 1rem;
        background-color: #FEF3C7;
        border-left: 5px solid #EAB308;
        border-radius: 0.375rem;
    }
    .book-card {
        background-color: #F9FAFB;
        border-radius: 0.5rem;
        padding: 1rem;
        margin-bottom: 1rem;
        border-left: 5px solid #8B5CF6;
        transition: transform 0.3s ease;
    }
    .book-card:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1);
    }
    .read-badge {
        background-color: #16A34A;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .unread-badge {
        background-color: #DC2626;
        color: white;
        padding: 0.25rem 0.75rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }
    .action-button {
        margin-right: 0.5rem;
    }
    .stButton>button {
        border-radius: 0.375rem;
    }
</style>
""", unsafe_allow_html=True)

# Lottie animation loader
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Session state init
if 'library' not in st.session_state:
    st.session_state.library = []
if 'search_results' not in st.session_state:
    st.session_state.search_results = []
if 'book_added' not in st.session_state:
    st.session_state.book_added = False
if 'book_removed' not in st.session_state:
    st.session_state.book_removed = False
if 'current_view' not in st.session_state:
    st.session_state.current_view = "library"

# Load/save functions
def load_library():
    try:
        if os.path.exists('library.json'):
            with open('library.json', 'r') as file:
                st.session_state.library = json.load(file)
            return True
        return False
    except Exception as e:
        st.error(f"Error loading library: {e}")
        return False

def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

def add_book(title, author, publication_year, genre, read_status):
    book = {
        'title': title,
        'author': author,
        'publication_year': publication_year,
        'genre': genre,
        'read_status': read_status,
        'added_date': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    }
    st.session_state.library.append(book)
    save_library()
    st.session_state.book_added = True
    time.sleep(0.5)

def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

def search_books(search_term, search_by):
    search_term = search_term.lower()
    results = []
    for book in st.session_state.library:
        if search_by == "Title" and search_term in book['title'].lower():
            results.append(book)
        elif search_by == "Author" and search_term in book['author'].lower():
            results.append(book)
        elif search_by == "Genre" and search_term in book['genre'].lower():
            results.append(book)
    st.session_state.search_results = results

def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    genres, authors, decades = {}, {}, {}

    for book in st.session_state.library:
        genres[book['genre']] = genres.get(book['genre'], 0) + 1
        authors[book['author']] = authors.get(book['author'], 0) + 1
        decade = (book['publication_year'] // 10) * 10
        decades[decade] = decades.get(decade, 0) + 1

    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': dict(sorted(genres.items(), key=lambda x: x[1], reverse=True)),
        'authors': dict(sorted(authors.items(), key=lambda x: x[1], reverse=True)),
        'decades': dict(sorted(decades.items(), key=lambda x: x[0]))
    }

def create_visualizations(stats):
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=.4,
            marker_colors=['#16A34A', '#DC2626']
        )])
        fig_read_status.update_layout(title_text="Read vs Unread Books", height=400)
        st.plotly_chart(fig_read_status, use_container_width=True)

    if stats['genres']:
        genres_df = pd.DataFrame({'Genre': list(stats['genres'].keys()), 'Count': list(stats['genres'].values())})
        fig_genres = px.bar(genres_df, x='Genre', y='Count', color='Count', color_continuous_scale='Purples')
        fig_genres.update_layout(title_text="Books by Genre", height=400)
        st.plotly_chart(fig_genres, use_container_width=True)

    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{dec}s" for dec in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(decades_df, x='Decade', y='Count', markers=True, line_shape="spline")
        fig_decades.update_layout(title_text="Books by Publication Decade", height=400)
        st.plotly_chart(fig_decades, use_container_width=True)

# Load data
load_library()

# Sidebar with new icons and animation
st.sidebar.markdown("<h1 style='text-align: center;'>📖 Menu</h1>", unsafe_allow_html=True)
lottie_book = load_lottieurl("https://assets1.lottiefiles.com/packages/lf20_jcikwtux.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=180, key="book_ani")

nav_options = st.sidebar.radio("Navigate", ["📚 View Library", "📝 Add Book", "🔍 Search Books", "📊 Library Stats"])
st.session_state.current_view = nav_options.split(" ")[1].lower()

# App title
st.markdown("<h1 class='main-header'>📖 Sterling Library Hub</h1>", unsafe_allow_html=True)

# Views
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>📝 Add a New Book</h2>", unsafe_allow_html=True)
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        with col1:
            title = st.text_input("Book Title")
            author = st.text_input("Author")
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1)
        with col2:
            genre = st.selectbox("Genre", ["Fiction", "Non-Fiction", "Sci-Fi", "Fantasy", "Mystery", "Romance", "Thriller", "Biography", "History", "Self-Help", "Poetry", "Science", "Philosophy", "Religion", "Art", "Other"])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        if st.form_submit_button("Add Book") and title and author:
            add_book(title, author, publication_year, genre, read_bool)

    if st.session_state.book_added:
        st.markdown("<div class='success-message'>✅ Book added successfully!</div>", unsafe_allow_html=True)
        st.balloons()
        st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>📚 Your Library</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>📭 No books found. Start by adding some!</div>", unsafe_allow_html=True)
    else:
        cols = st.columns(2)
        for i, book in enumerate(st.session_state.library):
            with cols[i % 2]:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"Read" if book["read_status"] else "Unread"}</span></p>
                </div>
                """, unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🗑️ Remove", key=f"remove_{i}"):
                        if remove_book(i):
                            st.rerun()
                with col2:
                    status_label = "📗 Mark as Read" if not book['read_status'] else "📕 Mark as Unread"
                    if st.button(status_label, key=f"status_{i}"):
                        st.session_state.library[i]['read_status'] = not book['read_status']
                        save_library()
                        st.rerun()
        if st.session_state.book_removed:
            st.markdown("<div class='success-message'>🗑️ Book removed successfully!</div>", unsafe_allow_html=True)
            st.session_state.book_removed = False

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>🔍 Search Books</h2>", unsafe_allow_html=True)
    search_by = st.selectbox("Search by:", ["Title", "Author", "Genre"])
    search_term = st.text_input("Enter keyword:")
    if st.button("Search"):
        if search_term:
            with st.spinner("Searching..."):
                time.sleep(0.5)
                search_books(search_term, search_by)
    if hasattr(st.session_state, 'search_results'):
        if st.session_state.search_results:
            st.markdown(f"<h3>📌 Found {len(st.session_state.search_results)} match(es):</h3>", unsafe_allow_html=True)
            for book in st.session_state.search_results:
                st.markdown(f"""
                <div class='book-card'>
                    <h3>{book['title']}</h3>
                    <p><strong>Author:</strong> {book['author']}</p>
                    <p><strong>Year:</strong> {book['publication_year']}</p>
                    <p><strong>Genre:</strong> {book['genre']}</p>
                    <p><span class='{"read-badge" if book["read_status"] else "unread-badge"}'>
                        {"Read" if book["read_status"] else "Unread"}</span></p>
                </div>
                """, unsafe_allow_html=True)
        elif search_term:
            st.markdown("<div class='warning-message'>🔍 No matching results found.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>📊 Library Stats</h2>", unsafe_allow_html=True)
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>📭 Your library is empty. Add books to see stats!</div>", unsafe_allow_html=True)
    else:
        stats = get_library_stats()
        col1, col2, col3 = st.columns(3)
        col1.metric("📚 Total Books", stats['total_books'])
        col2.metric("📗 Read", stats['read_books'])
        col3.metric("📈 % Read", f"{stats['percent_read']:.1f}%")
        create_visualizations(stats)

        if stats['authors']:
            st.markdown("<h3>🧑‍💼 Top Authors</h3>", unsafe_allow_html=True)
            for author, count in list(stats['authors'].items())[:5]:
                st.markdown(f"**{author}**: {count} book{'s' if count > 1 else ''}")

# Footer
st.markdown("---")
st.markdown("© 2025 Zameer Ahmed | Sterling Library Hub • Made with ❤️ and Streamlit", unsafe_allow_html=True)
