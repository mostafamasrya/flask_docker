
from flask import Flask ,jsonify,request
from flask_pymongo import PyMongo
from bson import json_util
import os
from abc import ABC, abstractmethod

# ===============================================================


app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mostafa"
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mostafa")


mongo = PyMongo(app)

@app.route("/")
def helloworld():
    return "Hello World!"



@app.route("/ramadan")
def functionOne():
    
    return "yes"



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


















if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=5000)
