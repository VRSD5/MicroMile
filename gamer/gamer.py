import flask
import json
from datetime import datetime
from flask_jwt_extended import JWTManager, get_jwt_identity, jwt_required, create_access_token
import chess, chess.svg
import requests




class Games:
	games = {}
	player_games = {}
	def make_game(self, game_name, player_1, player_2):
		games[game_name] = (player_1, player_2, chess.Board(), None)
		if player_1 in self.player_games:
			self.player_games[player_1].add(game_name)
		else:
			self.player_games[player_1] = set(game_name)

		if player_2 in self.player_games:
			self.player_games[player_2].add(game_name)
		else:
			self.player_games[player_2] = set(game_name)
	
	def do_move(self, game_name, player, move):

		if game_name in self.player_games[player]:
			game = self.games[game_name]
			if (game[0] == player and game[2].turn) or (game[1] == player and not game[2].turn):
				nove = chess.Move.from_uci(move)
				if nove in games[2].legal_moves: 
					games[2].push(nove)
					outcome = game[2].outcome()
					if outcome:
						if outcome.winner == chess.WHITE:
							return {"end":True, "Winner":game[0], "Loser":game[1]}
						elif outcome.winner == chess.BLACK:
							return {"end":True, "Winner":game[1], "Loser":game[0]}
						else:
							return {"end":True, "Draw":True}
		return {"end":False}

	def check_player(self, game_name, player):
		return game_name in self.player_games[player]
	
	def get_players(self, game_name):
		return self.games[game_name][0], self.games[game_name][1]

	def close_game(self, game_name):
		game = self.games[game_name]
		self.player_games[game[0]].discard(game)
		self.player_games[game[1]].discard(game)
		self.games.pop(game_name)
		
	

LOBSTER_URL = "http:/lobster.default.127.0.0.1.sslip.io"
ACCOUNTANT_URL = "http:/lobster.default.127.0.0.1.sslip.io"




app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = 'super_super_duper_secret_key'
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_COOKIE_SECURE"] = False

jwt = JWTManager(app)

games = Games()

# @app.route("/ui")
# def serve_root():
# 	return flask.send_file("static/index.html")

#TODO figure out how to make <game_id be a game id and be relevant>
@app.route("/ui/game/<game_id>")
@jwt_required()
def serve_game(game_id):
	return flask.send_file("static/index.html")


@app.route("/api/game/start")
@jwt_required
def game_start():
	pass



@app.route('/api/create-game', methods=['POST'])
@jwt_required()
def create_game():
	user = get_jwt_identity()
	data = flask.request.json
	if not user == "root":
		return
	
	id = data.get("lobby_name", "")
	p1 = data.get("player_1", "")
	p2 = data.get("player_2")

	games.make_game(id, p1, p2)


@app.route('/api/game/<game_id>/move/<move_uci>')
@jwt_required
def move(game_id, move_uci):
	user = get_jwt_identity()
	res = games.do_move(game_id, user, move_uci)

	
	if res["end"]:
		if "Draw" in res:
			a, b = games.get_players(game_id)
			root_token = create_access_token(identity="root")
			
			res = requests.post(f"{ACCOUNTANT_URL}/update_stats",
						json={
							"User":a,
							"Event":"draws"
						}, cookies=cookies)
			res = requests.post(f"{ACCOUNTANT_URL}/update_stats",
						json={
							"User":b,
							"Event":"draws"
						},cookies = cookies)
		else:
			root_token = create_access_token(identity="root")
			
			requests.post(f"{ACCOUNTANT_URL}/update_stats",
					 json={
						 "User":res["Loser"],
						 "Event":"losses"
					 }, )
			requests.post(f"{ACCOUNTANT_URL}/update_stats",
					 json={
						 "User":res["Winner"],
						 "Event":"wins"
					 }, cookies=cookies)
		games.close_game(game_id)

@app.route('/api/game/<game_id>/resign')
@jwt_required
def resign(game_id):
	user = get_jwt_identity()
	if not games.check_player(game_id, user):
		return
	
	other, b = Games.get_players(game_id)
	
	if other  == user:
		other = b 
	
	root_token = create_access_token(identity="root")
	cookies = {"auth_token":root_token}
	requests.post(f"{ACCOUNTANT_URL}/update_stats",
					 json={
						 "User":user,
						 "Event":"losses"
					 }, cookies=cookies)
	requests.post(f"{ACCOUNTANT_URL}/update_stats",
					 json={
						 "User":other,
						 "Event":"wins"
					 }, cookies=cookies)
	games.close_game(game_id)

@app.route('/api/game/<game_id>/propose')
@jwt_required
def propose(game_id):
	user = get_jwt_identity()
	if not games.check_player(game_id, user):
		return
	

	other, b = games.get_players(game_id)
	if other  == user:
		other = b 

	if games.games[game_id][3] == None:
		games.games[game_id][3] = user
	if games.games[game_id][3] == other:
		root_token = create_access_token(identity="root")
		cookies = {"auth_token":root_token}
		res = requests.post(f"{ACCOUNTANT_URL}/update_stats",
						json={
							"User":user,
							"Event":"draws"
						}, cookies=cookies)
		res = requests.post(f"{ACCOUNTANT_URL}/update_stats",
						json={
							"User":other,
							"Event":"draws"
						},cookies = cookies)
		games.close_game(game_id)
	if games.games[game_id][3] == user:
		games.games[game_id][3] = None

@app.route('/api/list')
@jwt_required
def list_games():
	user = get_jwt_identity()
	
	return flask.jsonify(games.player_games[user])




	