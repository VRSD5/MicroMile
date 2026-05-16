import flask
from flask import request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity, set_access_cookies
import json
from datetime import datetime
from functools import wraps
import requests


key = {
	"accountant":"http://accountant.default.svc.cluster.local",
	"lobster":"http://lobster.default.svc.cluster.local",
	"gamer":"http://gamer.default.svc.cluster.local"
}


AUTH_KEY = 'super_super_duper_secret_key'


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
app.config["JWT_COOKIE_CSRF_PROTECT"] = False



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
	try:
		data = flask.request.json
		username = data.get("text", "")
		if username in {"root", "open"}:
			return flask.jsonify({"res":"invalid username"})
		# Check if user exists if not add user
		resp = requests.post(f"{key['accountant']}/api/sign-in",
			json=data, 
		)
		
		# Provide security token
		access_token = create_access_token(identity=username)
		
		res = flask.jsonify({
			"redirect":"/ui/service/lobster",
		})
		
		set_access_cookies(res, access_token)
		return res
	except Exception as e:
		return flask.jsonify({"Exception":str(e)})
	

@app.route("/service/<service>/<path:path>", methods=["POST", "GET"])
@jwt_required()
def interior_routing(service, path):
	try:
		if service not in {"accountant", "lobster", "gamer"}:
			return flask.jsonify({"service":service, "path":path}),404
		target_url = f"{key[service]}/{path}"

		user = get_jwt_identity()
		headers = dict(request.headers)
		excluded = {"Host", "Content-Length", "Accept-Encoding"}
		headers = {k: v for k, v in request.headers if k not in excluded}
		if user != None:
			token = create_access_token(identity=user)

			headers["Authorization"] = f"Bearer {token}"
		
		payload = request.get_json(silent=True)
		#return flask.jsonify({"target":target_url})
		resp = requests.request(
			method=request.method,
			url=target_url,
			headers=headers,
			data=request.data

		)

		return flask.Response(resp.content, resp.status_code, resp.headers.items())
	except Exception as e:
		return flask.jsonify({"Exception":e})