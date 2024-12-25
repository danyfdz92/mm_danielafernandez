import http.server
import socketserver
import os
import logging

# Port to serve the documentation
PORT: int = 8000

# Path to the docs folder relative to the script
DIRECTORY: str = os.path.join(os.getcwd(), "mm_data_production/docs")

# Change the working directory to the docs folder
os.chdir(DIRECTORY)


class Handler(http.server.SimpleHTTPRequestHandler):
    """Custom HTTP request handler for serving documentation."""
    pass


def serve_docs(port: int, directory: str) -> None:
    """
    Serve the documentation using a simple HTTP server.

    :param port: The port on which to run the server.
    :param directory: The directory containing the documentation to serve.
    """
    os.chdir(directory)
    with socketserver.TCPServer(("", port), Handler) as httpd:
        logging.info(
            f"Serving documentation at http://localhost:{port}/mm_data_production.html"
        )
        httpd.serve_forever()


if __name__ == "__main__":
    serve_docs(PORT, DIRECTORY)