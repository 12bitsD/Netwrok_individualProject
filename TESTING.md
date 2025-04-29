# HTTP Server Testing Guide

This document explains how to test the various features of the multi-threaded HTTP server.

## Starting the Server

```bash
# Method 1: Using Python directly
python server.py [port]

# Method 2: Using the start script
./start_server.sh [port]
```

Default port is 8080 if not specified.

## Basic Tests

1. **Access the homepage:**
   Open a browser and navigate to:
   ```
   http://127.0.0.1:8080/
   ```
   You should see the index.html file.

2. **Access a text file:**
   ```
   http://127.0.0.1:8080/test.txt
   ```
   The server should return the text file content.

## Status Code Tests

1. **404 Not Found:**
   Request a non-existent file:
   ```
   http://127.0.0.1:8080/nonexistent.html
   ```
   You should receive a 404 error page.

2. **304 Not Modified:**
   This can be tested with curl using the If-Modified-Since header:
   ```bash
   # First, get the Last-Modified value
   curl -I http://127.0.0.1:8080/test.txt
   
   # Then use it in the If-Modified-Since header
   curl -I -H "If-Modified-Since: VALUE_FROM_PREVIOUS_REQUEST" http://127.0.0.1:8080/test.txt
   ```
   You should receive a 304 status code.

3. **400 Bad Request:**
   Send an invalid HTTP request:
   ```bash
   echo -e "INVALID REQUEST\r\n\r\n" | nc 127.0.0.1 8080
   ```

4. **HEAD Method:**
   Test the HEAD method:
   ```bash
   curl -I http://127.0.0.1:8080/test.txt
   ```
   You should receive headers but no body content.

## Connection Tests

1. **Keep-Alive Connection:**
   Test with curl:
   ```bash
   curl -v -H "Connection: keep-alive" http://127.0.0.1:8080/test.txt
   ```
   Check that the connection is kept alive.

2. **Close Connection:**
   Test with curl:
   ```bash
   curl -v -H "Connection: close" http://127.0.0.1:8080/test.txt
   ```
   Check that the connection is closed after the response.

## Multi-Threading Test

Send multiple requests simultaneously to verify that the server handles them in separate threads:

```bash
# Run several requests in parallel
for i in {1..10}; do
    curl http://127.0.0.1:8080/test.txt &
done
```

Check the server logs to see that requests were processed concurrently.

## Log Verification

Check the server.log file to verify that all requests are properly logged with:
- Client IP
- Timestamp
- Requested file path
- Response status code 