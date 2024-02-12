from ElasticsearchManager import ElasticsearchManager


class BookManager:
    """Manages interactions with the Elasticsearch index for books."""

    def __init__(self):
        """
        Initialize a BookManager object.
        """
        self.es_manager = ElasticsearchManager()
        self.index = "books"

    def index_book(self, book):
        """
        Index a book in Elasticsearch.

        :param book: The book object to index.
        :type book: Book
        """
        book_dict = book.to_dict()
        self.es_manager.index(self.index, book_dict)

    def get_books(self):
        """
        Retrieve all books from Elasticsearch.

        :return: A list of books.
        :rtype: list
        """
        return self.es_manager.get_all(index_name=self.index)

    def search_books(self, query):
        """
        Search for books in Elasticsearch based on a query.

        :param query: The query string to search for.
        :type query: str

        :return: A list of books matching the query.
        :rtype: list
        """
        return self.es_manager.search(index_name=self.index, query=query)
