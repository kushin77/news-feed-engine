"""
ElevatedIQ News Feed Processor - Embedding Generator Module
Generates vector embeddings for semantic search using OpenAI
"""

from typing import List, Optional

import httpx
import structlog

from .config import get_api_key, get_settings

logger = structlog.get_logger(__name__)


class EmbeddingGenerator:
    """Generates text embeddings using OpenAI's embedding API"""

    def __init__(self):
        self.settings = get_settings()
        self.api_key = get_api_key("openai")
        self.model = self.settings.embedding_model
        self.dimension = 1536  # text-embedding-ada-002 dimension

    async def generate(self, text: str) -> Optional[List[float]]:
        """
        Generate embedding vector for text

        Args:
            text: The text to generate embeddings for

        Returns:
            List of floats representing the embedding vector, or None on error
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured, skipping embeddings")
            return None

        if not text or not text.strip():
            logger.warning("Empty text provided for embedding")
            return None

        try:
            # Truncate text to avoid token limits
            # (~8191 tokens for ada-002, ~4 chars per token = ~32k chars)
            text = text[:32000]

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": text,
                        "encoding_format": "float",
                    },
                    timeout=30.0,
                )

                response.raise_for_status()
                data = response.json()

                embedding = data["data"][0]["embedding"]

                logger.debug(
                    "Generated embedding", dimension=len(embedding), model=self.model
                )

                return embedding

        except httpx.HTTPStatusError as e:
            logger.error(
                "OpenAI API error",
                status_code=e.response.status_code,
                error=e.response.text,
            )
            return None
        except Exception as e:
            logger.error("Embedding generation failed", error=str(e))
            return None

    async def generate_batch(self, texts: List[str]) -> List[Optional[List[float]]]:
        """
        Generate embeddings for multiple texts

        Args:
            texts: List of texts to generate embeddings for

        Returns:
            List of embedding vectors (or None for failed items)
        """
        if not self.api_key:
            logger.warning("OpenAI API key not configured, skipping embeddings")
            result: List[Optional[List[float]]] = [None] * len(texts)
            return result

        if not texts:
            return []

        try:
            # Filter and truncate texts
            processed_texts = [(t[:32000] if t and t.strip() else "") for t in texts]

            # Filter out empty texts but track indices
            valid_indices = [i for i, t in enumerate(processed_texts) if t]
            valid_texts = [processed_texts[i] for i in valid_indices]

            if not valid_texts:
                empty_result: List[Optional[List[float]]] = [None] * len(texts)
                return empty_result

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    "https://api.openai.com/v1/embeddings",
                    headers={
                        "Authorization": f"Bearer {self.api_key}",
                        "Content-Type": "application/json",
                    },
                    json={
                        "model": self.model,
                        "input": valid_texts,
                        "encoding_format": "float",
                    },
                    timeout=60.0,
                )

                response.raise_for_status()
                data = response.json()

                # Map results back to original indices
                results: List[Optional[List[float]]] = [None] * len(texts)
                for item in data["data"]:
                    original_idx = valid_indices[item["index"]]
                    results[original_idx] = item["embedding"]

                logger.info(
                    "Generated batch embeddings",
                    total=len(texts),
                    successful=len(valid_texts),
                )

                return results

        except Exception as e:
            logger.error("Batch embedding generation failed", error=str(e))
            error_result: List[Optional[List[float]]] = [None] * len(texts)
            return error_result


class SimilaritySearch:
    """Utilities for embedding-based similarity search"""

    @staticmethod
    def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        if not vec1 or not vec2 or len(vec1) != len(vec2):
            return 0.0

        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = sum(a * a for a in vec1) ** 0.5
        norm2 = sum(b * b for b in vec2) ** 0.5

        if norm1 == 0 or norm2 == 0:
            return 0.0

        return dot_product / (norm1 * norm2)

    @staticmethod
    def find_most_similar(
        query_embedding: List[float],
        candidates: List[tuple],  # [(id, embedding), ...]
        top_k: int = 10,
        threshold: float = 0.7,
    ) -> List[tuple]:
        """
        Find most similar items to query embedding

        Args:
            query_embedding: The query vector
            candidates: List of (id, embedding) tuples
            top_k: Number of results to return
            threshold: Minimum similarity threshold

        Returns:
            List of (id, similarity_score) tuples, sorted by similarity
        """
        if not query_embedding or not candidates:
            return []

        similarities = []
        for item_id, embedding in candidates:
            if embedding:
                sim = SimilaritySearch.cosine_similarity(query_embedding, embedding)
                if sim >= threshold:
                    similarities.append((item_id, sim))

        # Sort by similarity descending
        similarities.sort(key=lambda x: x[1], reverse=True)

        return similarities[:top_k]
