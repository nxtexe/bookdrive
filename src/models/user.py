from flask_login import UserMixin
from common.database import Database
import hashlib
import uuid


class User(UserMixin):
	def __init__(self, email, fname=None, lname=None, o_auth=False, password=None, cellphone=None, _id=None):
		self.email = email
		self.password = password
		self.fname = fname
		self.lname = lname
		self.cellphone = cellphone
		self._id = uuid.uuid4().hex if _id is None else _id
		self.o_auth = o_auth

	def get_id(self):
		return self._id

	@staticmethod
	def hash_password(password):
		salt = uuid.uuid4().hex
		return hashlib.sha512(salt.encode() + password.encode()).hexdigest() + ':' + salt

	def verify_password(self, login_password):
		password, salt = self.password.split(':')
		return password == hashlib.sha512(salt.encode() + login_password.encode()).hexdigest()


	@classmethod
	def get_by_email(cls, email):
		data = Database.find_one(collection="users", query={"email": email})
		if data is not None:
			return cls(**data)

	@classmethod
	def get_by_id(cls, _id):
		data = Database.find_one(collection="users", query={"_id": _id})
		if data is not None:
			return cls(**data)

	def json(self):
		return {
			'_id': self._id,
			'fname': self.fname,
			'lname': self.lname,
			'email': self.email,
			'password': self.password,
			'cellphone': self.cellphone,
			'o_auth': self.o_auth
		}

	def save_to_mongo(self):
		Database.insert(collection="users", data=self.json())
