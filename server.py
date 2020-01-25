import json, requests, os, time
from flask import Flask, request
from requests_toolbelt import MultipartEncoder

from mobilepert import (MobilePert,
    ParseError, MissingActivity
    )

from mobiledodgem import (MobileDodgem,
    InvalidMove, MaximumMoveFindTries, AiLost
)

# PERT_TOKEN = os.environ['PERT_TOKEN']
# PERT_VERIFY = os.environ['PERT_VERIFY']

qamsorpath = './qamsor.json'
mp = MobilePert(qamsorpath)
md = MobileDodgem(qamsorpath)

app = Flask(__name__)

@app.route('/')
def index():
    return 'Hello World'

@app.route('/health')
def health():
    print('alive')
    return 'alive'

@app.route('/pert', methods=['GET'])
def pertget():
    print('getpert')
    if (request.args.get('hub.verify_token', '') == PERT_VERIFY):
        print("Verifiedpert")
        return request.args.get('hub.challenge', '')
    else:
        print('not verifiedpert')
        return "Error, wrong validation token"

@app.route('/pert', methods=['POST'])
def pertpost():
    global mp, md

    def forfeit(message):
        buttons = [
            {
                'type': 'postback',
                'title': 'FORFEIT',
                'payload': 'get started'
            },
            {
                'type': 'postback',
                'title': 'PLAY AGAIN',
                'payload': 'start-dodgem'
            }
        ]
        sendmessage_button(id, message, buttons, PERT_TOKEN)

    def send_movable_tokens(message, tokens):
        buttons = [
            {
                'type': 'postback',
                'title': token,
                'payload': f'dodgem-token={token}'
            } for token in tokens
        ]
        sendmessage_button(id, message, buttons, PERT_TOKEN)

    print('pertpost')
    data = request.get_json()
    if data["object"] == "page":
        for entry in data["entry"]:
            for messaging_event in entry["messaging"]:
                id = messaging_event["sender"]["id"]
                message = ''
                if messaging_event.get("message"):
                    event = messaging_event["message"]
                    if event.get("attachments"):
                        pass
                    else:
                        message = event.get("text")
                elif messaging_event.get("postback"):
                    message = messaging_event["postback"]["payload"]
                message = message.lower()
                print(message)

                if message == 'get started':
                    print('in started')
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'PERT/CPM',
                            'payload': 'start-pert'
                        },
                        {
                            'type': 'postback',
                            'title': 'DODGEM GAME',
                            'payload': 'start-dodgem'
                        }
                    ]
                    message = 'Welcome to QAMSOR 101, choose the tool you want to use and learn more on.'
                    sendmessage_button(id, message, buttons, PERT_TOKEN)

                elif message == 'start-pert':
                    mp = MobilePert(qamsorpath)
                    mp.reset(id)
                    mp.changeState(id, 'pert-reset')
                    message = 'Welcome to QAMSOR 101 PERT tool.\n\n'
                    message += 'Choose Next Action.'
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'ADD ACTIVITY',
                            'payload': 'activity-add'
                        },
                        {
                            'type': 'postback',
                            'title': 'WHAT IS PERT?',
                            'payload': 'pert-help'
                        }
                    ]
                    sendmessage_button(id, 'Choose Next Action', buttons, PERT_TOKEN)
                elif message == 'start-dodgem':
                    md = MobileDodgem(qamsorpath)
                    md.start(id)
                    md.change_state(id, 'dodgem-new')
                    button_message = 'Welcome to QAMSOR 101 DODGEM Game\n\n'
                    button_message += 'Choose Next Action.'
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'VS AI',
                            'payload': 'dodgem-choose_ai'
                        },
                        {
                            'type': 'postback',
                            'title': 'WHAT IS DODGEM?',
                            'payload': 'dodgem-help'
                        }
                    ]
                    sendmessage_button(id, button_message, buttons, PERT_TOKEN)
                elif message == 'pert-help':
                    mp.changeState(id, 'pert-help')
                    response = mp.perthelp()
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'PROCEED WITH PERT/CPM',
                            'payload': 'start-pert'
                        },
                        {
                            'type': 'postback',
                            'title': 'BACK TO TOOL SELECTION',
                            'payload': 'get-started'
                        }
                    ]
                    sendmessage_button(id, message, buttons, PERT_TOKEN)
                elif message == 'dodgem-help':
                    md.change_state(id, 'dodgem-help')
                    response = md.dodgemhelp()
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'PROCEED WITH DODGEM GAME',
                            'payload': 'start-dodgem'
                        },
                        {
                            'type': 'postback',
                            'title': 'BACK TO TOOL SELECTION',
                            'payload': 'get started'
                        }
                    ]
                    sendmessage_button(id, response, buttons, PERT_TOKEN)
                elif message == 'pert-reset':
                    mp.reset(id)
                    mp.changeState(id, 'pert-reset')
                    send_message(id, 'Your Pert Table has been reset', PERT_TOKEN)
                    button_message = 'Choose Next Action'
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'ADD ACTIVITY',
                            'payload': 'acivity-add'
                        },
                        {
                            'type': 'postback',
                            'title': 'GO BACK',
                            'payload': 'get started'
                        }
                    ]
                    sendmessage_button(id, button_message, buttons, PERT_TOKEN)
                elif message == 'activity-add':
                    response = 'Enter the activity\'s code, optimistic, average, and pessimistic values, as well as its predecessor activities if any.\n\n'
                    response += 'Activity entry format:\n<Code> <a> <m> <b> <pred>-<pred>-<pred>'
                    response += 'If the activity has no predecessor, just leave the area blank'
                    mp.changeState(id, 'add')
                    send_message(id, response, PERT_TOKEN)
                elif message == 'activity-evaluate':
                    try:
                        response = mp.solve(id)
                    except MissingActivity as e:
                        send_message(id, str(e), PERT_TOKEN)
                        mp.changeState('pert-error')
                        return 'missing activity error'
                    send_message(id, response, PERT_TOKEN)
                    send_pert_file(id, PERT_TOKEN)
                    mp.changeState(id, 'pert-solved')
                elif message == 'dodgem-choose_ai':
                    md.change_state(id, 'dodgem-choosing_ai')
                    buttons = [
                        {
                            'type': 'postback',
                            'title': 'EASY',
                            'payload': 'dodgem-ai=easy'
                        },
                        {
                            'type': 'postback',
                            'title': 'MEDIUM',
                            'payload': 'dodgem-ai=medium'
                        },
                        {
                            'type': 'postback',
                            'title': 'HARD',
                            'payload': 'dodgem-ai=hard'
                        }
                    ]
                    message = 'Dodgem is a good example to demonstrate to you, concepts of decision making.\n\n'
                    message += 'This bot uses 3 types of AI.\n'
                    message += 'Easy AI is controlled randomly\nMedium AI chooses the first best option.\n'
                    message += 'Hard AI uses MINIMAX algorithm to decide its move.\n\n'
                    message += 'Choose the AI of your bot opponent\nGOOD LUCK!!!'
                    sendmessage_button(id, message, buttons, PERT_TOKEN)
                elif 'dodgem-ai=' in message:
                    ai = message.split('=')[1]
                    md.change_ai(id, ai)
                    md.change_state(id, 'dodgem-choosing_token')
                    message = f'{ai.upper()} AI chosen.\nPlay with good decision making in mind.\n\n'
                    message += md.show_board(id) + '\n'
                    message += 'Choose the token you want to move.'

                    tokens = md.get_movable_tokens(id)
                    if len(tokens) == 0:
                        forfeit('No movable tokens remaining.')
                    else:
                        send_movable_tokens(message, tokens)
                elif 'dodgem-token=' in message:
                    ai = md.ai(id)
                    md.change_state(id, 'dodgem-choosing_move')
                    token = message.split('=')[1].upper()
                    move_ref = {'u':'Up','l':'Left','r':'Right','d':'Down'}

                    moves = md.get_available_moves_of_token(id, token)
                    message = ai.upper() + ' AI\n' + md.show_board(id) + '\n\n'
                    message += f'Choose the move of the token: {token}'
                    buttons = [
                        {
                            'type': 'postback',
                            'title': move_ref[move],
                            'payload': f'dodgem-move={token}-{move}'
                        } for move in moves
                    ]
                    sendmessage_button(id, message, buttons, PERT_TOKEN)
                elif 'dodgem-move=' in message:
                    def winner(message):
                        message = md.show_board(id) + '\n' + message
                        buttons = [
                            {
                                'type': 'postback',
                                'title': 'BACK TO TOOL SELECTION',
                                'payload': 'get started'
                            },
                            {
                                'type': 'postback',
                                'title': 'PLAY AGAIN',
                                'payload': 'start-dodgem'
                            }
                        ]
                        sendmessage_button(id, message, buttons, PERT_TOKEN)

                    ai = md.ai(id)
                    md.change_state(id, 'dodgem-moved_token')
                    token_move = message.split('=')[1].split('-')
                    token = token_move[0].upper()
                    move = token_move[1]
                    md.move_token(id, token, move)
                    if md.check_winner(id):
                        winner('Player Won! CONGRATULATIONS')
                        return 'payer wins'
                    message = ai.upper() + ' AI\n' + md.show_board(id)
                    send_message(id, message, PERT_TOKEN)

                    # AI MOVE AFTER PLAYER
                    send_message(id, 'AI Choosing his move...', PERT_TOKEN)
                    send_typing_on(id, PERT_TOKEN)                    
                    md.ai_move(id, ai)
                    if resp := md.check_winner(id):
                        winner('AI Won! Goodluck next time!')
                        return 'ai wins'
                    message = ai.upper() + ' AI\n' + md.show_board(id)

                    message += 'Choose the token you want to move.'
                    tokens = md.get_movable_tokens(id)
                    if len(tokens) == 0:
                        fmsg = f'{ai} AI\n{md.show_board}' + '\n\nNo movable tokens remaining.'
                        forfeit(fmsg)
                    else:
                        send_movable_tokens(message, tokens)
                else:
                    state = mp.state(id)
                    if state == 'add':
                        try:
                            temp = mp.add(id, message=message)
                            buttons = [
                                {
                                    'type': 'postback',
                                    'title': 'ADD ACTIVITY',
                                    'payload': 'activity-add'
                                },
                                {
                                    'type': 'postback',
                                    'title': 'EVALUATE',
                                    'payload': 'activity-evaluate'
                                },
                                {
                                    'type': 'postback',
                                    'title': 'RESET',
                                    'payload': 'pert-reset'
                                }
                            ]
                            response = mp.showactivities_s(id)
                            response += f'\n{temp}\nChoose Next Action'
                            sendmessage_button(id, response, buttons, PERT_TOKEN)
                            mp.changeState(id, 'added-activity')
                        except ParseError as e:
                            send_message(id, str(e), PERT_TOKEN)
                    
    return "okpert"               

