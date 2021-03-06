#!/usr/bin/python
# -*- coding: utf-8 -*-
"""
Very simple web server for ParZu
"""

from __future__ import unicode_literals

import logging
from flask import Flask, request, Response

from parzu_class import Parser, process_arguments

suggested_outputformats = ['conll', 'prolog', 'graphical']
other_outputformats = ['tokenized', 'tagged', 'preprocessed', 'moses', 'raw']
valid_outputformats  = suggested_outputformats + other_outputformats

outputformat_docstring = ""
for outputformat in suggested_outputformats:
  outputformat_docstring += """      <li><a href="/parse?text=Ich bin ein Berliner.&format={0}">{0}</a></li>""".format(outputformat)

index_str = """<!doctype html>
<html lang="en">
<title>ParZu API</title>
<body>
Simple web API for ParZu, supporting both GET and POST requests.
<br/>
<br/>
Arguments:
<ul>
  <li>text: the raw text that you want to parse</li>
  <li>format: the desired output format. Suggested choices:
  <ul>
  {0}
  </ul>
  </li>
</ul>
<br/>
For more information, see <a href="http://github.com/rsennrich/ParZu">http://github.com/rsennrich/ParZu</a>.
</body></html>
""".format(outputformat_docstring)

class Server(object):

    def __init__(self):
        options = process_arguments(commandline=False)
        options['extrainfo'] = 'secedges'
        self.parser = Parser(options)
        self.app = Flask('ParZuServer')

        @self.app.route('/', methods=['GET'])
        def index():
            return Response(index_str, 200, mimetype='text/html')

        @self.app.route('/parse/', methods=['GET', 'POST'])
        def parse():
            if request.method == "GET":
                text = request.args.get('text', None)
                outputformat = request.args.get('format', 'conll')
            else:
                input = request.get_json(force=True)
                text = input.get('text')
                outputformat = input.get('format', 'conll')
            if not text:
                return "Please provide text as POST data or GET text= parameter\n", 400

            if outputformat not in valid_outputformats:
                return "Please provide valid output format as POST data or GET format= parameter\n</br>Valid outputformats are: <ul><li>{0}</li></ul>".format('</li>\n<li>'.join(valid_outputformats)), 400

            parses = self.parser.main(text, inputformat='plain', outputformat=outputformat)

            if outputformat in ['tokenized', 'tagged', 'conll', 'prolog', 'moses']:
                result = '\n'.join(parses)
            elif outputformat in ['preprocessed', 'raw']:
                result = parses
            elif outputformat == 'graphical':
                return Response(parses[0], mimetype='image/svg+xml')

            return Response(result, mimetype='text/plain')

if __name__ == '__main__':
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--port", "-p", type=int, default=5003,
                        help="Port number to listen to (default: 5003)")
    parser.add_argument("--host", "-H", help="Host address to listen on (default: localhost)")
    parser.add_argument("--debug", "-d", help="Set debug mode", action="store_true")
    args = parser.parse_args()

    logging.basicConfig(level=logging.DEBUG if args.debug else logging.INFO,
                        format='[%(asctime)s %(name)-12s %(levelname)-5s] %(message)s')

    server = Server()

    server.app.run(port=args.port, host=args.host, debug=args.debug, threaded=True)
