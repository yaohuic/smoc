# -*- coding: utf-8 -*-

"""Server that stands between the optimizer and cadence."""

import os
import os.path
import socket
import sys
import time

from ..utils.file import read_yaml


class Server(object):
    """A server that handles skill commands.

    This server is started and ran by cadence. It listens for commands from the optimizer
    from a UNIX socket, then pass the command to cadence. It then gather the result and
    send it back to the optimizer.

    Arguments:
        sckt {file} -- socket for communication between optimizer and server
        cad_file {file} -- cadence stream

    Keyword Arguments:
        debug {boolean} -- if true send debug messages to cadence(default: {False})
    """

    def __init__(self, sckt, cad_file, debug=False):
        """Create a new Server instance."""

        self.sckt = sckt
        self.cad_file = cad_file
        self.cad_in = self.cad_file.stdin
        self.cad_out = self.cad_file.stdout
        self.cad_err = self.cad_file.stderr
        self.debug = debug

        # Uninitialized variables
        self.conn = None    # Socket object used for communication
        self.addr = None    # The address bound to the socket on the optimizer

    def run(self):
        """Start the server."""

        # Receive initial message from cadence, to check connectivity
        # TODO: METER AQUI UM TRY!!!
        msg = self.recv_skill()

        # Start connection between the optimizer and the server (UNIX socket)
        s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

        try:
            os.remove("/tmp/pythcad_socket")
        except OSError:
            pass

        # Start to listen to the socket defined by the file
        s.bind("/tmp/pythcad_socket")
        s.listen(1)

        # Waits for client connection
        self.conn, _ = s.accept()

        # Forwards the message received from Cadence
        self.conn.sendall(msg)

        if self.debug is True:
            self.send_debug('Client is connected!')

        while True:

            # Receive request from the optimizer
            # TODO: Meter assíncrono
            req = self.conn.recv(1024)

            # Check for request to end connection
            if req.upper() == "DONE":
                break

            # Process the optimizer request
            expr = self.process_skill_request(req)

            # Send the request to Cadence
            self.send_skill(expr)

            # Wait for the response from Cadence
            msg = self.recv_skill()

            if self.debug is True:
                self.send_debug('Data sent to client: %s' % msg)

            # Process the Cadence response
            obj = self.process_skill_response(msg)

            # Send the message to the optimizer
            self.conn.sendall(obj)

        self.close()    # Stop the server

    def send_skill(self, expr):
        """Send a skill expression to Cadence for evaluation.

        Arguments:
            data {string} -- skill expression
        """
        self.cad_in.write(expr)
        self.cad_in.flush()

    def recv_skill(self):
        """Receive a response from Cadence.

        First receives the message length (number of bytes) and then receives the message

        Returns:
            msg {string} -- message received from cadence
        """
        num_bytes = int(self.cad_out.readline())
        msg = self.cad_out.read(num_bytes)

        # Remove the '\n' from the message
        if msg[-1] == '\n':
            msg = msg[:-1]

        return msg

    def send_warn(self, warn):
        """Send a warning message to Cadence.

        Arguments:
            warn {string} -- warning message
        """
        self.cad_err.write(warn)
        self.cad_in.flush()

    def send_debug(self, msg):
        """Send a debug message to Cadence.

        Arguments:
            msg {string} -- debug message
        """

        time.sleep(1)
        self.send_warn(msg)

    def process_skill_request(self, req):
        """Process a skill request from the optimizer.

        Based on the given request object, returns the skill expression
        to be evaluated by Cadence.

        Arguments:
            req {dict} -- request object

        Returns:
            expre {string or None} -- expression to be evaluated by Cadence
        """
        # TODO: for now it's just a string
        expr = req

        return expr

    def process_skill_response(self, msg):
        """Process the skill response from Cadence.

        Arguments:
            msg {string} -- cadence response

        Returns:
            obj {dict} -- response object
        """

        # TODO: for now it's just a string
        obj = msg

        return obj

    def close(self):
        """Close this server."""
        self.conn.close()
        os.remove("/tmp/pythcad_socket")

        # Send feedback to Cadence
        self.send_warn("Connection with the optimizer ended!")
        self.cad_out.close()  # close stdout
        self.cad_err.close()  # close stderr
        self.cad_file.exit(255)  # close connection to cadence (code up to 255)


def start_server():
    """Start the server"""

    sckt = read_yaml()['socket']['file']

    server = Server(sckt, sys, debug=True)

    server.run()


if __name__ == "__main__":
    start_server()