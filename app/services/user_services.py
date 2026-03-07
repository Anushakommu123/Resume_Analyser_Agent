"""
Service layer for RAG operations and test case management.
"""
from typing import List, Dict, Any, Optional
import json
import logging
from openai import AsyncOpenAI
import numpy as np
from bson import ObjectId

from app.config import settings
from app.database import db

logger = logging.getLogger(__name__)

# Initialize OpenAI client (will be None if API key not set)
openai_client = AsyncOpenAI(api_key=settings.openai_api_key) if settings.openai_api_key else None


async def get_embedding(text: str) -> List[float]:
    """Generate embedding for text using OpenAI."""
    try:
        if openai_client is None:
            raise ValueError("OpenAI API key not configured. Please set OPENAI_API_KEY in .env file")
        
        response = await openai_client.embeddings.create(
            model=settings.embedding_model,
            input=text
        )
        return response.data[0].embedding
    except Exception as e:
        logger.error(f"Error generating embedding: {e}")
        raise


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """Calculate cosine similarity between two vectors."""
    vec1_array = np.array(vec1)
    vec2_array = np.array(vec2)
    
    dot_product = np.dot(vec1_array, vec2_array)
    norm1 = np.linalg.norm(vec1_array)
    norm2 = np.linalg.norm(vec2_array)
    
    if norm1 == 0 or norm2 == 0:
        return 0.0
    
    return float(dot_product / (norm1 * norm2))


async def retrieve_similar_test_cases(query: str, top_k: int = None) -> List[Dict[str, Any]]:
    """
    Retrieve similar test cases from MongoDB using vector similarity search.
    
    Args:
        query: Query text to find similar test cases
        top_k: Number of results to return (defaults to settings.top_k_results)
    
    Returns:
        List of similar test cases with similarity scores
    """
    try:
        if not db.is_connected():
            logger.warning("MongoDB not connected. RAG retrieval disabled. Returning empty results.")
            return []
        
        top_k = top_k or settings.top_k_results
        
        # Generate embedding for query
        query_embedding = await get_embedding(query)
        
        # Get test cases collection
        collection = db.get_test_cases_collection()
        
        # Retrieve all test cases (for local MongoDB, we'll do similarity calculation in Python)
        # For MongoDB Atlas, you would use $vectorSearch aggregation pipeline
        all_test_cases = await collection.find({}).to_list(length=1000)
        
        if not all_test_cases:
            logger.info("No test cases found in database")
            return []
        
        # Calculate similarity for each test case
        test_cases_with_similarity = []
        for test_case in all_test_cases:
            stored_embedding = test_case.get("embedding")
            if stored_embedding:
                similarity = cosine_similarity(query_embedding, stored_embedding)
                test_cases_with_similarity.append({
                    **test_case,
                    "similarity_score": similarity
                })
        
        # Sort by similarity and return top_k
        test_cases_with_similarity.sort(key=lambda x: x.get("similarity_score", 0), reverse=True)
        
        # Remove embedding from results (not needed in response)
        results = []
        for tc in test_cases_with_similarity[:top_k]:
            result = {k: v for k, v in tc.items() if k != "embedding"}
            results.append(result)
        
        logger.info(f"Retrieved {len(results)} similar test cases")
        return results
        
    except Exception as e:
        logger.error(f"Error retrieving similar test cases: {e}")
        return []


async def store_test_case(
    test_code: str,
    description: str,
    metadata: Optional[Dict[str, Any]] = None
) -> str:
    """
    Store a test case in MongoDB with vector embedding.
    
    Args:
        test_code: The test code to store
        description: Description of the test case
        metadata: Additional metadata (endpoint, model, etc.)
    
    Returns:
        ID of the stored test case
    """
    try:
        if not db.is_connected():
            raise RuntimeError(
                "MongoDB not connected. Cannot store test case. "
                "Please ensure MongoDB is running and MONGODB_URI is correctly configured."
            )
        
        # Generate embedding from test code and description
        text_for_embedding = f"{description}\n{test_code}"
        embedding = await get_embedding(text_for_embedding)
        
        # Prepare document
        document = {
            "test_code": test_code,
            "description": description,
            "embedding": embedding,
            "metadata": metadata or {},
            "created_at": None  # Will be set by MongoDB
        }
        
        # Insert into collection
        collection = db.get_test_cases_collection()
        result = await collection.insert_one(document)
        
        logger.info(f"Stored test case with ID: {result.inserted_id}")
        return str(result.inserted_id)
        
    except Exception as e:
        logger.error(f"Error storing test case: {e}")
        raise


async def get_test_case_by_id(test_case_id: str) -> Optional[Dict[str, Any]]:
    """Retrieve a test case by ID."""
    try:
        if not db.is_connected():
            raise RuntimeError(
                "MongoDB not connected. Cannot retrieve test case. "
                "Please ensure MongoDB is running and MONGODB_URI is correctly configured."
            )
        
        collection = db.get_test_cases_collection()
        test_case = await collection.find_one({"_id": ObjectId(test_case_id)})
        
        if test_case:
            # Remove embedding from result
            test_case = {k: v for k, v in test_case.items() if k != "embedding"}
            test_case["_id"] = str(test_case["_id"])
        
        return test_case
    except Exception as e:
        logger.error(f"Error retrieving test case: {e}")
        return None


async def get_all_test_cases(limit: int = 100) -> List[Dict[str, Any]]:
    """Retrieve all test cases (without embeddings)."""
    try:
        if not db.is_connected():
            logger.warning("MongoDB not connected. Returning empty list.")
            return []
        
        collection = db.get_test_cases_collection()
        test_cases = await collection.find({}).limit(limit).to_list(length=limit)
        
        # Remove embeddings and convert ObjectId to string
        results = []
        for tc in test_cases:
            result = {k: v for k, v in tc.items() if k != "embedding"}
            result["_id"] = str(result["_id"])
            results.append(result)
        
        return results
    except Exception as e:
        logger.error(f"Error retrieving all test cases: {e}")
        return []

