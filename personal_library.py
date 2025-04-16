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

# Set page configuration
st.set_page_config(
    page_title="Personal Library Manager",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for styling (updated)
st.markdown("""
<style>
    /* Overall page and font styles */
    body {
        font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        background-color: #F7FAFC;
    }

    .main-header {
        font-size: 3rem !important;
        color: #3B82F6;
        font-weight: 700;
        margin-bottom: 1rem;
        text-align: center;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.2);
    }

    .sub-header {
        font-size: 1.6rem !important;
        color: #6366F1;
        font-weight: 600;
        margin-top: 1rem;
        margin-bottom: 1.5rem;
    }

    .success-message, .warning-message {
        padding: 1rem;
        border-radius: 0.375rem;
        box-shadow: 0 2px 5px rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    .success-message {
        background-color: #D1FAE5;
        border-left: 5px solid #34D399;
    }

    .warning-message {
        background-color: #FEF9C3;
        border-left: 5px solid #FBBF24;
    }

    /* Card styles for books */
    .book-card {
        background-color: #FFFFFF;
        border-radius: 1rem;
        padding: 1rem;
        margin-bottom: 1.5rem;
        box-shadow: 0 4px 10px rgba(0, 0, 0, 0.05);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    .book-card:hover {
        transform: translateY(-8px);
        box-shadow: 0 15px 30px rgba(0, 0, 0, 0.1);
    }

    /* Badge styles for read/unread status */
    .read-badge {
        background-color: #34D399;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }

    .unread-badge {
        background-color: #FBBF24;
        color: white;
        padding: 0.4rem 1rem;
        border-radius: 1rem;
        font-size: 0.875rem;
        font-weight: 600;
    }

    /* Button styles */
    .action-button {
        background-color: #6366F1;
        color: white;
        padding: 0.5rem 1rem;
        border-radius: 0.375rem;
        font-size: 1rem;
        font-weight: 500;
        border: none;
        transition: background-color 0.2s ease;
    }

    .action-button:hover {
        background-color: #4F46E5;
    }

    .stButton>button {
        border-radius: 0.375rem;
    }
</style>
""", unsafe_allow_html=True)

# Function to load lottie animations
def load_lottieurl(url):
    try:
        r = requests.get(url)
        if r.status_code != 200:
            return None
        return r.json()
    except:
        return None

# Initialize session state variables
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

# Load library data from file if it exists
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

# Save library data to file
def save_library():
    try:
        with open('library.json', 'w') as file:
            json.dump(st.session_state.library, file)
        return True
    except Exception as e:
        st.error(f"Error saving library: {e}")
        return False

# Add a book to the library
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
    time.sleep(0.5)  # Slight delay for animation effect

# Remove a book from the library
def remove_book(index):
    if 0 <= index < len(st.session_state.library):
        del st.session_state.library[index]
        save_library()
        st.session_state.book_removed = True
        return True
    return False

# Search for books in the library
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

# Calculate library statistics
def get_library_stats():
    total_books = len(st.session_state.library)
    read_books = sum(1 for book in st.session_state.library if book['read_status'])
    percent_read = (read_books / total_books * 100) if total_books > 0 else 0
    
    genres = {}
    authors = {}
    decades = {}
    
    for book in st.session_state.library:
        # Count genres
        if book['genre'] in genres:
            genres[book['genre']] += 1
        else:
            genres[book['genre']] = 1
        
        # Count authors
        if book['author'] in authors:
            authors[book['author']] += 1
        else:
            authors[book['author']] = 1
        
        # Count decades
        decade = (book['publication_year'] // 10) * 10
        if decade in decades:
            decades[decade] += 1
        else:
            decades[decade] = 1
    
    # Sort by count
    genres = dict(sorted(genres.items(), key=lambda x: x[1], reverse=True))
    authors = dict(sorted(authors.items(), key=lambda x: x[1], reverse=True))
    decades = dict(sorted(decades.items(), key=lambda x: x[0]))
    
    return {
        'total_books': total_books,
        'read_books': read_books,
        'percent_read': percent_read,
        'genres': genres,
        'authors': authors,
        'decades': decades
    }

# Function to create visualizations
def create_visualizations(stats):
    # Read vs Unread pie chart
    if stats['total_books'] > 0:
        fig_read_status = go.Figure(data=[go.Pie(
            labels=['Read', 'Unread'],
            values=[stats['read_books'], stats['total_books'] - stats['read_books']],
            hole=.4,
            marker_colors=['#34D399', '#FBBF24']
        )])
        fig_read_status.update_layout(
            title_text="Read vs Unread Books",
            showlegend=True,
            height=400
        )
        st.plotly_chart(fig_read_status, use_container_width=True)
    
    # Genres bar chart
    if stats['genres']:
        genres_df = pd.DataFrame({
            'Genre': list(stats['genres'].keys()),
            'Count': list(stats['genres'].values())
        })
        fig_genres = px.bar(
            genres_df, 
            x='Genre', 
            y='Count',
            color='Count',
            color_continuous_scale=px.colors.sequential.Viridis
        )
        fig_genres.update_layout(
            title_text="Books by Genre",
            xaxis_title="Genre",
            yaxis_title="Number of Books",
            height=400
        )
        st.plotly_chart(fig_genres, use_container_width=True)
    
    # Decades line chart
    if stats['decades']:
        decades_df = pd.DataFrame({
            'Decade': [f"{decade}s" for decade in stats['decades'].keys()],
            'Count': list(stats['decades'].values())
        })
        fig_decades = px.line(
            decades_df, 
            x='Decade', 
            y='Count',
            markers=True,
            line_shape="spline"
        )
        fig_decades.update_layout(
            title_text="Books by Publication Decade",
            xaxis_title="Decade",
            yaxis_title="Number of Books",
            height=400
        )
        st.plotly_chart(fig_decades, use_container_width=True)

# Load library data on app start
load_library()

# Sidebar navigation
st.sidebar.markdown("<h1 style='text-align: center;'>📚 Navigation</h1>", unsafe_allow_html=True)

# Display lottie animation in sidebar
lottie_book = load_lottieurl("https://assets9.lottiefiles.com/temp/lf20_aKAfIn.json")
if lottie_book:
    with st.sidebar:
        st_lottie(lottie_book, height=200, key="book_animation")

# Navigation options
nav_options = st.sidebar.radio(
    "Choose an option:",
    ["View Library", "Add Book", "Search Books", "Library Statistics"]
)

# Change current view based on navigation
if nav_options == "View Library":
    st.session_state.current_view = "library"
elif nav_options == "Add Book":
    st.session_state.current_view = "add"
elif nav_options == "Search Books":
    st.session_state.current_view = "search"
elif nav_options == "Library Statistics":
    st.session_state.current_view = "stats"


# Application header
st.markdown("<h1 class='main-header'>📚 Personal Library Manager</h1>", unsafe_allow_html=True)

# Handle views based on current selection
if st.session_state.current_view == "add":
    st.markdown("<h2 class='sub-header'>📝 Add a New Book</h2>", unsafe_allow_html=True)
    
    # Input form for adding books
    with st.form(key='add_book_form'):
        col1, col2 = st.columns(2)
        
        with col1:
            title = st.text_input("Book Title", max_chars=100)
            author = st.text_input("Author", max_chars=100)
            publication_year = st.number_input("Publication Year", min_value=1000, max_value=datetime.now().year, step=1, value=2023)
        
        with col2:
            genre = st.selectbox("Genre", [
                "Fiction", "Non-Fiction", "Science Fiction", "Fantasy", 
                "Mystery", "Romance", "Thriller", "Biography", 
                "History", "Self-Help", "Poetry", "Science", 
                "Philosophy", "Religion", "Art", "Other"
            ])
            read_status = st.radio("Read Status", ["Read", "Unread"], horizontal=True)
            read_bool = read_status == "Read"
        
        submit_button = st.form_submit_button(label="Add Book")
        
        if submit_button and title and author:
            add_book(title, author, publication_year, genre, read_bool)
    
    # Display success message if book was added
    if st.session_state.book_added:
        st.markdown("<div class='success-message'>Book added successfully!</div>", unsafe_allow_html=True)
        st.balloons()  # Show celebration balloons
        st.session_state.book_added = False

elif st.session_state.current_view == "library":
    st.markdown("<h2 class='sub-header'>📖 Your Library</h2>", unsafe_allow_html=True)
    
    if not st.session_state.library:
        st.markdown("<div class='warning-message'>Your library is empty. Add some books to get started!</div>", unsafe_allow_html=True)
    else:
        # Display the books in the library as cards
        for idx, book in enumerate(st.session_state.library):
            col1, col2 = st.columns([3, 1])
            with col1:
                st.markdown(f"**{book['title']}**")
                st.markdown(f"By {book['author']}")
                st.markdown(f"Genre: {book['genre']}")
                st.markdown(f"Published: {book['publication_year']}")
                st.markdown(f"Added: {book['added_date']}")
                badge = "read-badge" if book['read_status'] else "unread-badge"
                st.markdown(f"<span class='{badge}'>Status: {'Read' if book['read_status'] else 'Unread'}</span>", unsafe_allow_html=True)

            with col2:
                remove_button = st.button(f"Remove Book", key=f"remove_{idx}", use_container_width=True)
                if remove_button:
                    if remove_book(idx):
                        st.session_state.book_removed = True
                        st.session_state.library.pop(idx)

        if st.session_state.book_removed:
            st.session_state.book_removed = False
            st.markdown("<div class='success-message'>Book removed successfully!</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "search":
    st.markdown("<h2 class='sub-header'>🔍 Search Books</h2>", unsafe_allow_html=True)
    
    # Search form
    with st.form(key='search_form'):
        search_term = st.text_input("Search Term", max_chars=100)
        search_by = st.selectbox("Search By", ["Title", "Author", "Genre"])
        submit_button = st.form_submit_button(label="Search")
        
        if submit_button and search_term:
            search_books(search_term, search_by)

    # Display search results
    if st.session_state.search_results:
        for idx, book in enumerate(st.session_state.search_results):
            st.markdown(f"**{book['title']}** by {book['author']} ({book['publication_year']})")
            st.markdown(f"Genre: {book['genre']}")
            st.markdown(f"Status: {'Read' if book['read_status'] else 'Unread'}")
            st.markdown(f"Added on: {book['added_date']}")
    elif st.session_state.search_results == []:
        st.markdown("<div class='warning-message'>No results found.</div>", unsafe_allow_html=True)

elif st.session_state.current_view == "stats":
    st.markdown("<h2 class='sub-header'>📊 Library Statistics</h2>", unsafe_allow_html=True)
    
    # Generate library stats and visualizations
    stats = get_library_stats()
    create_visualizations(stats)
