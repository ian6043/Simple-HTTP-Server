Description:
A very simple http server that serves as a method of learnning about HTTP GET and POST requests, sockets, curl, and Cookies
The code does not use http module as would negate the purpose of getting a deeper understanding of http

There is a sample.sh file that is used to test the server using curl.

Usage: 
    chmod +x sample.sh
    ./sample.sh

High Level Specifications
Server functionality:
    ● User Authentication:
        ○ Users can log in with a username and password.
        ○ Passwords are stored as SHA-256 salted-hashed values in an “accounts.json” file.
        ○ Successful logins are authenticated by hashing the plaintext password with the salt stored in “accounts.json”.
        ○ User sessions are tracked using a cookie with a timeout.
        ○ Multiple users can be logged in at the same time.
    ● File Download:
        ○ Authenticated users can view the contents of files from a specified directory.
        ○ File access is restricted to the authenticated users directory only.
        ○ Unauthorized access to files is denied.
    ● Sessions:
        ○ User sessions are managed using randomly generated session IDs stored as a
        cookie.
        ○ Sessions expire after a configurable timeout period.

Usage:
    python3 server.py [IP] [PORT] [ACCOUNTS_FILE] [SESSION_TIMEOUT] [ROOT_DIRECTORY]
    Example: python3 server.py 127.0.0.1 8080 accounts.json 5 accounts/

    IP: The IP address on which the server will bind to.
    PORT: The port on which the server will listen for incoming connections.
    ACCOUNTS_FILE: A JSON file containing user accounts and their hashed passwords along with the corresponding salt.
    SESSION_TIMEOUT: The session timeout duration (in seconds).
    ROOT_DIRECTORY: The root directory containing user directories.

Server Specifications:
    HTTP and Requests:
    ● The server can use HTTP version 1.0, but the server should not care what HTTP version
    the client uses.
    ● A POST request is used for logging in. The request must have a request target of “/”
    ● A GET request is used for retrieving files after logging in. The request must have a
    request target of the filename from the root “/”, such as “/file.txt”.
        ○ The server then finds the “file.txt” file in the directory for that user only (via the
        username)
        ○ The server must read the contents of the file as text and insert it into the HTTP
        body of the response
    ● A sample POST request with response
        ○ Client sends:
                POST / HTTP/1.0
                Host: 127.0.0.1:8080
                User-Agent: curl/7.68.0
                Accept: */*
                username: Jerry
                password: 4W61E0D8P37GLLX
        ○ Server replies with:
                HTTP/1.0 200 OK
                Set-Cookie: sessionID=0x68938897ef8fdfc8
                Logged in!
        ○ Server logs:
                SERVER LOG: 2023-11-02-15-16-46 LOGIN SUCCESSFUL: Jerry : 4W61E0D8P37GLLX
    ● A corresponding sample GET request for the file “file.txt” with response. Note: This is
    after logging in with the previous POST request and still within the session timeout limit.
        ○ Client sends:
            GET /file.txt HTTP/1.0
            Host: 127.0.0.1:8080
            User-Agent: curl/7.68.0
            Accept: */*
            Cookie: sessionID=0x68938897ef8fdfc8
        ○ Server replies with:
            HTTP/1.0 200 OK
            The different snowstorm exhibits fee.
        ○ The server also logs:
            SERVER LOG: 2023-11-02-15-23-21 GET SUCCEEDED: Jerry : /file.txt