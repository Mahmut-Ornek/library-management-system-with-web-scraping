# Library Management System with Web Scraping

This project is a Python-based library management system that integrates **web scraping** to dynamically populate the library catalog with real book data.

Book information is scraped from **OpenLibrary** and then managed through a simple **command-line interface (CLI)** that supports borrowing, returning, and tracking books.

---

## 🚀 Features

- Web scraping using **Requests** and **BeautifulSoup**
- Concurrent scraping with **ThreadPoolExecutor**
- Object-Oriented Design (OOP)
- Book borrowing and returning system
- Patron login with **SHA-256 password hashing**
- Loan tracking with due dates
- Interactive CLI menu

---

## 🕸️ Web Scraping

- Source: https://openlibrary.org/trending/forever
- Scraped data:
  - Book title
  - Author
  - ISBN
  - Genre
  - Publication year
- Each book page is fetched individually
- Scraping is performed concurrently for better performance

---

## 🧱 System Design

Main components of the system:

- **Book**: Represents a book entity and its availability
- **Patron**: Represents a library user
- **Loan**: Tracks borrowing details and due dates
- **Library**: Manages books, patrons, and loans
- **Catalog**: Central registry for books, patrons, and loans
- **WebScraper**: Fetches book data from OpenLibrary
- **Login**: Handles patron authentication

---

## ▶️ How to Run

1. Install dependencies:
   ```bash
   pip install requests beautifulsoup4 
   ```
2. Run the program:
    ```bash
   python library.py
   ```
3. Follow the interactive menu in the terminal.

---

## 🧪 Example Workflow

- Fetch trending books from OpenLibrary
- Add scraped books to the library catalog
- Login as a patron
- Borrow and return books
- Track borrowed books and availability

---

## 📌 Notes

- This project is intended for educational purposes.
- The focus is on combining web scraping with basic system design concepts.
- No database is used; all data is stored in memory during runtime.

---

## 🛠 Technologies Used

- Python
- Requests
- BeautifulSoup
- Concurrent Futures
- Hashlib