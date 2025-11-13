from pymongo import MongoClient
URI = "mongodb+srv://newuser:hotmailsex.com@videoc.kanky.mongodb.net/notes"

client = MongoClient(URI,    tlsAllowInvalidCertificates=True,tls=True)
db = client.notes
login_collection = db['login']
register_collection = db['register']
notes_collection = db['notes']
print(db)