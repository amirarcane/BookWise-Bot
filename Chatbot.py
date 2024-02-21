import os
import re
import time
import openai

from dotenv import load_dotenv
from CartManager import CartManager
from ElasticsearchManager import ElasticsearchManager

# Load environment variables from .env file
load_dotenv()


class Chatbot:
    """A chatbot capable of handling user queries and managing a shopping cart."""

    def __init__(self):
        """
        Initialize a Chatbot object by reading the OpenAI API key from a YAML file.
        """
        self.es = ElasticsearchManager()
        self.cart_manager = CartManager()
        openai.api_key = os.getenv("OPENAI_API_KEY")

    def handle_query(self, messages, query):
        """
        Handle a user query.

        :param messages: List of messages exchanged in the conversation.
        :type messages: list
        :param query: The user's query.
        :type query: str

        :return: Updated list of messages, response, and shopping cart items.
        :rtype: tuple
        """
        query_lower = query.lower()
        messages, response = self.generate_response(messages, query_lower)
        action, title, author, genre, response = self.extract_action(response)

        if action == "Search":
            books = self.es.search_book(title=title, author=author, genre=genre)
            num_books = len(books)

            if num_books > 1:
                # Format the book details into a string, each on a new line
                books_details = "\n".join(
                    [f"{idx + 1}. Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}"
                     for idx, book in enumerate(books)])
                response += f"\nI found multiple books:\n{books_details}\n\nWhich one do you mean?"
            elif num_books == 1:
                book = books[0]  # Get the single book found
                response += f"\nI found the book: Title: {book['title']}, Author: {book['author']}, Genre: {book['genre']}. Would you like to add it to the cart?"
            else:
                response += "\nI couldn't find any books matching your criteria."

            # Ensure the response is part of the conversation history
            messages.append({"role": "assistant", "content": response})
        elif action == "Add_to_Cart":
            self.add_to_cart(title)
        elif action == "Remove_from_Cart":
            self.remove_from_cart(title)
        elif action == "Clear_Cart":
            self.remove_all()

        time.sleep(1)
        carts = self.cart_manager.get_cart()

        return messages, response, carts

    def add_to_cart(self, title):
        """
        Add an item to the shopping cart.

        :param title: The title of the item to add.
        :type title: str
        """
        search_results = self.cart_manager.search_cart(title)
        if search_results:
            return f"Item {title} already in our database."

        self.cart_manager.add(title)

    def remove_from_cart(self, title):
        """
        Remove an item from the shopping cart.

        :param title: The title of the item to remove.
        :type title: str
        """
        search_results = self.cart_manager.search_cart(title)
        if not search_results:
            return f"Item {title} not found in our database."

        self.cart_manager.remove(title)

    def remove_all(self):
        """Remove all items from the shopping cart."""
        self.cart_manager.clear()

    def generate_response(self, messages, user_query, temperature=0.7):
        """
        Generate a response to a user query.

        :param messages: List of messages exchanged in the conversation.
        :type messages: list
        :param user_query: The user's query.
        :type user_query: str
        :param temperature: Controls the randomness of the response.
        :type temperature: float

        :return: Updated list of messages and the generated response.
        :rtype: tuple
        """
        messages.append({"role": "user", "content": user_query})

        completion = openai.ChatCompletion.create(model="gpt-4",
                                                  messages=messages,
                                                  temperature=temperature)

        ai_response = completion.choices[0].message.content
        messages.append({"role": "assistant", "content": ai_response})

        return messages, ai_response

    def extract_action(self, text):
        """
        Extract action and book title from text.

        :param text: The text to extract information from.
        :type text: str

        :return: Action, book title, and updated text.
        :rtype: tuple
        """
        action = ""
        book_title = ""
        author = ""
        genre = ""
        pattern = r"\[ACTION: (.*?); BOOK_TITLE: (.*?); AUTHOR: (.*?); GENRE: (.*?)\]"
        matches = re.findall(pattern, text)

        if matches:
            for match in matches:
                action, book_title, author, genre = match
                text = text.replace(
                    "[ACTION: " + action + "; BOOK_TITLE: " + book_title + "; AUTHOR: " + author + "; GENRE: " + genre + "]",
                    "")

        return action, book_title, author, genre, text
