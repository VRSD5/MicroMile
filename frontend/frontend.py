import flask
import requests
import json





app = flask.Flask(__name__)


ACCOUNTANT = "http://accountant.default.svc.cluster.local"
GAMER = "http://gamer.default.svc.cluster.local"
LOBSTER = "http://lobster.default.svc.cluster.local"



@app.route("/")
def serve_root():
	
	#If signed in redirect to
	#return flask.get(f"{LOBSTER}/ui")
	#Else
	#return flask.get(f"{ACCOUNTANT}/ui")
	#Figure out how to change url possibly
	return flask.send_file("static/index.html")

@app.route("/<path:path>")
def reroute(path):
	return flask.send_from_directory("static", path)

@app.route("/accountant/<path:path>", methods=['POST', 'GET'])
def reroute_accountant(path):
	if flask.request.method == 'POST':
		r = requests.post(
			f"{ACCOUNTANT}/{path}",
			json = flask.request.json
		)
		return r
	else:
		r = requests.get(
			f"{ACCOUNTANT}/{path}",
			json = flask.request.json
		)
		return r

@app.route("/lobster/<path:path>", methods=['POST', 'GET'])
def reroute_accountant(path):
	if flask.request.method == 'POST':
		r = requests.post(
			f"{LOBSTER}/{path}",
			json = flask.request.json
		)
		return r
	else:
		r = requests.get(
			f"{LOBSTER}/{path}",
			json = flask.request.json
		)
		return r


@app.route("/accountant/sign-in", methods=['POST'])
def sign_in():
	r = requests.post(
		f"{ACCOUNTANT}/api/sign-in",
		json=flask.request.json
	)

	res = flask.make_response(flask.redirect("/lobster/ui"))
	res.set_cookie('jwt_token', r.json()["token"])

	return res

@app.route('/ui/comments', methods=['GET'])
def get_comments():
	r = requests.get(f"{ACCOUNTANT}/comments")
	return  flask.jsonify(r.json())



