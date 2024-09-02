
from flask import Flask ,jsonify,request
from flask_pymongo import PyMongo
from bson import json_util
import os
from abc import ABC, abstractmethod
from flask_cors import CORS
# ===============================================================


app = Flask(__name__)
CORS(app)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mostafa"
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mostafa")


mongo = PyMongo(app)

@app.route("/")
def helloworld():
    return "Hello World!"



@app.route("/create_meeting")
def functionOne():
    link = my_funct()
    data = {"message":"link returned successfully"
           ,"status":200,
           "link":link}
    return jsonify(data)



@app.route("/all_users")
def all_users():
    # Access a collection in your database
    users = mongo.db.users.find()  # 'users' is the collection name
    
    # Convert the MongoDB cursor to a list and then to JSON
    # users_list = [user for user in users]
    users_list = json_util.dumps(users)
    
    return users_list


@app.route("/add_user")
def add_user():
    # Insert a document into the 'users' collection
    mongo.db.users.insert_one({"name": "mostafa Doe", "email": "mostafa@example.com"})
    return jsonify(message="User added successfully!")


@app.route("/add_users")
def add_users():
    # Insert a document into the 'users' collection
    # mongo.db.users.insert_one({"name": "mostafa Doe", "email": "mostafa@example.com"})
    users = [
    {"name": "Alice", "email": "alice@example.com"},
    {"name": "Bob", "email": "bob@example.com"}
    ]
    mongo.db.users.insert_many(users)
    return jsonify(message="Users added successfully!")


@app.route("/find_user")
def find_user():
    user = mongo.db.users.find_one({"email":"bob@example.com"})
    if not user:
        return jsonify(message="Users not found yet!")
    user = json_util.dumps(user)
    return user


@app.route("/update_user")
def update():
    user = mongo.db.users.update_one({"email":"bob@example.com"}, {"$set": {"name": "mohmaed"}})
    return jsonify(message="Users updated successfully!")


@app.route("/count")
def count():
    count = mongo.db.users.count_documents({})
    print(count)

    return jsonify(message="Number of Documents" + str(count))

# ===============================================================
# ===============================================================
# ===============================================================
# =============== Design Patterns ===============================

# strategy design pattern


class PaymentStrategy(ABC):
    @abstractmethod
    def pay(self,amount):
        pass


class CashStrategy(PaymentStrategy):
    def pay(self,amount):
        print("i pay cash ,sir")
        return f"paid {amount} using cash way"
    
class OnlineStrategy(PaymentStrategy):
    def pay(self,amount):
        print("i pay online using online link ")
        return f"i pay {amount} online using online link "
    


class CreditCardStrategy(PaymentStrategy):
    def pay(self,amount):
        print("i pay using credit card")
        return f"{amount} paid using credit card"

class FawryStrategy(PaymentStrategy):
    def pay(self,amount):
        print("i pay using Fawry")
        return f"{amount} paid using Fawry"


class PaymentContext:
    def __init__(self,method,strategy=None):
        if method == "credit_cart":
            strategy = CreditCardStrategy()
        elif method == "cash":
            strategy = CashStrategy()
        elif method == "fawry":
            strategy = FawryStrategy()
        else:
            strategy = OnlineStrategy()
        self.strategy = strategy

    def set_strategy(self,strategy):
        self.strategy = strategy

    def execute_amount(self,amount):
        return self.strategy.pay(amount)
    


@app.route('/pay', methods=['POST'])
def pay_api():
    data = request.json
    method = data["method"]
    amount = data["amount"]
    
    context = PaymentContext(method)

    result = context.execute_amount(amount)


    return jsonify(result)








# =========================================================== meeting module


import json
import hmac
import hashlib
import random
import requests
from typing import Dict, Optional

api_key = 'plugnmeet'
api_secret = 'zumyyYWqv7KR2kUqvYdq4z4sXg7XTBD2ljT6'
server_url = 'https://demo.plugnmeet.com'


def send_request(body: Dict[str, any], method: str) -> Optional[Dict[str, any]]:
    # Convert the body to JSON string
    b = json.dumps(body)

    # Generate HMAC-SHA256 hash
    hmac_sha256 = hmac.new(api_secret.encode(), b.encode(), hashlib.sha256)
    signature = hmac_sha256.hexdigest()

    # Set headers
    headers = {
        'Content-Type': 'application/json',
        'API-KEY': api_key,
        'HASH-SIGNATURE': signature,
    }

    # Send POST request
    response = requests.post(
        f'{server_url}/auth/{method}',
        headers=headers,
        data=b
    )

    # Handle the response
    if response.status_code != 200:
        print(f'Error: {response.reason}')
        print(response.text)
        return None
    print(response.text)

    return response.json()


