#!/usr/bin/env python3

import flask
import json
from pprint import pprint


app = flask.Flask(__name__)


@app.route('/firewatch-hub/report', methods=['POST'])
def report():
    print('Request data:')
    pprint(json.loads(flask.request.data.decode()))
    return flask.jsonify({'ok': True})


if __name__ == '__main__':
    app.run(debug=True)
