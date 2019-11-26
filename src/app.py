from flask import Flask, render_template, request
from os import environ
import json
from models.spider import BookSpider
from flask_socketio import SocketIO, emit, send

app = Flask(__name__)
environ['secret'] = "secret"
app.secret_key = environ["secret"]
socketio = SocketIO(app)

@app.route('/')
def home():
	return render_template("home.html")

@app.route('/search/<string:query>')
def search(query):
	return "None"

@app.route('/scrape_test')
def scrape_test():
	return render_template("scrape_test.html")

@app.route('/scrape', methods=['POST'])
def scrape():
	query = request.form['query']
	structure_type = request.form['type']
	if query is not None:
		spider = BookSpider(query)
		spider.scrape()
		if structure_type == "sorted":
			for key in spider.parse_dict:
				spider.parse_dict[key] = spider.sort_structure(spider.parse_dict[key])
		return json.dumps(spider.parse_dict)
	else:
		return "None"

@app.route('/messageboard')
def render_board():
	return render_template("message_board.html")


@socketio.on('my event')
def handle_message(message):
	emit('broadcast', message, broadcast=True)


if __name__ == "__main__":
	#app.run(debug=True)
	socketio.run(app, debug=True)