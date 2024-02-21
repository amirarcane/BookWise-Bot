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

    def recommend_books(self, book):
        """
        Recommend books similar to a given book based on vector similarity.

        This method uses the vector representation of the provided book object and employs
        Elasticsearch's script_score query to compute similarity scores with other books in
        the database. It returns a list of books that are most similar to the given book,
        based on their vector representations.

        Parameters:
        - book (Book): The book object to find similar books to. This object must have a 'vector'
                       attribute that represents its combined title, author, and genre features.

        Returns:
        - list: A list of dictionaries, where each dictionary represents a book similar to the given book.
                Each dictionary contains keys like 'title', 'author', 'genre', and 'vector', detailing
                the properties of the recommended books.
        """

        return self.es_manager.search_vector(index_name=self.index, query_vector=book.vector)
