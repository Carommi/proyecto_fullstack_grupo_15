from decouple import config
from motor.motor_asyncio import AsyncIOMotorClient


MONGODB_URL = config("MONGODB_URL", default="mongodb://localhost:27017")
DATABASE_NAME = config("DATABASE_NAME", default="global_speak")

client = AsyncIOMotorClient(MONGODB_URL)
database = client[DATABASE_NAME]
estudiantes_collection = database["estudiantes"]
matriculas_collection = database["matriculas"]
