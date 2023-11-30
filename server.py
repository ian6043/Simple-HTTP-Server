# Author imw27 Ian Wilkinson
import sys
import socket
import json
import random
from datetime import datetime
import hashlib


class CookieManager:
    def __init__(self):
        self.cookies = {}

    def set_cookie(self, name, value):
        creation_time = datetime.utcnow()  # Timestamp when the cookie was created
        self.cookies[name] = {"value": value, "created_at": creation_time}

    def update_cookie_time(self, name):
        if name in self.cookies:
            self.cookies[name]["created_at"] = datetime.utcnow()

    def get_cookie(self, name):
        cookie = self.cookies.get(name)
        if cookie:
            return cookie["value"]
        return None

    def get_cookie_timestamp(self, name):
        cookie = self.cookies.get(name)
        if cookie:
            return cookie["created_at"]
        return None

    def has_duration_passed(self, name, duration):
        cookie_timestamp = self.get_cookie_timestamp(name)
        if cookie_timestamp:
            current_time = datetime.utcnow()
            time_difference_seconds = (current_time - cookie_timestamp).total_seconds()
            return time_difference_seconds >= duration
        return False

    def print_all_cookies(self):
        for name, cookie in self.cookies.items():
            print(
                f"Name: {name}, Value: {cookie['value']}, Created At: {cookie['created_at']}"
            )


global_cookie_manager = CookieManager()


def extractStartLine(request):
    lines = request.split("\r\n")
    start_line = lines[0]
    thing = start_line.split(" ")

    return thing


def generate_random_64bit_hex():
    random_int = random.getrandbits(64)
    hex_representation = format(random_int, "016x")
    return hex_representation


def createHTTPResponse(status, headers=None, body=None):
    response = "HTTP/1.0 " + status + "\r\n"
    if headers:
        for header in headers:
            response = response + header + "\r\n"
    if body != None:
        response = response + " \r\n" + body + "\r\n"
    return response


def extractHeaders(request):
    lines = request.split("\r\n")
    # print("LINES")
    # print(lines)
    lines = lines[1:]
    count = 0
    for line in lines:
        count += 1
        if line == "":
            break
    return lines[: count - 1]


def splitHeader(header):
    result = header.split(":", 1)
    result[1] = result[1].strip()
    return result


def isValidCredentials(username, password, accounts_file):
    with open(accounts_file) as json_file:
        data = json.load(json_file)
        try:
            if username in data:
                info = data[username]
                salt = info[1]
                salted_password = password + salt
                hashed_password = hashlib.sha256(
                    salted_password.encode("utf-8")
                ).hexdigest()
                return hashed_password == info[0]
            else:
                # print("not found in file")
                return 0
        except FileNotFoundError:
            # print("ewwow")
            return 0


def logMessage(message: str):
    current_datetime = datetime.now()
    formatted_datetime = current_datetime.strftime("%Y-%m-%d-%H-%M-%S")
    s = "SERVER LOG: " + formatted_datetime + " " + message
    return s


# returns an http response
def handlePost(headers, accounts_file):
    # print("Handling Post")
    username = None
    password = None
    # print("HEADERS :")
    # print(headers)
    for header in headers:
        headerParts = splitHeader(header)
        if headerParts[0] == "username":
            username = headerParts[1].strip()
        if headerParts[0] == "password":
            password = headerParts[1].strip()
    # print("username " + username + " password " + password)
    if not (username and password):
        print(logMessage("LOGIN FAILED"))
        return createHTTPResponse("501 Not Implemented")
    if isValidCredentials(username, password, accounts_file):
        # COOKIEESSSSSSSSSSSSSSSSSSSSSSSSSSS
        sessionID = generate_random_64bit_hex()
        global_cookie_manager.set_cookie(sessionID, username)
        header = "Set-Cookie: sessionID=" + sessionID
        # print("header")
        # print(header)
        print(logMessage(f"LOGIN SUCCESSFUL: {username} : {password}"))
        return createHTTPResponse("200 OK", [header], "Logged in!")
    else:
        print(logMessage(f"LOGIN FAILED: {username} : {password}"))
        return createHTTPResponse("200 OK", None, "Login Failed!")


def handleGet(start_line, headers, timeout, root_dir):
    # print("Handling Get")
    cookie = None
    for header in headers:
        headerParts = splitHeader(header)
        if headerParts[0] == "Cookie":
            cookie = headerParts[1].strip().split("=")[1]
    target = start_line[1]
    if not cookie:
        return createHTTPResponse("401 Unauthorized")
    if global_cookie_manager.get_cookie(cookie):
        user = global_cookie_manager.get_cookie(cookie)
        print("user:")
        print(user)
        if not global_cookie_manager.has_duration_passed(cookie, int(timeout)):
            global_cookie_manager.update_cookie_time(cookie)
            file_path = root_dir + user + target
            try:
                with open(file_path, "r") as file:
                    contents = file.read()
                    print(logMessage(f"GET SUCCEEDED: {user} : {target}"))
                    return createHTTPResponse("200 OK", None, contents)
            except FileNotFoundError:
                print(logMessage(f"GET FAILED: {user} : {target}"))
                return createHTTPResponse("404 NOT FOUND")
        else:
            print(logMessage(f"SESSION EXPIRED: {user} : {target}"))
            return createHTTPResponse("401 Unauthorized")
    else:
        print(logMessage(f"COOKIE INVALID: {target}"))
        print(cookie)
        global_cookie_manager.print_all_cookies()
        return createHTTPResponse("401 Unauthorized")


def main():
    if len(sys.argv) != 6:
        print("Water Chestnuts")
        print(len(sys.argv))
        exit()

    ip = sys.argv[1]
    port = sys.argv[2]
    accounts_file = sys.argv[3]
    session_timeout = sys.argv[4]
    root_dir = sys.argv[5]

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_socket.bind((ip, int(port)))

    server_socket.listen(5)

    while True:
        client_socket, client_address = server_socket.accept()

        request = client_socket.recv(1024)
        # print(type(request))
        # print(request)
        request = request.decode()
        # print(request)
        start_line = extractStartLine(request)

        # print(start_line)

        headers = extractHeaders(request)
        if start_line[0] == "POST" and start_line[1] == "/":
            res = handlePost(headers, accounts_file)
            print(res)
            client_socket.send(res.encode())
        elif start_line[0] == "GET":
            res = handleGet(start_line, headers, session_timeout, root_dir)
            print(res)
            client_socket.send(res.encode())
        else:
            res = createHTTPResponse("501 Not Implemented")
            print(res)
            client_socket.send(res.encode())
        client_socket.close()


if __name__ == "__main__":
    main()
