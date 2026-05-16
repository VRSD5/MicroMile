import flask
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
import json
from datetime import datetime
import requests

ACCOUNTANT_URL = "http://accountant.default.svc.cluster.local"
GAMER_URL = "http://gamer.default.svc.cluster.local"

class Lobbies:
	data = {}
	invites = {}
	count = 0
	def add_lobby(self, creator, invitee="open"):
		
		game = (self.count, creator, invitee)
		self.data[self.count] = game
		if invitee not in self.invites:
			self.invites[invitee] = set() 
		self.invites[invitee].add(game)
		
		self.count += 1
		


	
	def get_lobbies(self, username="open"):
		if username in self.invites:
			return list(self.invites[username])
		return []


	def get_lobby_info(self, lobby):
		if lobby in self.data:
			return self.data[lobby]
		else:
			return None
	
	def check_lobby_exists(self, lobby_name):
		return lobby_name in self.data

	def close_lobby(self, lobby_name):
		game = self.data[lobby_name]
		self.invites[game[2]].discard(game)
		self.data.pop(lobby_name)
	
	def join_lobby(self, lobby_name, username):
		game = self.data[lobby_name]
		if game[2] == "open" or game[1] == username:
			self.data[lobby_name] = (lobby_name, game[1], username)
			self.invites[None].discard(game)
			self.invites[username].add(self.data[lobby_name])
			return True
		return False

	



app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super_super_duper_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_COOKIE_SECURE"] = False



jwt = JWTManager(app)



lobbies = Lobbies()




@app.route('/api/create-lobby-invite', methods=['POST'])
@jwt_required()
def create_lobby_invite():
	try:
		data = flask.request.json
		username = get_jwt_identity()
		invitee = data.get("text")
		if username == invitee:
			return flask.jsonify({"status": "fine", "idk":"attempted to invite self to lobby"})

		lobbies.add_lobby(username, invitee)
		return flask.jsonify({"status": "ok"})
	except Exception as e:
		return flask.jsonify({"Exception":e})


@app.route('/api/create-lobby', methods=['POST'])
@jwt_required()
def create_lobby():
	try:
		username = get_jwt_identity()
		
		lobbies.add_lobby(username)
		return flask.jsonify({"status": "ok"})
	except Exception as e:
		return flask.jsonify({"Exception":e})
		
	

@app.route('/api/close-lobby', methods = ['POST'])
@jwt_required()
def close_lobby():
	data = flask.request.json
	username = get_jwt_identity()
	lobby_name = data.get("text", "")
	game = lobbies.get_lobby_info(lobby_name)

	if username == game[1] or username == game[2]:
		lobbies.close_lobby(lobby_name)
	return flask.jsonify({"response":"response"})


@app.route('/api/join-lobby', methods = ['POST'])
@jwt_required()
def join_lobby():
	try:
		data = flask.request.json
		username = get_jwt_identity()
		lobby_name = data.get("id", "")
		
		game = lobbies.get_lobby_info(lobby_name)
		if game == None:
			return flask.jsonify({"No", "Game"})

		if game[2] == None:
			if not lobbies.join_lobby(lobby_name, username):
				return

			game = (game[0], game[1], username)
			lobbies.data[game[0]] = game

		if username == game[1] or username == game[2]:
			
			#Call gamer to make game
			root_token = create_access_token(identity="root")
			cookies = {"auth_token":root_token}
			
			requests.post(f"{GAMER_URL}/api/create-game"
					, json = {
						"lobby_name":lobby_name,
						"player_1":game[1],
						"player_2":game[2]
					}, 
					cookies=cookies)
			#redirect to gamer/ui/game/id
			return flask.redirect(f"/server/gamer/ui/game/{lobby_name}")
	except Exception as e:
		return flask.jsonify({"Exception":e})

@app.route('/api/lobbies', methods = ['GET'])
@jwt_required()
def get_lobbies():
	username = get_jwt_identity()
	hold = lobbies.get_lobbies(username)
	hold.extend(lobbies.get_lobbies())

	returnal = []
	for i in hold:
		returnal.append({"id": i[0], "player_1":i[1], "player_2":i[2] if i[2] else "None"})

	return flask.jsonify(returnal)



	