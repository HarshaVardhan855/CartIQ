"""
RAG (Retrieval-Augmented Generation) Engine for CartIQ.
Integrates LangChain, ChromaDB, and ProviderManager for grounded product Q&A
and general shopping advisory (no live marketplace data required).
"""

from typing import List, Optional
from data.schemas import GroupedProduct, AskResponse
from ai.provider_manager import ProviderManager
from ai.prompts import RAG_QA_SYSTEM_PROMPT, GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT
from ai.embeddings import SimpleEmbeddingGenerator
from utils.logger import logger


class CartIQRAGEngine:
    """
    RAG Pipeline for product Q&A, requirement matching, and grounded shopping explanations.
    When no products are available, falls back to general shopping advisory mode.
    """

    def __init__(self, provider_manager: Optional[ProviderManager] = None):
        self.provider_manager = provider_manager or ProviderManager()
        self.embedder = SimpleEmbeddingGenerator()
        self._init_vectorstore()

    def _init_vectorstore(self):
        try:
            import chromadb
            # In-memory ephemeral ChromaDB client
            self.chroma_client = chromadb.Client()
            self.collection = self.chroma_client.create_collection(
                name="cartiq_products",
                metadata={"hnsw:space": "cosine"}
            )
            logger.info("ChromaDB vectorstore initialized successfully.")
        except Exception as e:
            logger.warning(f"ChromaDB initialization fallback: {e}")
            self.collection = None

    def index_products(self, products: List[GroupedProduct]):
        """
        Indexes grouped products and marketplace offers into ChromaDB vectorstore.
        """
        if not products or not self.collection:
            return

        documents = []
        metadatas = []
        ids = []

        for p_idx, prod in enumerate(products):
            offers_summary = ", ".join([f"{o.marketplace}: ₹{o.price}" for o in prod.offers])
            doc_text = (
                f"Product: {prod.canonical_name}\n"
                f"Brand: {prod.brand}\n"
                f"Category: {prod.category}\n"
                f"Lowest Price: ₹{prod.lowest_price} on {prod.lowest_marketplace}\n"
                f"Highest Price: ₹{prod.highest_price}\n"
                f"Offers: {offers_summary}\n"
                f"Features: {', '.join(prod.features)}\n"
            )
            documents.append(doc_text)
            metadatas.append({
                "product_id": prod.product_id,
                "brand": prod.brand,
                "lowest_price": prod.lowest_price,
                "canonical_name": prod.canonical_name
            })
            ids.append(f"doc_{prod.product_id}_{p_idx}")

        try:
            # Clear old and add new
            existing_ids = self.collection.get()["ids"]
            if existing_ids:
                self.collection.delete(ids=existing_ids)

            embeddings_list = [self.embedder.embed_text(d) for d in documents]
            self.collection.add(
                documents=documents,
                embeddings=embeddings_list,
                metadatas=metadatas,
                ids=ids
            )
            logger.info(f"Indexed {len(documents)} products into ChromaDB.")
        except Exception as e:
            logger.error(f"Error indexing into ChromaDB: {e}")

    def format_retrieved_context(self, products: List[GroupedProduct]) -> str:
        """
        Formats retrieved products cleanly into grounding prompt context.
        """
        context_blocks = []
        for p in products:
            offers_lines = []
            for o in p.offers:
                url_str = o.product_url if o.product_url else "Link unavailable"
                offers_lines.append(
                    f"  - Marketplace: {o.marketplace} | Price: ₹{o.price} | Rating: {o.rating} ⭐ | URL: {url_str}"
                )
            block = (
                f"PRODUCT: {p.canonical_name}\n"
                f"Brand: {p.brand} | Model: {p.model}\n"
                f"Lowest Retrieved Price: ₹{p.lowest_price} (on {p.lowest_marketplace})\n"
                f"Highest Retrieved Price: ₹{p.highest_price} | Price Difference: ₹{p.price_difference}\n"
                f"Offers:\n" + "\n".join(offers_lines) + "\n"
                f"Key Features: {', '.join(p.features)}\n"
            )
            context_blocks.append(block)
        return "\n----------------------------------------\n".join(context_blocks)

    def ask_question(
        self,
        question: str,
        products: List[GroupedProduct],
        simulate_gemini_failure: bool = False
    ) -> AskResponse:
        """
        Answers product Q&A using RAG + ProviderManager (Gemini -> Groq -> Rule Fallback).

        When products are available: uses grounded RAG mode (no fabrication allowed).
        When no products are available: uses general shopping advisory mode
        (provides general buying guidance; never fabricates live marketplace data).
        """
        if not products:
            # === GENERAL SHOPPING ADVISOR MODE ===
            # No live products — answer from general product knowledge only.
            # CRITICAL: Must never fabricate current prices, ratings, or availability.
            logger.info("[RAGEngine] No products in context — using General Shopping Advisor mode.")

            system_prompt = GENERAL_SHOPPING_ADVISOR_SYSTEM_PROMPT
            prompt = f"User Shopping Question: {question}"

            answer_text, provider_used = self.provider_manager.generate_text(
                prompt=prompt,
                system_prompt=system_prompt,
                simulate_gemini_failure=simulate_gemini_failure
            )

            return AskResponse(
                answer=answer_text,
                context_used_count=0,
                provider_used=provider_used
            )

        # === RAG GROUNDED MODE (products available) ===
        self.index_products(products)
        formatted_context = self.format_retrieved_context(products)
        system_prompt = RAG_QA_SYSTEM_PROMPT.format(context=formatted_context)
        prompt = f"User Shopping Question: {question}"

        answer_text, provider_used = self.provider_manager.generate_text(
            prompt=prompt,
            system_prompt=system_prompt,
            simulate_gemini_failure=simulate_gemini_failure
        )

        return AskResponse(
            answer=answer_text,
            context_used_count=len(products),
            provider_used=provider_used
        )
