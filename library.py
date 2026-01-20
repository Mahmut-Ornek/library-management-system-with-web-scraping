from datetime import datetime, timedelta
import hashlib
import requests
from bs4 import BeautifulSoup as bs
import concurrent.futures


class Book:
    def __init__(self, isbn, title, author, genre, year_published): #Initializes the book attributes.
        self.isbn = isbn
        self.title = title
        self.author = author
        self.genre = genre
        self.year_published = year_published
        self.availability = True
    
    def set_availability(self, availability : bool): #Sets the availability of book.
        self.availability = availability

    def get_availability(self): #Returns the availability of book.
        return self.availability

    def __str__(self):
        return f"{self.title} by {self.author}.\nGenre: {self.genre} \nYear: {self.year_published} \nISBN: {self.isbn}"
    

class Patron:
    def __init__(self, patron_id, name, phone_number, password): #Initializes the patron attributes.
        self.patron_id = patron_id
        self.name = name
        self.phone_number = phone_number
        #Hash the password using SHA-256 and store its hexadecimal string representation.
        self.password = hashlib.sha256(password.encode()).hexdigest() 
        self.books_borrowed = []

    def borrow_book(self, book): #Adds a book to the patron's list of borrowed books.
        if book.get_availability():
            self.books_borrowed.append(book)
            book.set_availability(False)
        else:
            print("Book is not available")

    def return_book(self, book): #Removes a book from the patron's list of borrowed books.
        if book in self.books_borrowed:
            self.books_borrowed.remove(book)
            book.set_availability(True)
        else: 
            print("Book is not borrowed!")

    def get_books_borrowed(self): #Returns the list of books borrowed by the patron.
        return self.books_borrowed

    def __str__(self):
        borrowed = [book.title for book in self.books_borrowed]
        return f"Name: {self.name}\nID: {self.patron_id}\nPhone Number: {self.phone_number}\nBorrowed: {borrowed if borrowed else 'None'}"


class Loan:
    def __init__(self, loan_id, book, patron, loan_date, due_date): #Initializes the loan attributes.
        self.loan_id = loan_id
        self.book = book
        self.patron = patron
        self.loan_date = loan_date
        self.due_date = due_date

    def get_details(self): # Returns a dictionary of loan details.
        return {"loan_id": self.loan_id, "book": self.book.title, "patron": self.patron.name, "loan_date": self.loan_date, "due_date": self.due_date}

    def __str__(self):
        return f"Loan ID {self.loan_id}: {self.book.title} to {self.patron.name}\nDue Date: {self.due_date}"


class Library:
    def __init__(self, name): #Initializes the library attributes.
        self.name = name
        self.books = []
        self.patrons = []
        self.loans = []
        self.catalog = Catalog()
        self.loan_counter = 0 # for adjusting loan id

    def add_book(self, book): #Adds a book to the library and the catalog.
        self.books.append(book)
        self.catalog.add_book(book)

    def add_patron(self, patron): #Adds a patron to the library and the catalog.
        self.patrons.append(patron)
        self.catalog.add_patron(patron)
    
    def loan_book(self, book, patron): #Creates a new loan and updates the catalog.
        if book.get_availability():
            # Increase the loan counter to generate a new unique loan ID
            self.loan_counter += 1
            
            # Record the current date as the loan date
            loan_date = datetime.now()
            # Set the due date as 15 days from the loan date
            due_date = loan_date + timedelta(days=15)
            loan = Loan(str(self.loan_counter), book, patron, loan_date, due_date)
            
            self.loans.append(loan)
            self.catalog.add_loan(loan)
            patron.borrow_book(book)
        else:
            print("Book is NOT available for loan.")

    def return_book(self, book, patron): #Handles the return of a book and updates the catalog.
        for loan in self.loans:
            if loan.book == book and loan.patron == patron:
                self.loans.remove(loan)
                self.catalog.remove_loan(loan)
                patron.return_book(book)
                break # it breakes the loop when removes the book

    def search_book(self,title): #Searches for a book by title.
        for x in self.books: 
            if title.lower() in x.title.lower():
                return x
    
    def search_patron(self, name): #Searches for a patron by name.
        for y in self.patrons:
            if name.lower() in y.name.lower():
                return y

    def __str__(self):
        return f"Library: {self.name}\n{self.catalog}"


