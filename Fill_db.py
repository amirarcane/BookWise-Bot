"""
This script populates an Elasticsearch index with book data using the Book and BookManager classes.

The Book class represents a book entity with attributes such as title, author, and genre, and provides a method to convert the book entity to a dictionary suitable for indexing in Elasticsearch.

The BookManager class manages interactions with the Elasticsearch index for books, providing methods to index a book, retrieve all books, and search for books based on a query.

The script iterates through a list of titles, authors, and genres, creates Book instances for each book, and indexes them using the BookManager.

"""

from Book import Book
from BookManager import BookManager

# List of titles
titles = [
    "To Kill a Mockingbird",
    "1984",
    "The Great Gatsby",
    "Pride and Prejudice",
    "The Catcher in the Rye",
    "The Hobbit",
    "Moby-Dick",
    "The Lord of the Rings",
    "Harry Potter and the Sorcerer's Stone",
    "The Chronicles of Narnia",
    "Sapiens: A Brief History of Humankind",
    "Thinking, Fast and Slow",
    "The Immortal Life of Henrietta Lacks",
    "Deep Learning",
    "Machine Learning Yearning",
    "Pattern Recognition and Machine Learning",
    "Hands-On Machine Learning with Scikit-Learn, Keras, and TensorFlow",
    "Python Deep Learning",
    "Natural Language Processing with Python",
    "Reinforcement Learning: An Introduction"
]

# List of corresponding authors
authors = [
    "Harper Lee",
    "George Orwell",
    "F. Scott Fitzgerald",
    "Jane Austen",
    "J.D. Salinger",
    "J.R.R. Tolkien",
    "Herman Melville",
    "J.R.R. Tolkien",
    "J.K. Rowling",
    "C.S. Lewis",
    "Yuval Noah Harari",
    "Daniel Kahneman",
    "Rebecca Skloot",
    "Ian Goodfellow, Yoshua Bengio, and Aaron Courville",
    "Andrew Ng",
    "Christopher M. Bishop",
    "Aurélien Géron",
    "François Chollet",
    "Steven Bird, Ewan Klein, and Edward Loper",
    "Richard S. Sutton and Andrew G. Barto"
]

# List of genres
genres = [
    "Classic",
    "Classic",
    "Classic",
    "Classic",
    "Classic",
    "Fantasy",
    "Fiction",
    "Fantasy",
    "Fantasy",
    "Fantasy",
    "History",
    "Psychology",
    "Biography",
    "Science",
    "Computer Science",
    "Computer Science",
    "Computer Science",
    "Computer Science",
    "Computer Science",
    "Computer Science"
]

for i in range(len(titles)):
    title = titles[i]
    author = authors[i]
    genre = genres[i]

    # Create a book instance
    book = Book(title=title, author=author, genre=genre)

    # Create a book manager instance
    bookmanager = BookManager()

    # Index the book
    bookmanager.index_book(book)
