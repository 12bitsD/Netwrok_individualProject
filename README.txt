# Python Multi-threaded HTTP Server

A simple multi-threaded HTTP server implementation using Python sockets.

## Features

- Multi-threaded connection handling
- Support for GET and HEAD methods
- HTTP status codes: 200, 304, 400, 403, 404, 415
- Persistent connections (keep-alive)
- Request logging

## Requirements

- Python 3.6+

## Running the Server

1. Navigate to the project directory:
   ```
   cd run
   ```

2. Start the server:
   ```
   python main.py [port]
   ```
   Where `[port]` is an optional port number (default: 8080)

3. Or use the start script:
   ```
   ./start_server.sh [port]
   ```

4. Test the server by visiting:
   ```
   http://127.0.0.1:8080
   ```

## File Structure

- `main.py`: Entry point for the application
- `server.py`: Core server implementation
- `http_parser.py`: HTTP request parsing
- `http_response.py`: HTTP response generation
- `logger.py`: Logging system
- `config.py`: Configuration constants
- `www/`: Directory for web content (HTML, images, etc.)
- `server.log`: Log file for server requests

## Architecture

The server is designed with modular components:

1. `HTTPServer`: Manages connections and threads
2. `HTTPParser`: Parses HTTP requests
3. `HTTPResponse`: Generates HTTP responses
4. `Logger`: Handles request logging

## Example Usage

```
python main.py 8888
```

This starts the server on port 8888. 