class Catalog:
    #Initializes the catalog attributes.
    def __init__(self):
        self.loans = {}
        self.books = {}
        self.patrons = {}

    def add_book(self, book):
        self.books[book.isbn] = book

    def add_patron(self, patron):
        self.patrons[patron.patron_id] = patron

    def add_loan(self, loan):
        self.loans[loan.loan_id] = loan

    def remove_book(self, book):
        self.books.pop(book.isbn, None)

    def remove_patron(self, patron):
        self.patrons.pop(patron.patron_id, None)

    def remove_loan(self, loan):
        self.loans.pop(loan.loan_id, None)

    def get_book(self, isbn):
        return self.books.get(isbn)

    def get_patron(self, patron_id):
        return self.patrons.get(patron_id)

    def get_loan(self, loan_id):
        return self.loans.get(loan_id)

    def __str__(self):
        return f"Catalog:\n->{len(self.books)} books\n->{len(self.patrons)} patrons\n->{len(self.loans)} loans"
        

class WebScraper:
     
    def __init__(self, url): #Initializes the web scraper with a URL.
        self.url = url
        self.books = []
        self.session = requests.Session()
        self.session.headers.update({"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"})
        
    
    def fetch_books(self):
        #Scrapes the web for book data using the requests library and BeautifulSoup . 

        #It parses the HTML to extract book details and returns a list of Book objects.
        try:
            r = self.session.get(self.url, timeout=20)
            r.raise_for_status()
        except requests.RequestException as e:
            print(f"Failed to fetch main page {self.url}: {e}")
            return []
        
        soup = bs(r.text, "html.parser")    
        book_elements = soup.find_all("span", class_="bookcover")
        self.books = self.parse_book_elements(book_elements[:20]) #20 books at most.
        
        return self.books

    def parse_book_elements(self, elements): #Helper method to parse HTML elements and create Book objects.
        books = []
        base_url = "https://openlibrary.org"
        
        def fetch_book(element):
            # Visit each book page and extract details
            a = element.find("a", href=True)

            #return None if an elements link is missing
            if not a:
                return None

            book_url = base_url + a["href"]

            try:
                r2 = self.session.get(book_url, timeout=20)
                r2.raise_for_status()
                soup2 = bs(r2.text, "html.parser")

                # Extract book info or set default if missing
                title_el = soup2.find("h1", itemprop = "name")
                title = title_el.text.strip() if title_el else "Unknown Title"

                author_el = soup2.find("a", itemprop = "author")
                author = author_el.text.strip() if author_el else "Unknown Author"

                year_published_el = soup2.find("span", itemprop="datePublished")
                year_published = year_published_el.text.strip() if year_published_el else "Unknown Year"

                isbn_el = soup2.find("dd", itemprop = "isbn")
                if isbn_el:
                    isbn_text = isbn_el.text.strip()
                    isbn = isbn_text.split()[0].replace(",", "")  # take first one, remove comma if any
                else:
                    isbn = "Unknown ISBN"

                # Try to fetch the first genre if available.
                genre_label = soup2.find("span", class_="reviews__label", title="What are the genres of this book?")
                first_genre = None
                if genre_label:
                    genre_category = genre_label.find_parent("span", class_="review__category")
                    first_genre = genre_category.find("span", class_="reviews__value").text.strip() if genre_category else "Unknown Genre"
                
                # Add book only if ISBN is found. 
                # ISBN is more important for returning and borrowing a book.
                if isbn != "Unknown ISBN":    
                    return Book(isbn, title, author, first_genre, year_published)
                
            except requests.RequestException as e:
                print(f"Network error for {book_url}: {e}")

            except Exception as e:
                print(f"Parsing error for {book_url}: {e}")
            return None

        # Run fetches in parallel
        #Instead of fetching book pages one by one (sequential), it allows up to 10 fetches to happen at the same time.
        with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor: 
            results = list(executor.map(fetch_book, elements))

        # Keep only non-None results
        books = [b for b in results if b is not None]
        return books
    
    def __str__(self):
        #Print books if available
        if not self.books:
            print("No books to display.")
        for book in self.books:
            print(book)
            print("-"*50)


