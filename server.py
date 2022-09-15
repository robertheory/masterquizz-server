from flask import Flask
from flask_socketio import SocketIO, emit
from faker import Faker
fake = Faker()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=False, engineio_logger=False,
                    cors_allowed_origins="*")

clientList = []


def searchClient(client):
    for i in range(len(clientList)):
        if clientList[i]['id'] == client['id']:
            return True
    return False


@socketio.on('message')
def handle_message(data):
    print('received message: ' + data)


@socketio.on('connect')
def on_join(auth):
    newClient = auth['user']
    print('** NEW CONNECTION **')
    print(newClient)
    if (searchClient(newClient)):
        print('** CLIENT ALREADY EXISTS **')
    else:
        clientList.append(newClient)
    emit('client-list', clientList, broadcast=True)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
