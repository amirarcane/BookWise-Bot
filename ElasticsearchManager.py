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