class Login:
    #Constructor to initialize the login system with the catalog reference.
    def __init__(self, catalog):
        self.catalog = catalog
        self.current_patron = None #Tracks the currently logged-in user.

    def login(self, patron_id, password):
        #Verify patron credentials using SHA-256 hashed password.
        patron = self.catalog.get_patron(patron_id)
        if patron and patron.password == hashlib.sha256(password.encode()).hexdigest():
            self.current_patron = patron
            return patron
        return None

    def logout(self):
        #Clear the current login session.
        self.current_patron = None

    def is_logged_in(self):
        #Return True if a patron is logged in.
        return self.current_patron is not None

    def get_current_patron(self):
        #Return the currently logged-in patron object.
        return self.current_patron

    def __str__(self):
        if self.current_patron:
            return f"{self.current_patron.name} logged in."
        return "No one logged"



if __name__ == "__main__":
    #Initialize scraper and fetch trending books
    scraper = WebScraper("https://openlibrary.org/trending/forever")
    books = scraper.fetch_books()

    # Create a library and add fetched books
    library = Library("The Book Portal")
    for b in books:
        library.add_book(b)

    # Create a patron and register them in the library
    patron1 = Patron("P001", "Mahmut", "544-9999", "pswrd12345")
    library.add_patron(patron1)

    # Simulate a login system
    login = Login(library.catalog)
    login.login("P001", "pswrd12345")
    print(login)

    if books:
        print("\nFetched Books:\n")
        scraper.__str__() #Display scraped books
        print("*" * 50)

        #Loop for interactive menu
        while True:
            print("\n=== Library Menu ===")
            print("1. View all books")
            print("2. Borrow a book")
            print("3. Return a book")
            print("4. View my borrowed books")
            print("5. Exit")

            choice = input("Enter your choice (1-5): ").strip()

            if choice == "1":
                # Show all books and availability
                print("\nAvailable Books:")
                for b in books:
                    status = "Available" if b.get_availability() else "Not Available"
                    print(f"- {b.title} (ISBN: {b.isbn}) [{status}]")

            elif choice == "2":
                #Borrow book by ISBN
                select = input("\nEnter book ISBN for borrowing: ").strip()
                book_to_borrow = next((b for b in books if b.isbn == select), None)

                if book_to_borrow:
                    library.loan_book(book_to_borrow, patron1)
                    print("\nAfter borrowing:")
                    print(patron1)
                else:
                    print("Book not found.")

            elif choice == "3":
                #Return a borrowed book.
                borrowed_books = patron1.get_books_borrowed()

                if not borrowed_books:
                    print("You have no borrowed books.")
                else:
                    print("\nYour borrowed books:")
                    for b in borrowed_books:
                        print(f"- {b.title} (ISBN: {b.isbn})")

                    select_return = input("\nEnter book ISBN to return: ").strip()
                    book_to_return = next((b for b in borrowed_books if b.isbn == select_return), None)

                    if book_to_return:
                        library.return_book(book_to_return, patron1)
                        print("\nAfter returning:")
                        print(patron1)
                    else:
                        print("Book not found in your borrowed list.")

            elif choice == "4":
                # Show all currently borrowed books.
                print("\nCurrently borrowed books:")
                borrowed = patron1.get_books_borrowed()

                if borrowed:
                    for b in borrowed:
                        print(f"- {b.title} (ISBN: {b.isbn})")
                else:
                    print("None")

            elif choice == "5":
                #Exit menu
                print("Goodbye!")
                break

            else:
                print("Invalid choice. Please enter 1–5.")

    else:
        print("No books were fetched")

    # Final library status summary
    print("\nLibrary status:")
    print(library)

