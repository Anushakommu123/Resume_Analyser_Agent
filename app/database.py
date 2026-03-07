"""
MongoDB database connection and vector store setup.
"""
from motor.motor_asyncio import AsyncIOMotorClient
from pymongo import ASCENDING
from typing import Optional
import logging

from app.config import settings

logger = logging.getLogger(__name__)


class Database:
    """MongoDB database connection manager."""
    
    client: Optional[AsyncIOMotorClient] = None
    database = None
    
    @classmethod
    async def connect(cls, raise_on_error: bool = False):
        """
        Connect to MongoDB database.
        
        Args:
            raise_on_error: If True, raise exception on connection failure. 
                          If False, log warning and continue without MongoDB.
        """
        try:
            logger.info(f"Attempting to connect to MongoDB at: {settings.mongodb_uri}")
            cls.client = AsyncIOMotorClient(
                settings.mongodb_uri,
                serverSelectionTimeoutMS=5000  # 5 second timeout
            )
            cls.database = cls.client[settings.database_name]
            
            # Verify connection
            await cls.client.admin.command('ping')
            logger.info(f"✓ Successfully connected to MongoDB: {settings.database_name}")
            logger.info("✓ RAG features are now ENABLED")
            
            # Ensure vector search index exists
            await cls._ensure_vector_index()
            
            return True
            
        except Exception as e:
            error_msg = str(e)
            logger.error(f"✗ Failed to connect to MongoDB: {error_msg}")
            logger.error(f"✗ MongoDB URI: {settings.mongodb_uri}")
            logger.error("✗ RAG features will be DISABLED")
            
            if raise_on_error:
                raise
            
            # Don't raise - allow app to start without MongoDB
            cls.client = None
            cls.database = None
            return False
    
    @classmethod
    async def disconnect(cls):
        """Disconnect from MongoDB database."""
        if cls.client:
            cls.client.close()
            logger.info("Disconnected from MongoDB")
    
    @classmethod
    async def _ensure_vector_index(cls):
        """Ensure vector search index exists for test cases collection."""
        try:
            collection = cls.database[settings.test_cases_collection]
            
            # Check if vector search index exists
            indexes = await collection.list_indexes().to_list(length=100)
            index_names = [idx.get("name") for idx in indexes]
            
            # Create vector search index if it doesn't exist
            # Note: For MongoDB Atlas, vector search indexes are created via Atlas UI
            # For local MongoDB, we'll create a regular index on the embedding field
            if "embedding_1" not in index_names:
                await collection.create_index([("embedding", ASCENDING)])
                logger.info("Created vector index on embedding field")
            
        except Exception as e:
            logger.warning(f"Could not create vector index: {e}")
            # Continue without vector index - will use regular queries
    
    @classmethod
    def get_collection(cls, collection_name: str):
        """Get a collection from the database."""
        if cls.database is None:
            raise RuntimeError(
                "Database not connected. Please ensure MongoDB is running and "
                "MONGODB_URI is correctly configured in .env file."
            )
        return cls.database[collection_name]
    
    @classmethod
    def is_connected(cls) -> bool:
        """Check if database is connected."""
        return cls.client is not None and cls.database is not None
    
    @classmethod
    def get_test_cases_collection(cls):
        """Get the test cases collection."""
        return cls.get_collection(settings.test_cases_collection)


# Database instance
db = Database()

