from flask import Flask
from flask_socketio import SocketIO, emit
from faker import Faker
fake = Faker()

app = Flask(__name__)

app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, logger=False, engineio_logger=False,
                    cors_allowed_origins="*")

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
        "index": 1,
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


class Game:
    def __init__(self):
        self.currentRound = None
        self.finishedRounds = []
        self.finished = False
        self.users = []

    def user_exists(self, userId):
        for i in range(len(self.users)):
            if self.users[i]['id'] == userId:
                return True
        return False

    def user_already_answered(self, id):
        for i in range(len(self.currentRound.answers)):
            if self.currentRound.answers[i]['user'] == id:
                return True
        return False

    def all_users_answered(self):
        answer_user_ids = map(
            lambda answer: answer['user'], self.currentRound.answers)

        not_answered_users = filter(
            lambda user: user['id'] not in answer_user_ids, self.users)

        if (len(list(not_answered_users)) == 0):
            return True
        else:
            return False

    def show_round_results(self):
        self.currentRound.open = False
        response = {
            "round": game.currentRound.question,
            "question": questions[game.currentRound.question]['question'],
            "correctAnswer": questions[game.currentRound.question]['answer'],
            "answers": game.currentRound.answers
        }
        print(response)
        emit('round-result', response, broadcast=True)

    def new_answer(self, data):
        if (not self.user_already_answered(data['user'])):
            self.currentRound.add_answer(
                user=data['user'], name=data['name'], answer=data['answer'])
            if (self.all_users_answered()):
                print("ALL USERS ANSWERED")
                self.show_round_results()

    def register_user(self, user):
        exits = self.user_exists(userId=user["id"])
        if (not exits):
            self.users.append(user)
            if (self.currentRound.open):
                response = {
                    "question": questions[game.currentRound.question]['question'],
                    "options": questions[game.currentRound.question]['options']
                }
                print('** JOIN ROUND **')
                emit('begin-round', response)

    def finish_game(self):
        self.finished = True
        self.currentRound = None

    def next_round(self):
        print(self.currentRound)
        if (self.currentRound == None):
            newQuestion = 0
        else:
            newQuestion = self.currentRound.question + 1
            self.finishedRounds.append(self.currentRound)

        if (len(questions) > newQuestion):
            self.currentRound = Round(questions[newQuestion]['index'])

            print(self.currentRound)
            response = {
                "question": questions[self.currentRound.question]['question'],
                "options": questions[self.currentRound.question]['options']
            }
            emit('begin-round', response, broadcast=True)
        else:
            self.finish_game()


game = Game()


@socketio.on('connect')
def on_join(auth):
    newClient = auth['user']
    print('** NEW CONNECTION **')
    game.register_user(newClient)
    emit('client-list', game.users, broadcast=True)


@socketio.on('start-game')
def handle_start_game():
    print('** NEW GAME **')
    game.next_round()


@socketio.on('answer')
def handle_answer(data):
    print('** NEW ANSWER **')
    print(data)
    game.new_answer(data)


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    socketio.run(app)
