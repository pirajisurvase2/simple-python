from motor.motor_asyncio import AsyncIOMotorClient,AsyncIOMotorDatabase
from config import DB_NAME, DB_USERNAME, DB_PASSWORD
from pymongo.database import Database
from pymongo.collection import Collection

client = AsyncIOMotorClient(f"mongodb+srv://{DB_USERNAME}:{DB_PASSWORD}@cluster0.eqjafpc.mongodb.net/{DB_NAME}?retryWrites=true&w=majority&appName=simplelender")
db :Database = client[DB_NAME]

users_collection: Collection = db["users"]
borrower_collection : Collection = db["borrower"]
transactions_collection: Collection = db["transactions"]