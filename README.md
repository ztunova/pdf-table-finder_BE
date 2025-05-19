# PDF Table Finder Backend

This FastAPI application serves as the backend for a PDF table detection and extraction tool. It exposes a set of endpoints that allow users to:

- Upload PDF files
- Automatically detect tables within the uploaded documents using selected detection method. Available methods include PyMuPDF library or YOLO model.
- Extract tabular data from specified regions using selected extraction method. Available methods include PyMuPDF library, custom OCR algorithm or extraction using ChatGPT API.

In addition, the API supports exporting the extracted data either as:
- An Excel (.xlsx) file
- A ZIP archive containing individual CSV files (one per extracted table)

**Note**: All table region coordinates are specified as percentages, relative to the width and height of the page.

## Demo
Deployed API is available at following URL: https://api.pdf-table-extractor.dyn.cloud.e-infra.cz/ <br>
User interface for the API can be found at following URLs: 
- repository: https://github.com/ztunova/pdf-table-finder_FE
- deployed application: https://pdf-table-extractor.dyn.cloud.e-infra.cz/

## Technologies
- Python 3.11
- FastAPI
- PyMuPDF
- YOLO for table detection (https://huggingface.co/foduucom/table-detection-and-extraction)
- ChatGPT API integration

## Setup Instructions

### 1. Prerequisites
- Python 3.11


### 2. Configuration
The application integrates OpenAI's ChatGPT API and requires a valid API key to be specified in the `.env` file.
- Create a `.env` file based on the provided `.env.sample`
- Include your ChatGPT API key

Ensure that the correct environment paths are set up in `/src/constants.py`.

### 3. Installation and Running the Application
1) Clone the repository with `git clone`
2) Use `cd` to navigate to the project root directory
3) Create a virtual environment `python3 -m venv .venv`
4) Activate the virtual environment `source venv/bin/activate`
3) Install dependencies using `pip install -r requirements.txt`
4) Run project locally with `make run`


### 4. Build Docker Image
The project includes a Dockerfile for containerized deployment. <br>
To build the Docker image, navigate to the project root directory and use command `docker build -t pdf-table-extractor-be .` <br>
Instructions to deploy to CERIT Kubernetes cluster together with configuration files can be found in following repository: https://github.com/ztunova/pdf-table-finder_kubernetes-deployment

## Project Structure
```
/
├── src/                  # Main application code
│   ├── ...               # API endpoint definitions and utility functions
|   ├── custom_types/     # Type definitions
|   ├── exceptions/       # Custom exception classes
|   ├── pdf_processing/   # Classes for PDF detection and extraction
|   ├── service/          # Service layer components
├── Dockerfile            # Container definition
├── Makefile              # Build and run commands
├── .env.sample           # Template for environment variables
└── ...
```

