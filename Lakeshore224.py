"""
Connect to Lakeshore224 over TCP Ethernet. Basic readout queries 

Manual: 
https://www.lakeshore.com/docs/default-source/product-downloads/224_manual.pdf?sfvrsn=57de6414_7

Derek Fujimoto
Sep 2026
"""
import socket
import numpy as np 
import time

class Lakeshore224(object):

    # default number of bytes to read out at once
    RECV_BYTES = 1024

    # termination character
    TERM = '\n'

    def __init__(self, ip, port=7777):

        # create connection
        self.socket = socket.create_connection((ip, port), timeout=10)

        # set timeout on send/recv
        self.socket.settimeout(1.0) # seconds

    def close(self):
        """terminate the connection"""
        self.socket.close()

    def query(self, cmd:str):

        # format cmd
        cmd += self.TERM

        # send cmd - ensure full command is sent
        sent = 0
        while sent < len(cmd):
            s = self.socket.send(cmd[sent:].encode('ascii'))
            sent += s
            if s == 0:
                raise ConnectionError("Lakeshore224 socket connection broken")

        # read response until terminator character is recorded
        msg = ""
        resp = ""
        t0 = time.monotonic() # timeout on response time
        while self.TERM not in resp:
            resp = self.socket.recv(self.RECV_BYTES).decode()
            msg += resp

            if time.monotonic()-t0 > 1:
                raise TimeoutError("Lakeshore224 timeout on recv")
            
        return msg.strip()

    def get_tempK(self, input):
        """Get temperature of input in Kelvin
        
        Args: 
            input (str): one of A, B, C1-C5, D1-D5, 0 (all)
        Returns: 
            float|np.ndarray: temperature in K
        """

        resp = self.query(f'KRDG? {input}')

        if input in (0, '0'):
            resp = resp.split(',')
            resp = np.fromiter(map(float, resp), dtype=float)
        else:
            resp = float(resp)

        return resp
        