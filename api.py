import os
import sys
from flask import Flask, request
from flask.ext.restful import Resource, Api

import sqlalchemy
from sqlalchemy import Column, ForeignKey, UniqueConstraint, PrimaryKeyConstraint, and_, or_
from sqlalchemy import create_engine, update, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship, sessionmaker


# Set timezone to UTC
os.environ['TZ'] = 'UTC'

Base = declarative_base(
)
app = Flask(__name__)
api = Api(app, prefix='/api/v1')


######################
##
## API Classes
##
######################

class RouterData(Resource):
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

api.add_resource(RouterData, '/routerdata')


######################
##
## Util functions
##
######################

def parse_data(data):

    nodes = data['nodes']
    timestamp = data['timestamp']  # UTC time in epoch

    nodes = nodes.split("\n")
    # Remove first 2 lines because it is just the header
    nodes.pop(0)
    nodes.pop(0)

    # name,blocked,primaryIp,routes,viaIp,viaDev,metric,lastDesc,lastRef,
    for node in nodes:
        print(node)

    print(timestamp)
    print(len(nodes))


######################
##
## SQL functions
##
######################

def update_last_seen(self, last_seen):
    """
    update last_seen value in database
    """
    db_session.query(Status).filter(Status.name == 'last_seen').update({Status.value: last_seen})
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


class Nodes(Base):
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
        status_last_seen = Status(name='last_seen', value=0)
        db_session.add(status_last_seen)
        db_session.commit()

    app.run(host='0.0.0.0', debug=True)
