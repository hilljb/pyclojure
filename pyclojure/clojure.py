#!/usr/bin/python2

""" A Python module wrapping nrepl to interact with a Leiningen Clojure REPL.

Some notes:
- All return values are unicode objects inside a dictionary.
- You need to explicitly kill the repl before exiting.

Example:
>>> import clojure
>>> repl = clojure.NREPL()
nREPL server started on port 57041 on host 127.0.0.1 - nrepl://127.0.0.1:57041

>>> repl.eval('(defn f [a b] (+ a b))')
{u'session': u'658b32e6-ee3f-4a44-aa24-06ce375e4fb4', u'ns': u'user', u'value': u"#'user/f"}

>>> repl.eval('(f 1 2)')
{u'session': u'32ca0012-0fc1-4170-977c-6d480f678766', u'ns': u'user', u'value': u'3'}
"""


__author__ = "Jason B. Hill"
__email__ = "jason@jasonbhill.com"

import os
import subprocess

import nrepl

class NREPL(object):
    """ Create a Leiningen NREPL and interact with it.
    """
    def __init__(self, port=None):
        """ Initiate a Leiningen NREPL.

        INPUT
        -----
        port : int : optional
            The port to use for the NREPL server.
        """
        # Make sure the port is a positive integer
        if port:
            if not isinstance(port, (int, long)):
                raise TypeError("NREPL port must be an integer: %s given" % port)
            if port < 1:
                raise ValueError("NREPL port must be greater than zero: %s given" % port)

        self.port = port
        self.host = 'localhost'

        # Form the command to execute
        cmd = "lein repl :headless"
        if self.port:
            cmd += " :port %s" % self.port

        # Execute the command
        proc = subprocess.Popen(
            cmd.split(),
            stdout=subprocess.PIPE,
            stderr=open(os.devnull,'w'),
            stdin=open(os.devnull,'w')
        )

        # Get the return string and parse the port
        retport = None
        while not retport:
            retline = proc.stdout.readline()
            if 'server started' in retline:
                print retline
                retport = retline.split('port')[1].split()[0]

        if retport:
            self.port = retport


    def eval(self, cmd):
        """ Evaluate a command using the attached NREPL.

        INPUT
        -----
        cmd : str
            The command to execute.

        OUTPUT
        ------
        A dictionary with u'session', u'ns', and u'value'.
        """
        host_string = 'nrepl://' + str(self.host) + ':' + str(self.port)
        c = nrepl.connect(host_string)
        c.write({"op": "eval", "code": cmd})
        print "%s" % c.read()


    def exit(self):
        """ Shut down the NREPL server.

        This method should be called so the NREPL server is not zombied.
        """
        self.eval('(System/exit 0)')

