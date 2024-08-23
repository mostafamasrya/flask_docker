
from flask import Flask ,jsonify
from flask_pymongo import PyMongo
from bson import json_util
import os

app = Flask(__name__)
# app.config["MONGO_URI"] = "mongodb://localhost:27017/mostafa"
app.config["MONGO_URI"] = os.getenv("MONGO_URI", "mongodb://localhost:27017/mostafa")


mongo = PyMongo(app)

@app.route("/")
def helloworld():
    return "Hello World!"


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


if __name__ == "__main__":
    app.run(debug=False,host='0.0.0.0',port=5000)
