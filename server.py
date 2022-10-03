from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
import os

app = Flask(__name__)
CORS(app)

socketio = SocketIO(app, logger=False, engineio_logger=False,
                    cors_allowed_origins=[])

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
        self.next_round_confirmation = []

    def user_exists(self, user_id):
        user_ids = map(lambda user: user['id'], self.users)
        if (user_id in list(user_ids)):
            return True
        else:
            return False

    def user_already_answered(self, id):
        for i in range(len(self.currentRound.answers)):
            if self.currentRound.answers[i]['user'] == id:
                return True
        return False

    def all_users_answered(self):
        answer_user_ids = list(map(
            lambda answer: answer['user'], self.currentRound.answers))

        not_answered_users = list(filter(
            lambda user: user['id'] not in answer_user_ids, self.users))

        if (len(not_answered_users) == 0):
            return True
        else:
            return False

    def show_round_results(self):
        self.currentRound.open = False
        response = {
            "round": self.currentRound.question,
            "question": questions[self.currentRound.question]['question'],
            "correctAnswer": questions[self.currentRound.question]['answer'],
            "answers": self.currentRound.answers
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
        exits = self.user_exists(user["id"])
        emit('client-list', game.users, broadcast=True)
        print("Exists", exits)
        print("USER ", user)
        print("USERS ", len(self.users))

        if (not exits):
            self.users.append(user)

        if (bool(self.currentRound)):
            print('** HAS A ROUND **')
            if (self.currentRound.open):
                response = {
                    "question": questions[self.currentRound.question]['question'],
                    "options": questions[self.currentRound.question]['options']
                }
                print('** JOIN ROUND **')
                emit('begin-round', response)
            else:
                print('** SHOW RESULTS **')
                response = {
                    "round": self.currentRound.question,
                    "question": questions[self.currentRound.question]['question'],
                    "correctAnswer": questions[self.currentRound.question]['answer'],
                    "answers": self.currentRound.answers
                }
                emit('round-result', response)

    def finish_game(self):
        print('** GAME FINISHED **')

        response = list(map(lambda round: ({
            "round": round.question,
            "question": questions[round.question]['question'],
            "correctAnswer": questions[round.question]['answer'],
            "answers": round.answers,
        }), self.finishedRounds))

        print(response)
        emit('game-result', response, broadcast=True)

        self.finished = True
        self.currentRound = None

    def all_users_want_to_continue(self):
        not_confirmed_users = filter(
            lambda user: user['id'] not in self.next_round_confirmation, self.users)

        if (len(list(not_confirmed_users)) == 0):
            return True
        else:
            return False

    def handle_continue(self, userId):
        self.next_round_confirmation.append(userId)

        if (self.all_users_want_to_continue()):
            self.next_round()
            self.next_round_confirmation = []

    def next_round(self):
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
def on_connect(auth):
    global game
    newClient = auth['user']
    print('** NEW CONNECTION **')
    game.register_user(newClient)


@socketio.on('start-game')
def handle_start_game():
    global game
    print('** NEW GAME **')
    old_users = game.users
    game = Game()
    game.users = old_users
    game.next_round()


@socketio.on('answer')
def handle_answer(data):
    global game
    print('** NEW ANSWER **')
    print(data)
    game.new_answer(data)


@socketio.on('continue')
def handle_continue(data):
    global game
    print('** CONTINUE **')
    print(data)
    game.handle_continue(data['id'])


@socketio.on('disconnect')
def disconnect():
    print('Client disconnected')


if __name__ == '__main__':
    PORT = os.environ.get('PORT', 3333)
    socketio.run(app, allow_unsafe_werkzeug=True,
                 host='0.0.0.0', port=PORT, debug=True)
