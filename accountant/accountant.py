import flask
from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import json
from datetime import datetime
from functools import wraps




AUTH_KEY = 'super_super_duper_secret_key'
LOBSTER_URL = "http://lobster.default.127.0.0.1.sslip.io"
# LOBSTER_URL = "http://localhost:3002"

class Users:	
	data = {}
	def add_user(self, username):
		if username in self.data:
			return False
		self.data[username] = {"wins":0, "draws":0, "losses":0}
		return True
	
	def check_user_exists(self, username):
		return username in self.data





app = flask.Flask(__name__)
app.config['JWT_SECRET_KEY'] = AUTH_KEY
app.config['JWT_TOKEN_LOCATION'] = ['headers']
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_SAMESITE"] = "Lax"



jwt = JWTManager(app)

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
	username = data.get("text", "")

	# Check if user exists if not add user
	if not users.check_user_exists(username):
		users.add_user(username)
	# Provide security token

	return flask.jsonify({
		"redirect":f"/ui/service/lobster"
	})




@app.route('/api/test-jwt', methods=['GET'])
@jwt_required()
def test_jwt():
	username = get_jwt_identity()
	return jsonify({
		"res":username
	})

@app.route('/api/update_stats', methods = ['PUT'])
@jwt_required
def updated_stats():
	test = get_jwt_identity()
	if test != "root":
		return
	
	data = flask.request.json
	user = data.get("User", "")
	event = data.get("Event", "")

	Users.data[user][event] += 1

@app.route('/api/get_stats', methods = ['GET'])
@jwt_required()
def get_stats():
	user = get_jwt_identity()
	return jsonify(Users.data[user])