def process_request(room_info: Dict[str, any], user_info: Dict[str, any]) -> Optional[str]:
    # Check if the room is active or not
    is_room_active_req = {
        'room_id': room_info['room_id'],
    }

    res = send_request(is_room_active_req, 'room/isRoomActive')
    if res is None or not res.get('status'):
        print(res.get('msg', 'Unknown error'))
        return None

    is_room_active = res.get('is_active', False)

    # If not active, create the room
    if not is_room_active:
        room_create_res = send_request(room_info, 'room/create')
        if room_create_res is None or not room_create_res.get('status'):
            print('Error: ', room_create_res.get('msg', 'Unknown error'))
            return None

        is_room_active = room_create_res.get('status', False)

    # If room is active, join the room
    if is_room_active:
        get_join_token_req = {
            'room_id': room_info['room_id'],
            'user_info': user_info,
        }

        room_join_res = send_request(get_join_token_req, 'room/getJoinToken')
        if room_join_res and room_join_res.get('status'):
            # Handle successful join token response
            print('Join token response: ', room_join_res)
            link = f"{server_url}/?access_token={room_join_res['token']}"
            return link
        else:
            print(room_join_res.get('msg', 'Unknown error'))


def send_api_request(body: any, token: str, path: str, json_encode: bool = True,
                     content_type: str = 'application/json') -> any:
    try:
        # Convert the body to JSON string if json_encode is true
        request_body = json.dumps(body) if json_encode else body

        # Make the POST request
        response = requests.post(
            f'{server_url}/api/{path}',
            headers={
                'Authorization': token,
                'Content-Type': content_type,
            },
            data=request_body
        )

        # Handle the response
        print(response.text)
        return response.text
    except Exception as e:
        print(f'Error: {e}')
        if not json_encode:
            return {'status': False, 'msg': f'Error: {e}'}
        else:
            return {'status': False, 'msg': f'Error: {e}'}


def extract_token(get_token: str) -> Optional[str]:
    import re
    token_reg_exp = re.compile(r'eyJ[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+\.[a-zA-Z0-9-_]+')
    match = token_reg_exp.search(get_token)
    if match:
        return match.group(0)
    return None


def my_funct():
    room_info = {
        'room_id': '123',
        'empty_timeout': 60 * 60 * 2,
        'metadata': {
            'room_title': 'Demo room',
            'welcome_message': 'Welcome to plugNmeet!<br /> To share microphone click mic icon from bottom left side.',
            'room_features': {
                'allow_webcams': True,
                'mute_on_start': False,
                'allow_screen_share': True,
                'allow_rtmp': True,
                'admin_only_webcams': False,
                'allow_view_other_webcams': True,
                'allow_view_other_users_list': True,
                'allow_polls': True,
                'room_duration': 0,
                'enable_analytics': True,
                'allow_virtual_bg': True,
                'allow_raise_hand': True,
                'recording_features': {
                    'is_allow': True,
                    'is_allow_cloud': True,
                    'is_allow_local': True,
                    'enable_auto_cloud_recording': False,
                    'only_record_admin_webcams': False,
                },
                'chat_features': {
                    'allow_chat': True,
                    'allow_file_upload': True,
                    'max_file_size': 50,
                    'allowed_file_types': ['jpg', 'png', 'zip'],
                },
                'shared_note_pad_features': {'allowed_shared_note_pad': True},
                'whiteboard_features': {'allowed_whiteboard': True},
                'external_media_player_features': {'allowed_external_media_player': True},
                'waiting_room_features': {'is_active': True},
                'breakout_room_features': {'is_allow': True, 'allowed_number_rooms': 6},
                'display_external_link_features': {'is_allow': True},
                'ingress_features': {'is_allow': True},
                'speech_to_text_translation_features': {'is_allow': True, 'is_allow_translation': True},
            },
        },
    }

    characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
    user_id = ''.join(random.choice(characters) for _ in range(10))

    user_info = {
        'is_admin': True,
        'name': 'mahmoud',
        'user_id': user_id,
    }

    link = process_request(room_info, user_info)

    return link

#
# if __name__ == '__main__':
#     main()














if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=5000)
