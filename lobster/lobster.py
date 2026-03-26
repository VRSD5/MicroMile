import flask
import json
from datetime import datetime


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



class Lobbies:	
	def add_lobby(self, lobby_name, creator, invitee=None):
		#TODO Figure out how to deal with empty invitee
		game = (lobby_name, creator, invitee)

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
			cursor.execute("INSERT INTO users(name, player_a, player_b) VALUES(%s, %s, %s)", game)
			
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

		return json.dumps(game)
	
	def get_lobbies(self, username=None):
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

			#TODO query to get lobbies and if username != None filter by username
			cursor.execute("SELECT content FROM comments")
			

			comments = cursor.fetchall()

			# Close the connection
			cursor.close()
			connection.close()

		except psycopg2.OperationalError as e:
			print(f"Connection error: {e}")

		#TODO that thing where you don't get all values you get a subset
		return comments
	
	def check_lobby_exists(self, lobby_name):
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

			#TODO check if lobby exists
			cursor.execute("SELECT content FROM comments")
			lobby_exists = False

			

			# Close the connection
			cursor.close()
			connection.close()

		except psycopg2.OperationalError as e:
			print(f"Connection error: {e}")

	
		return lobby_exists

	def close_lobby(self, lobby_name):
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

			#TODO query to delete lobby by name
			cursor.execute("SELECT content FROM comments")
			

			comments = cursor.fetchall()

			# Close the connection
			cursor.close()
			connection.close()

		except psycopg2.OperationalError as e:
			print(f"Connection error: {e}")

		#TODO that thing where you don't get all values you get a subset
		return comments
	





app = flask.Flask(__name__)


lobbies = Lobbies()


@app.route("/ui")
def serve_root():
	return flask.send_file("static/index.html")

@app.route("/<path:path>")
def serve_static(path):
	return flask.send_from_directory("static", path)


#TODO
@app.route('/api/create-lobby', methods=['POST'])
def create_lobby():
	data = flask.request.json

	# Check if user exists if not add user
	if not lobbies.check_user_exists():
		lobbies.add_user(data.get("text", ""))
	# Provide security token
	
	#print(data.get("text"))
	return flask.Response(
		lobbies.add_user(data.get("text", "")),
		mimetype="application/json"
	)

@app.route('/api/check-lobby')
def check_lobby():
	pass

@app.route('/api/close-lobby')
def close_lobby():
	pass

@app.route('/api/join-lobby')
def join_lobby():
	pass






	