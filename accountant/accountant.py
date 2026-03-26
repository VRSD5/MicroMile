import flask
from flask import request, jsonify
import json
from datetime import datetime
import jwt
from functools import wraps

import psycopg2
import os

# Connection parameters loaded from environment variables
DB_NAME = "bXlkYXRhYmFzZQ=="
DB_USER = "bXl1c2Vy"
DB_PASSWORD = "bXlwYXNzd29yZA=="
DB_HOST = "postgresql" # This should be the K8s service name (e.g., "db")
DB_PORT = 5432 # e.g., 5432

DB_NAME = "mydatabase"
DB_USER = "myuser"
DB_PASSWORD = "mypassword"

#TODO Set up a secret so I don't have this
AUTH_KEY = 'very_secret_key'


class Users:	
	data = {}
	def add_user(self, username):
		#token = however I generate a JST
		token = jwt.encode({"username":username}, AUTH_KEY, algorithm="HS256")
		
		self.data[username] = token

		return token
	
		user = (username, token)
		try:
			# Connect to the PostgreSQL database
			connection = psycopg2.connect(
				dbname=DB_NAME,
				user=DB_USER,
				password=DB_PASSWORD,
				host=DB_HOST,
				port=DB_PORT
			)
			cursor = connection.cursor()

			# Execute a simple query
			cursor.execute("INSERT INTO users(username, token) VALUES(%s, %s)", user)
			
			# Close the connection
			cursor.close()
			connection.commit()
			connection.close()

		except psycopg2.OperationalError as e:
			print(f"Connection error: {e}")
			return json.dumps(str(e))
			#return json.dumps({"error": "DB Error",
					#   "DB_NAME": DB_NAME,
					#   "DB_USER": DB_USER,
					#   "DB_PASS": DB_PASSWORD,
					#   "DB_HOST": DB_HOST,
					#   "DB_PORT": DB_PORT})

		return json.dumps({
			"token":token
		})
	
	def check_user_exists(self, username):
		user_exists = False

		if username in self.data.keys():
			user_exists = True

		return user_exists

		try:
			# Connect to the PostgreSQL database
			connection = psycopg2.connect(
				database=DB_NAME,
				user=DB_USER,
				password=DB_PASSWORD,
				host=DB_HOST,
				port=DB_PORT
			)
			cursor = connection.cursor()

			# query to check if user exists
			cursor.execute("SELECT content FROM comments")
			user_exists = False

			comments = cursor.fetchall()

			# Close the connection
			cursor.close()
			connection.close()

		except psycopg2.OperationalError as e:
			print(f"Connection error: {e}")

		return user_exists
	
	def get_user_token(self, username):
		if not self.check_user_exists(username):
			return None
		return self.data[username]
	
		try:
			# Connect to the PostgreSQL database
			connection = psycopg2.connect(
				database=DB_NAME,
				user=DB_USER,
				password=DB_PASSWORD,
				host=DB_HOST,
				port=DB_PORT
			)
			cursor = connection.cursor()

			# query to get user token
			cursor.execute("SELECT content FROM comments")
			

			#token = cursor.fetchall()
			token = "testing_token"

			# Close the connection
			cursor.close()
			connection.close()

		except psycopg2.OperationalError as e:
			print(f"Connection error: {e}")

		return json.dumps({"token":token})

	





app = flask.Flask(__name__)


users = Users()


@app.route("/ui")
def serve_root():
	return flask.send_file("static/index.html")

@app.route("/<path:path>")
def serve_static(path):
	return flask.send_from_directory("static", path)



@app.route('/api/sign-in', methods=['POST'])
def sign_in():
	data = flask.request.json

	# Check if user exists if not add user
	if not users.check_user_exists():
		users.add_user(data.get("text", ""))
	# Provide security token
	
	#print(data.get("text"))
	
	return flask.Response(
		json.dump({"token":users.get_user_token(data.get("text", ""))}),
		mimetype="application/json"
	)

@app.route('/api/check_user')
def check_user():
	pass

@app.route('/api/check_token')
def check_token():
	pass

	#Needs both username and token field
	data = flask.request.json
	#Get token from users
	test_token = users.get_user_token(data.get("username", ""))

	#Compare token
	return flask.Response(
		json.dumps({"success":test_token == data.get("token", "")}),
		mimetype="application/json"
		)


def token_required(f):
	@wraps(f)
	def decorated(*args, **kwargs):
		token = request.cookies.get('jwt_token')

		if not token:
			return jsonify({'message': 'Token is missing!'}), 401
		
		try:
			data = jwt.decode(token, AUTH_KEY, algorithms=["HS26"])
			current_user = data["username"]
		except:
			return jsonify({'message': 'Token is invalid!'}), 401

		return f(current_user, *args, **kwargs)
	return decorated