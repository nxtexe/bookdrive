from common.database import Database
import uuid

class Book():
	def __init__(
		self,
		uploader,
		isbn,
		title,
		authors,
		publisher,
		edition,
		binding,
		publish_date,
		cover_img,
		price,
		category,
		quantity,
		condition,
		active=False,
		description=None,
		images=None,
		_id = None):
		self.isbn = isbn
		self.uploader = uploader
		self.title = title
		self.active = active
		self.authors = authors
		self.publisher = publisher
		self.edition = edition
		self.binding = binding
		self.publish_date = publish_date
		self.description = description
		self.cover_img = cover_img
		self.images = images
		self.price = price
		self.category = category
		self.condition = condition
		self.quantity = quantity
		self._id = uuid.uuid4().hex if _id is None else _id

	def update(self, attrib, val):
		Database.update(collection="books", query={"_id": self._id}, new_val={"$set": {attrib: val}})

	@classmethod
	def get_all(cls):
		books = Database.find(collection="books", query=({}))
		return [cls(**book) for book in books]

	@classmethod
	def get_by_title(cls, name):
		data = Database.find_one(collection="books", query={"title": title})
		if data is not None:
			return cls(**data)

	@classmethod
	def get_by_id(cls, _id):
		data = Database.find_one(collection="books", query={"_id": _id})
		if data is not None:
			return cls(**data)

	def json(self):
		return {
			'isbn': self.isbn,
			'uploader': self.uploader,
			'title': self.title,
			'active': self.active,
			'authors': self.authors,
			'publisher': self.publisher,
			'edition': self.edition,
			'quantity': self.quantity,
			'binding': self.binding,
			'publish_date': self.publish_date,
			'description': self.description,
			'cover_img': self.cover_img,
			'images': self.images,
			'price': self.price,
			'category': self.category,
			'condition': self.condition,
			'_id': self._id
			}

	def save_to_mongo(self):
		Database.insert(collection="books", data=self.json())