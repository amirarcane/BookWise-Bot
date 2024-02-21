from elasticsearch import Elasticsearch


class ElasticsearchManager:
    """Manages interactions with Elasticsearch indices for books and the shopping cart."""

    BOOKS_INDEX_NAME = "books"
    CART_INDEX_NAME = "cart"

    def __init__(self, dimension=384):
        """
        Initialize an ElasticsearchManager object.

        :param dimension: The dimension of the dense vectors.
        :type dimension: int
        """
        self.es = Elasticsearch(hosts="https://localhost:9200", basic_auth=["elastic", "vozLjbIOWbriPTQnU8Mg"],
                                verify_certs=False)
        self.dimension = dimension
        # Create indices
        self._create_index(self.BOOKS_INDEX_NAME, {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "author": {"type": "text"},
                    "genre": {"type": "text"},
                    "vector": {"type": "dense_vector", "dims": self.dimension}
                }
            }
        })
        self._create_index(self.CART_INDEX_NAME, {
            "mappings": {
                "properties": {
                    "title": {"type": "text"},
                    "vector": {"type": "dense_vector", "dims": self.dimension}
                }
            }
        })

    def _create_index(self, index_name, mapping):
        """
        Create an Elasticsearch index with the given name and mapping.

        :param index_name: The name of the index to create.
        :type index_name: str
        :param mapping: The mapping for the index.
        :type mapping: dict
        """
        self.es.indices.create(index=index_name, body=mapping, ignore=400)

    def index(self, index_name, document):
        """
        Index a document into the specified Elasticsearch index.

        :param index_name: The name of the index to index the document into.
        :type index_name: str
        :param document: The document to be indexed.
        :type document: dict
        """
        self.es.index(index=index_name, body=document)

    def search(self, index_name, query):
        """
        Search documents in the specified Elasticsearch index based on a query.

        :param index_name: The name of the index to search.
        :type index_name: str
        :param query: The query string.
        :type query: str

        :return: List of documents matching the query.
        :rtype: list
        """
        response = self.es.search(index=index_name, query={"multi_match": {"query": query, "fields": ["title"]}})
        return [hit["_source"] for hit in response["hits"]["hits"]]

    def get_all(self, index_name):
        """
        Retrieve all documents from the specified Elasticsearch index.

        :param index_name: The name of the index.
        :type index_name: str

        :return: List of all documents in the index.
        :rtype: list
        """
        response = self.es.search(index=index_name, body={"query": {"match_all": {}}, "size": 50})
        return [doc["_source"] for doc in response["hits"]["hits"]]

    def delete(self, index_name, title):
        """
        Delete a document from the specified Elasticsearch index based on its title.

        :param index_name: The name of the index.
        :type index_name: str
        :param title: The title of the document to delete.
        :type title: str

        :return: Response indicating the status of the delete operation.
        :rtype: dict or str
        """
        query = {"query": {"match": {"title": title}}}
        search_resp = self.es.search(index=index_name, body=query, size=1)
        if search_resp['hits']['hits']:
            document_id = search_resp['hits']['hits'][0]['_id']
            delete_resp = self.es.delete(index=index_name, id=document_id)
            return delete_resp
        else:
            return "Document not found."

    def clear(self, index_name):
        """
        Clear all documents from the specified Elasticsearch index.

        :param index_name: The name of the index.
        :type index_name: str
        """
        response = self.es.delete_by_query(
            index=index_name,
            body={
                "query": {
                    "match_all": {}
                }
            },
            # Add this to wait until the operation is complete before continuing
            wait_for_completion=True
        )

    def search_book(self, title, author, genre):
        """
        Enhanced search method that tries alternative search parameters if the initial search yields no results.
        It first attempts to find books matching the provided genre, title, or author. If no results are found, it
        then searches other fields for the provided keywords.

        :param title: The title of the book, or None.
        :type title: str
        :param author: The author of the book, or None.
        :type author: str
        :param genre: The genre of the book, or None.
        :type genre: str

        :return: List of documents matching the query, with fallback search in other fields if necessary.
        :rtype: list
        """

        # Normalize input to avoid "None" and None
        def normalize_input(input_value):
            if input_value in [None, "None", ""]:
                return None
            return input_value

        title = normalize_input(title)
        author = normalize_input(author)
        genre = normalize_input(genre)

        # Initial search query conditions
        query_conditions = []
        if title:
            query_conditions.append({"match": {"title": title}})
        if author:
            query_conditions.append({"match": {"author": author}})
        if genre:
            query_conditions.append({"match": {"genre": genre}})

        # Execute the initial search
        if query_conditions:
            query = {"bool": {"must": query_conditions}}
            response = self.es.search(index=self.BOOKS_INDEX_NAME, body={"query": query, "size": 50})
            if response["hits"]["hits"]:
                return [hit["_source"] for hit in response["hits"]["hits"]]

        # Fallback search if no results found in the initial query
        fallback_keywords = [kw for kw in [title, author, genre] if kw is not None]
        if fallback_keywords:
            fallback_query = {
                "multi_match": {
                    "query": " ".join(fallback_keywords),
                    "fields": ["title", "author", "genre"],
                    "type": "best_fields"
                }
            }
            response = self.es.search(index=self.BOOKS_INDEX_NAME, body={"query": fallback_query, "size": 50})
            return [hit["_source"] for hit in response["hits"]["hits"]]

        return []

    def search_vector(self, index_name, query_vector, size=5):
        """
        Perform a vector similarity search in the specified Elasticsearch index using a book object.

        This method takes a book object, utilizes its vector representation, and performs a vector
        similarity search in the specified Elasticsearch index to find similar books based on
        vector similarity scores.

        Parameters:
        - index_name (str): The name of the Elasticsearch index to search.
        - book (Book): The book object whose vector representation will be used for the similarity search.
        - size (int): The number of similar books to return. Defaults to 5.

        Returns:
        - list: A list of Elasticsearch hits representing documents that are similar to the given book,
                based on vector similarity. Each hit is a dictionary containing document details.
        """
        # Elasticsearch script_score query for computing similarity
        query = {
            "script_score": {
                "query": {"match_all": {}},
                "script": {
                    "source": "cosineSimilarity(params.query_vector, 'vector') + 1.0",
                    "params": {"query_vector": query_vector}
                }
            }
        }

        response = self.es.search(index=index_name, body={"query": query}, size=size)
        return response["hits"]["hits"]