def send_pert_file(id, token):
    dirpath = os.path.dirname(os.path.abspath(__file__))
    filename = f'pert{id}.csv'
    filepath = f'{dirpath}/{filename}'

    m = MultipartEncoder(
        fields = {
            "recipient": f"{{'id': {id}}}",
            "message": '''{
                "attachment": {
                    "type": "file",
                    "payload": {
                    }
                }
            }''',
            "filedata": (filepath, open(filepath, 'rb'), 'text/csv')
        }
    )

    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": token},

        headers={"Content-Type": m.content_type},

        data=m
    )

def sendmessage_button(id, message, buttons, token):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": token},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
            "recipient": {"id": id},
            "message": {
                "attachment": {
                    "type": "template",
                    "payload": {
                        "template_type": "button",
                        "text": message,
                        "buttons": buttons
                    }
                }
            }
        })
    )

def send_typing_on(id, token):
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": token},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
            "recipient": {"id": id},
            "sender_action": "typing_on"
        })
    )

def send_message(sender_id, message_text, token):
    '''
    Sending response back to the user using facebook graph API
    '''
    r = requests.post("https://graph.facebook.com/v2.6/me/messages",

        params={"access_token": token},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
            "recipient": {"id": sender_id},
            "message": {"text": message_text}
            }
        )
    )

def set_get_started_button():
    r = requests.post("https://graph.facebook.com/v5.0/me/messenger_profile",

        params={"access_token": PERT_TOKEN},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
            "get_started": {
                "payload": "get started"
            }
        })
    )
    print(r.text)

def set_persistent_menu():
    r = requests.post("https://graph.facebook.com/v5.0/me/messenger_profile",

        params={"access_token": PERT_TOKEN},

        headers={"Content-Type": "application/json"},

        data=json.dumps({
            "persistent_menu": [
                {
                    "locale": "default",
                    "composer_input_disabled": False,
                    "call_to_actions": [
                        {
                            "type": "postback",
                            "title": "TOOL SELECTION",
                            "payload": "get started"
                        }
                    ]
                }
            ]
        })
    )
    print(r.text)

if __name__ == "__main__":
    # set_get_started_button()
    # set_persistent_menu()
    app.run()