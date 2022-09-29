from flask import Flask
from flask_socketio import SocketIO, emit
from faker import Faker
fake = Faker()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=False, engineio_logger=False,
                    cors_allowed_origins="*")

clientList = []

questions = [
    {
        "index": 0,
        "question": "Quanto é 2 + 2?",
        "answer": "a",
        "options": {
            "a": "é 6",
            "b": "é 2",
            "c": "é 3",
            "d": "é 4",
            "e": "é 9"
        }
    },
    {
        "index": 0,
        "question": "Quanto é 1 + 1?",
        "answer": "a",
        "options": {
            "a": "é 1",
            "b": "é 3",
            "c": "é 5",
            "d": "é 6",
            "e": "é 2"
        }
    }
]


class Round:
    def __init__(self, question):
        self.question = question
        self.open = True
        self.answers = []

    def add_answer(self, user, name, answer):
        self.answers.append({
            "user": user,
            "name": name,
            "answer": answer
        })


currentRound = Round(questions[0]['index'])
finishedRounds = []


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


@socketio.on('start-game')
def handle_start_game():
    print('** NEW GAME **')
    currentRound = Round(questions[0]['index'])
    response = {
        "question": currentRound.question,
        "options": questions[currentRound.question]['options']
    }
    emit('begin-round', response, broadcast=True)


@socketio.on('answer')
def handle_answer(data):
    print('** NEW ANSWER **')
    print(data)
    currentRound.add_answer(
        user=data['user'], name=data['name'], answer=data['answer'])

    if (len(currentRound.answers) == len(clientList)):
        currentRound.open = False
        response = {
            "round": currentRound.question,
            "question": questions[currentRound.question]['question'],
            "correctAnswer": questions[currentRound.question]['answer'],
            "answers": currentRound.answers
        }
        print(response)
        emit('round-result', response, broadcast=True)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
