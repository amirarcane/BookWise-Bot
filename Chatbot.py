import re
import time
import openai
from CartManager import CartManager


class Chatbot:
    """A chatbot capable of handling user queries and managing a shopping cart."""

    def __init__(self, openai_api_key):
        """
        Initialize a Chatbot object.

        :param openai_api_key: The API key for OpenAI services.
        :type openai_api_key: str
        """
        self.cart_manager = CartManager()
        openai.api_key = openai_api_key

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
        action, title, response = self.extract_action(response)

        if action == "Add_to_Cart":
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

        completion = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            temperature=temperature
        )

        ai_response = completion.choices[0].message['content']
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
        pattern = r"\[ACTION: (.*?); BOOK_TITLE: (.*?)\]"
        matches = re.findall(pattern, text)

        if matches:
            for match in matches:
                action, book_title = match
                text = text.replace("[ACTION: " + action + "; BOOK_TITLE: " + book_title + "]", "")

        return action, book_title, text
