from ElasticsearchManager import ElasticsearchManager
from Vectorizer import Vectorizer


class CartManager:
    """Manages interactions with the Elasticsearch index for the shopping cart."""

    def __init__(self):
        """
        Initialize a CartManager object.
        """
        self.es_manager = ElasticsearchManager()
        self.vectorize = Vectorizer()
        self.index = "cart"

    def add(self, title):
        """
        Add a book to the shopping cart.

        :param title: The title of the book to add.
        :type title: str
        """
        document = {
            "title": title,
            "vector": self.vectorize.vectorize(title).tolist()
        }
        self.es_manager.index(self.index, document)

    def remove(self, title):
        """
        Remove a book from the shopping cart.

        :param title: The title of the book to remove.
        :type title: str
        """
        self.es_manager.delete(index_name=self.index, title=title)

    def get_cart(self):
        """
        Retrieve all items from the shopping cart.

        :return: A list of items in the shopping cart.
        :rtype: list
        """
        return self.es_manager.get_all(index_name=self.index)

    def search_cart(self, query):
        """
        Search for items in the shopping cart based on a query.

        :param query: The query string to search for.
        :type query: str

        :return: A list of items matching the query in the shopping cart.
        :rtype: list
        """
        return self.es_manager.search(index_name=self.index, query=query)

    def clear(self):
        """
        Clear all items from the shopping cart.
        """
        return self.es_manager.clear(index_name=self.index)
