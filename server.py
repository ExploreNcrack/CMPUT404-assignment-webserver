#!/usr/local/bin/python3
#  coding: utf-8 
import socketserver
import os

# Copyright 2013 Abram Hindle, Eddie Antonio Santos, Zhaozhen Liang
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
# 
#     http://www.apache.org/licenses/LICENSE-2.0
# 
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
#
# Furthermore it is derived from the Python documentation examples thus
# some of the code is Copyright © 2001-2013 Python Software
# Foundation; All Rights Reserved
#
# http://docs.python.org/2/library/socketserver.html
#
# run: python freetests.py

# try: curl -v -X GET http://127.0.0.1:8080/


class MyWebServer(socketserver.BaseRequestHandler):
    
    def handle(self):
        """
        This function handles the http request that is recieved by the server 
        """
        # self.request is the TCP socket connected to the client
        self.data = self.request.recv(1024).strip()
        self.data = self.data.decode("utf-8")
        # split header string 
        self.data_split = self.data.split(" ")
        # print ("Got a request of: %s\n" % self.data.split())
        if not self._check_request_method():
            # Method not accept
            # send 405 message
            self._send_405_response()
            return
        request_path = self._check_request_path()
        if not request_path:
            # requested path is not allow or wrong 
            # send 404 message
            self._send_404_response()
            return 
        elif request_path == "301":
            # already handled send 301 to client in check_request_path
            return
        else:
            # read the request path object
            # send the request path file object as string
            self._send_file(request_path)
            return
        # self.request.sendall(bytearray("OK",'utf-8'))


    def _send_file(self, fileName):
        header = "HTTP/1.1 200 OK\r\nContent-Type: text/%s; charset=utf-8\r\n\r\n"%(fileName.split(".")[1])
        html_string = ""
        file = open(fileName, 'r')
        for line in file:
            html_string += line
        self.request.sendall(bytearray(header+html_string,'utf-8'))


    def _send_301_response(self, url):
        message301_header = "HTTP/1.1 301 Moved Permanently\r\nLocation: %s\r\nContent-Type: text/plain; charset=UTF-8\r\nStatus: 301 Moved Permanently\r\n\r\n"%(url)
        self.request.sendall(bytearray(message301_header,'utf-8'))



    def _send_404_response(self):
        message404_header = "HTTP/1.1 404 Not Found\r\nContent-Type: text/html; charset=utf-8\r\nStatus: 404 Not Found\r\n\r\n"
        message404_content = "<html><head><title>404 Not Found</title></head><body bgcolor='white'><center><h1>404 Not Found</h1></center></body></html>"
        message404 = message404_header + message404_content
        self.request.sendall(bytearray(message404,'utf-8'))


    def _send_405_response(self):
        message405_header = "HTTP/1.1 405 Method Not Allowed\r\nContent-Type: text/plain; charset=utf-8\r\nStatus: 405 Method Not Allowed\r\n\r\n"
        self.request.sendall(bytearray(message405_header,'utf-8'))

    
    def _check_request_method(self):
        """
        This function checks the request method that is stated in the http request header
        Return:
        True:
            Method accept: GET
        False:
            Method not accept: (POST/PUT/DELETE)
        """
        if self.data_split[0].upper() != "GET":
            return False
        return True


    def _check_request_path(self):
        """
        This function checks the request url
        Return:
        True:
            return requested object
        False:
            requested path is not allow or wrong
            path cannot contain ../
        """
        # path is in split data position index 1
        www = "www"
        check_path_accessibility = self._prevent_access_to_other_directory(www+self.data_split[1])
        check_path_is_file = os.path.isfile(www+self.data_split[1])
        check_path_is_dir = os.path.isdir(www+self.data_split[1])
        if not check_path_is_dir and not check_path_is_file:
            # requested path format invalid
            return False
        if not check_path_accessibility:
            # requested path is not allowed to access
            return False
        if check_path_is_dir:
            # if the requested path is directory 
            requested_path = self.data_split[1]
            if requested_path[-1] != "/":
                # check if there is / at the end
                # return 301 
                self._send_301_response(requested_path+"/")
                return "301"
        if check_path_is_dir:
            # request for root
            # return index.html
            return www+self.data_split[1]+"index.html"
        else:
            # request for file
            return www+self.data_split[1]
        

    def _prevent_access_to_other_directory(self, path_string):
        """
        This function checks the path string if it contains ../ 
        Return:
        True:
            it does not access to other directory
        False:
            it tries to access to directory outside of the www
        """        
        # get the www absolute path 
        current_dir = os.path.realpath("www")
        # retrieve all the children directory absolute path
        www_child_dirctories = []
        for sub_dir in os.walk(current_dir):
            www_child_dirctories.append(sub_dir[0])
        # www_child_dirctories = [x[0] for x in os.walk(current_dir)]
        abosulte_request_path = os.path.realpath(path_string)
        # if given path is a file
        if os.path.isfile(path_string):
            # get the file's directory
            dir_of_request_path = os.path.dirname(abosulte_request_path)
            # check if the file's directory is a child directory of www
            if dir_of_request_path not in www_child_dirctories:
                return False
        # if given path is a directory        
        if os.path.isdir(path_string):
            if abosulte_request_path not in www_child_dirctories:
                return False

        return True
         


if __name__ == "__main__":
    # declare host and portnumber
    HOST, PORT = "localhost", 8080
    socketserver.TCPServer.allow_reuse_address = True
    # Create the TCP server, binding to localhost on port 8080
    server = socketserver.TCPServer((HOST, PORT), MyWebServer)

    # Activate the server; this will keep running until you
    # interrupt the program with Ctrl-C
    server.serve_forever()

