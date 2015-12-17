import os
from flask import Flask, request, send_from_directory
from flask.ext.restful import Resource, Api

import sqlalchemy
from sqlalchemy import create_engine, Column, Integer, String
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker


# Set timezone to UTC
os.environ['TZ'] = 'UTC'

Base = declarative_base()

app = Flask(__name__, static_folder="web")
api = Api(app, prefix='/api/v1')


######################
##
## Static web routes
##
######################

@app.route('/')
def index():
    return send_from_directory('web', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('web', path)

######################
##
## API Classes
##
######################

class APIRouterData(Resource):
    def post(self):
        success = False
        # Make sure it is an authorized router
        router = request.remote_addr
        if router == '10.224.98.1':
            data = request.json
            parse_data(data)
            success = True
        else:
            print("Data from unauthorized router")

        return {'success': success}


class APINodes(Resource):
    def get(self):
        nodes = db_session.query(Node).all()

        node_list = []
        for node in nodes:
            node_list.append(row2dict(node))
            
        return {'nodes': node_list}


class APILastSeen(Resource):
    def get(self):
        last_seen = int(db_session.query(Status).filter(Status.name == 'lastSeen').first().value)

        return {'last_seen': last_seen}


api.add_resource(APIRouterData, '/routerdata')
api.add_resource(APINodes, '/nodes')
api.add_resource(APILastSeen, '/nodes/last_seen')


######################
##
## Util functions
##
######################

def row2dict(row):
    d = {}
    for column in row.__table__.columns:
        d[column.name] = getattr(row, column.name)

    return d


def parse_data(data):
    """
    Process data received from the node
    """
    nodes = data['nodes']
    timestamp = data['timestamp']  # UTC time in epoch from the node

    # Update global last_seen
    update_last_seen(timestamp)

    nodes = nodes.split("\n")
    # Remove first 2 lines because it is just the header
    nodes.pop(0)
    nodes.pop(0)

    # Update/add each node to the database
    # name,blocked,primaryIp,routes,viaIp,viaDev,metric,lastDesc,lastRef,
    for node_raw_data in nodes:
        node_raw_data = node_raw_data.split(',')
        node_data = {'name': node_raw_data[0],
                     'blocked': node_raw_data[1],
                     'primaryIp': node_raw_data[2],
                     'routes': node_raw_data[3],
                     'viaIp': node_raw_data[4],
                     'viaDev': node_raw_data[5],
                     'metric': node_raw_data[6],
                     'lastDesc': node_raw_data[7],
                     'lastRef': node_raw_data[8],
                     'lastSeen': timestamp,
                     }
        add_node(node_data)

    # Check if we have any new nodes
    # A node is new when `Node.lastSeen` == `Node.firstSeen`


    # Check to see what nodes are down
    # A node is down when `Node.lastSeen` != `Status.lastSeen`



######################
##
## SQL functions
##
######################

def add_node(data):
    node_exist = db_session.query(Node).filter(Node.primaryIp == data['primaryIp']).first()
    if node_exist is None:
        # Add new node to database
        node_data = Node(name=data['name'],
                         blocked=data['blocked'],
                         primaryIp=data['primaryIp'],
                         routes=data['routes'],
                         viaIp=data['viaIp'],
                         viaDev=data['viaDev'],
                         metric=data['metric'],
                         lastDesc=data['lastDesc'],
                         lastRef=data['lastRef'],
                         lastSeen=data['lastSeen'],
                         firstSeen=data['lastSeen'],
                         )
        db_session.add(node_data)

    else:
        node_data = db_session.query(Node)\
                              .filter(Node.primaryIp == data['primaryIp'])\
                              .update({Node.name: data['name'],
                                       Node.blocked: data['blocked'],
                                       Node.routes: data['routes'],
                                       Node.viaIp: data['viaIp'],
                                       Node.viaDev: data['viaDev'],
                                       Node.metric: data['metric'],
                                       Node.lastDesc: data['lastDesc'],
                                       Node.lastRef: data['lastRef'],
                                       Node.lastSeen: data['lastSeen'],
                                       })

    try:
        db_session.commit()
    except sqlalchemy.exc.IntegrityError:
        # tried to add an item to the database which was already there
        pass


def update_last_seen(last_seen):
    """
    update last_seen value in database
    """
    db_session.query(Status).filter(Status.name == 'lastSeen').update({Status.value: last_seen})
    db_session.commit()


######################
##
## SQL Tables
##
######################

class Status(Base):
    __tablename__ = 'status'
    id    = Column(Integer,    primary_key=True, autoincrement=True)
    name  = Column(String(50), nullable=False)
    value = Column(String(50), nullable=False)


class Node(Base):
    __tablename__ = 'nodes'
    name      = Column(String(100), nullable=False)
    blocked   = Column(Integer,     nullable=False)
    primaryIp = Column(String(100), primary_key=True)
    routes    = Column(Integer,     nullable=False)
    viaIp     = Column(String(100), nullable=False)
    viaDev    = Column(String(10),  nullable=False)
    metric    = Column(String(10),  nullable=False)
    lastDesc  = Column(Integer,     nullable=False)
    lastRef   = Column(Integer,     nullable=False)
    lastSeen  = Column(Integer,     nullable=False)
    firstSeen = Column(Integer,     nullable=False)


######################
##
## Main
##
######################

if __name__ == '__main__':
    db_file = "nodes.sqlite"

    db_is_new = False
    if not os.path.isfile(db_file):
        db_is_new = True

    engine = create_engine('sqlite:///' + db_file)

    # Create if it does not exist
    Base.metadata.create_all(engine)

    Base.metadata.bind = engine
    DBSession = sessionmaker(bind=engine)
    db_session = DBSession()

    if db_is_new:
        # Init database values
        status_last_seen = Status(name='lastSeen', value=0)
        db_session.add(status_last_seen)
        db_session.commit()

    app.run(host='0.0.0.0', debug=True)
