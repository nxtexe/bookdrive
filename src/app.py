from flask_login import LoginManager, login_user, login_required, logout_user, login_url, current_user
from flask import Flask, render_template, request, abort, redirect, url_for
from flask_socketio import SocketIO, emit, send
from werkzeug.utils import secure_filename
from common.database import Database
from models.spider import BookSpider
from is_safe_url import is_safe_url
from models.book import Book
from datetime import datetime
from models.user import User
from os import environ
import json
import os
import re


app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
environ['secret'] = "secret"
app.secret_key = environ["secret"]
socketio = SocketIO(app)
UPLOAD_FOLDER = './images/'
ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

@app.before_first_request
def initialize():
	Database.initialize()

@login_manager.user_loader
def load_user(user_id):
	return User.get_by_id(user_id)

@app.route('/')
def home():
	books = Book.get_all()
	return render_template("home.html", books=books)

@login_manager.unauthorized_handler
def unauthorized():
	if request.method == 'GET':
		return redirect(login_url('/login', request.url))
	else:
		return dict(error=True, message="Please Log In For Access"), 403

@app.route('/account')
@login_required
def user_account():
	return render_template("user_account.html")

@app.route("/logout")
@login_required
def logout():
	logout_user()
	return redirect(url_for('home'))


@app.route('/login', methods=['GET', 'POST'])
def login():
	if request.method == 'GET':
		return render_template("login.html", url="/login", name="Login")
	else:
		part = request.form['part']
		if part == "1":
			email = request.form['email']
			o_auth = request.form['o_auth']
			next = request.args.get('next')
			user = User.get_by_email(email)
			if user is not None:
				if user.o_auth:
					if o_auth == "1":
						login_user(user)
						return next or url_for('home')
					else:
						return "Google User"
				else:
					return "Continue"
			else:
				if o_auth == "1":
					user = User(email=email, o_auth=True)
					user.save_to_mongo()
					login_user(user)
					return next or url_for('home')
				else:
					return "User Doesn't Exist"
		elif part == "2":
			email = request.form['email']
			password = request.form['password']
			user = User.get_by_email(email)
			if user.verify_password(password) is False:
				return "Password Invalid"
			else:
				login_user(user)
				next = request.args.get('next')
				#if not is_safe_url.is_safe_url(next, {request.url_root.split('/')[-2]}):
					#return abort(400)
				return next or url_for('home')

@app.route('/signup', methods=['GET', 'POST'])
def signup():
	if request.method == 'GET':
		return render_template("signup.html", url="/signup", name="Sign Up")
	else:
		part = request.form['part']
		if part == "1":
			email = request.form['email']
			o_auth = request.form['o_auth']
			next = request.args.get('next')
			if o_auth == "1":
				user = User.get_by_email(email)
				if user is None:
					user = User(email=email, o_auth=True)
					user.save_to_mongo()
					login_user(user)
					return next or url_for('home')
				else:
					login_user(user)
					return next or url_for('home')
			elif User.get_by_email(email) is None:
				return "Continue"
			else:
				return "User Already Exists"
		elif part == "2":
			fname = request.form['fname']
			lname = request.form['lname']
			email = request.form['email']
			password = request.form['password']
			cellphone = request.form['cellphone']
			next = request.args.get('next')
			user = User(fname=fname, lname=lname, email=email, password=User.hash_password(password), cellphone=cellphone)
			user.save_to_mongo()
			login_user(user)
			# if not is_safe_url.is_safe_url(next, {request.url_root.split('/')[-2]}):
			# 	return abort(400)
			return next or url_for('home')

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

def allowed_file(filename):
	return '.' in filename and \
				 filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/list_book', methods=['POST'])
def list_book():
	condition = request.form['condition']
	price = request.form['price']
	title = request.form['title']
	isbn = request.form['isbn']
	authors = request.form['authors']
	publish_date = request.form['publish_date']
	category = request.form['category']
	cover_image = request.form['cover_image']
	publisher = request.form['publisher']
	edition = request.form['edition']
	binding = request.form['binding']
	quantity = request.form['quantity']
	description = request.form['description']
	files = request.files.getlist("images")
	image_list = []
	book = Book(description=description, quantity=quantity, uploader=current_user._id, condition=condition, price=price, title=title, isbn=isbn, authors=authors, publish_date=publish_date, category=category, cover_img=cover_image, publisher=publisher, edition=edition, binding=binding)
	for file in files:
		if file.filename == '':
			return 'No selected file'
		if file and allowed_file(file.filename):
			filename = secure_filename(file.filename)
			#save as book_id.filename.fileformat
			image_list.append(f"{book._id}.{filename}")
			file.save(os.path.join(app.config['UPLOAD_FOLDER'], f"{book._id}.{filename}"))
	book.images = image_list
	book.save_to_mongo()
	return book._id

@app.route('/update/description/<string:book_id>', methods=['POST'])
def update_description(book_id):
	book = Book.get_by_id(book_id)
	if book is None:
		return "Book not found"
	else:
		description = request.form['description-2']
		book.description = description
		book.update("description", description)
		return "Updated"

@app.route('/book/activate/<string:book_id>', methods=['POST'])
def activate_book(book_id):
	book = Book.get_by_id(book_id)
	if book is None:
		return "Book not found"
	else:
		book.update("active", True)
		return "Active"

@app.route('/messageboard')
@login_required
def render_board():
	return render_template("message_board.html")


@socketio.on('my event')
def handle_message(message):
	emit('broadcast', message, broadcast=True)


if __name__ == "__main__":
	app.run(debug=True)
	# socketio.run(app, debug=True)