import streamlit as st
from BookManager import BookManager
from Chatbot import Chatbot

OPENAI_API_KEY = "YOUR_OPENAI_API_KEY"


def initialize_session_state():
    """
    Initialize session state variables if they don't exist.
    """
    if 'messages' not in st.session_state:
        st.session_state.messages = []
    if 'books' not in st.session_state:
        st.session_state.books = []


def app():
    """
    Main application function.
    """
    initialize_session_state()
    st.title("Welcome to BookWise Bot")
    placeholder = st.empty()

    placeholder.empty()
    st.sidebar.header("Shopping Cart")

    question = st.text_area("Ask me anything:")

    chatbot = Chatbot(openai_api_key=OPENAI_API_KEY)

    with open('prompt.txt', 'r') as file:
        # Read the contents of the file
        system_message = file.read()

    st.session_state.messages.append({"role": "system", "content": system_message})

    book_manager = BookManager()

    st.session_state.books_dict = book_manager.get_books()

    books = format_books_dict_to_string(st.session_state.books_dict)
    st.session_state.messages.append({"role": "system", "content": books})

    if st.button("Send"):
        st.session_state.messages, response, carts = chatbot.handle_query(st.session_state.messages, question)

        st.write(response)
        titles = [item['title'] for item in carts]
        for title in titles:
            st.sidebar.warning(title)


def format_books_dict_to_string(books):
    """
    Convert dictionary of books to a readable string format.

    :param books: Dictionary containing book information.
    :type books: list

    :return: Formatted string of book information.
    :rtype: str
    """
    message = "Here's the list of books available:\n"
    for book in books:
        message += f"* Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}\n"
    return message


if __name__ == "__main__":
    app()
