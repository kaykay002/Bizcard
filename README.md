**BizCard OCR**
BizCard OCR is a Python-based application designed to extract text information from business card images using Optical Character Recognition (OCR) technology. It provides a convenient way to digitize and process business card data for further use.

**Features**
OCR Text Extraction: Extracts text information such as name, designation, company, email, website, address, and contact number from business card images.
Database Integration: Stores extracted business card data into a PostgreSQL database for easy retrieval and management.
User Interface: Provides a user-friendly interface built using Streamlit, allowing users to upload images, view extracted data, modify details, and store data in the database.

**Here are the technologies used in the BizCard OCR project:**
Python: The core programming language used for developing the application logic and backend functionality.
OpenCV: OpenCV (Open Source Computer Vision Library) is used for image processing tasks such as image loading, preprocessing, and extraction of regions of interest.
Tesseract OCR: Tesseract OCR is an open-source OCR engine widely used for extracting text from images. In this project, Tesseract OCR is utilized for text extraction from business card images.
Streamlit: Streamlit is a Python library used for building interactive web applications. It is employed in this project to create a user-friendly interface for uploading images, viewing extracted data, and interacting with the application.
Pandas: Pandas is a powerful data manipulation library in Python used for data analysis and manipulation. It is used here for storing and manipulating the extracted business card data.
Psycopg2: Psycopg2 is a PostgreSQL adapter for Python. It is used for establishing connections to the PostgreSQL database and executing SQL queries to store and retrieve data.
PostgreSQL: PostgreSQL is a powerful, open-source relational database management system used for storing the extracted business card data.

**Usage**
Upload Business Card Image: Use the provided UI to upload a business card image.
Extract Data: Click on the "Extract Data" button to extract text information from the uploaded image.
View Extracted Data: View the extracted data in a tabular format on the UI.
Modify Details: Select a name from the list and modify the details as needed. Click on the "Modify" button to update the database with the modified information.
Store Data: Click on the "Save to the Database" button to store the extracted business card data into the PostgreSQL database.

