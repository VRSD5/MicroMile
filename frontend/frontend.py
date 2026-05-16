import flask
from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import json
from datetime import datetime
from functools import wraps
import requests


key = {
	"accountant":"http://accountant.default.127.0.0.1.sslip.io",
	"lobster":"http://lobster.default.127.0.0.1.sslip.io",
	"gamer":"http://gamer.default.127.0.0.1.sslip.io"
}


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
app.config['JWT_TOKEN_LOCATION'] = ['cookies']
app.config["JWT_COOKIE_SECURE"] = False
app.config["JWT_COOKIE_SAMESITE"] = "Lax"



jwt = JWTManager(app)

users = Users()


@app.route("/ui/accountant")
def serve_accountant():
	return flask.send_file("static/accountant.html")

@app.route("/ui/service/<service>")
@jwt_required()
def serve_service(service):
	return flask.send_file(f"static/{service}.html")

@app.route("/api/sign-in", methods=["POST"])
def sign_in():
	data = flask.request.json
	username = data.get("text", "")
	# Check if user exists if not add user
	resp = requests.post(f"{key["accountant"]}/api/sign-in",
		json=data, 
	)
	redirect = resp.json["redirect"]
	
	
	# Provide security token
	access_token = create_access_token(identity=username)
	
	res = flask.jsonify({
		"redirect":redirect,
	})
	

	set_access_cookies(res, access_token)
	return res
	

@app.route("/<service>/<path:path>", methods=["POST", "GET"])
def interior_routing(service, path):
	if service not in {"accountant", "lobster", "gamer"}:
		return flask.jsonify({"service":service, "path":path}),404
	target_url = f"{key[service]}/{path}"

	user = get_jwt_identity()
	headers = request.headers
	if user != None:
		token = create_access_token(identity=user)

		headers["Authorization"] = f"Bearer {token}"
	resp = requests.request(
		method=request.method,
		url=target_url,
		headers=headers,
		json=request.json

	)

	return flask.Response(resp.content, resp.status_code, resp.headers.items())