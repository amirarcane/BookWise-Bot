from Vectorizer import Vectorizer


class Book:
    """Represents a book entity with title, author, genre, and a vectorized representation."""

    def __init__(self, title, author, genre):
        """
        Initialize a Book object.

        :param title: The title of the book.
        :type title: str
        :param author: The author of the book.
        :type author: str
        :param genre: The genre of the book.
        :type genre: str
        """
        self.title = title
        self.author = author
        self.genre = genre
        self.vector = Vectorizer()

    def to_dict(self):
        """
        Convert the book entity to a dictionary suitable for indexing in Elasticsearch.

        :return: A dictionary representing the book entity.
        :rtype: dict
        """
        return {
            "title": self.title,
            "author": self.author,
            "genre": self.genre,
            "vector": self.vector.vectorize(self.title).tolist()
        }
