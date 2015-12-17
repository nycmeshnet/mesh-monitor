import os
import sys
from flask import Flask, request
from flask.ext.restful import Resource, Api


app = Flask(__name__)
api = Api(app, prefix='/api/v1')


class RouterData(Resource):
    def post(self):
        # Make sure it is an authorized router
        router = request.remote_addr
        if router == '10.224.98.1':
            data = request.json
            parse_data(data)
        else:
            print("Data from unauthorized router")

        return {'success': True}

api.add_resource(RouterData, '/routerdata')


def parse_data(data):

    nodes = data['nodes']
    nodes = nodes.split("\n")
    # Remove first 2 lines because it is just the header
    nodes.pop(0)
    nodes.pop(0)

    # name,blocked,primaryIp,routes,viaIp,viaDev,metric,lastDesc,lastRef,
    for node in nodes:
        print(node)

    print(data['timestamp'])
    print(len(nodes))

if __name__ == '__main__':
    app.run(host='0.0.0.0', debug=True)
