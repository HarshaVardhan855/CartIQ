"""
CartIQ Common Product Schema and API Data Transfer Objects using Pydantic.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class ProductOffer(BaseModel):
    """
    Standardized marketplace offer schema. Every source must normalize to this model.
    """
    product_id: str = Field(description="Unique internal ID for product group association")
    name: str = Field(description="Normalized product name/title")
    brand: str = Field(default="Generic", description="Brand name")
    model: str = Field(default="", description="Model name or SKU")
    category: str = Field(default="General", description="Product category")
    price: float = Field(description="Current selling price")
    original_price: Optional[float] = Field(default=None, description="Original list price before discount")
    currency: str = Field(default="INR", description="Currency code (e.g. INR, USD)")
    discount: float = Field(default=0.0, description="Discount percentage")
    rating: float = Field(default=0.0, description="Product rating (0.0 to 5.0)")
    review_count: int = Field(default=0, description="Number of customer reviews")
    features: List[str] = Field(default_factory=list, description="List of feature specifications")
    availability: bool = Field(default=True, description="Stock availability status")
    marketplace: str = Field(description="Marketplace name (Amazon, Flipkart, Meesho, etc.)")
    product_url: str = Field(description="Direct URL to original product page")
    image_url: Optional[str] = Field(default=None, description="Product image URL")
    source_product_id: str = Field(description="Marketplace specific product identifier")
    last_updated: str = Field(default_factory=lambda: datetime.now().strftime("%d %b %Y, %I:%M %p"), description="Price retrieval timestamp")

class GroupedProduct(BaseModel):
    """
    Same Product -> Multiple Marketplace Offers.
    Groups identical physical/logical products across different marketplaces.
    """
    product_id: str
    canonical_name: str
    brand: str
    model: str
    category: str
    features: List[str] = Field(default_factory=list)
    image_url: Optional[str] = None
    offers: List[ProductOffer] = Field(default_factory=list)
    lowest_price: float = 0.0
    highest_price: float = 0.0
    price_difference: float = 0.0
    lowest_marketplace: str = ""
    available_offers_count: int = 0

class SearchQuery(BaseModel):
    """
    Search request payload.
    """
    query: str = Field(..., description="Natural language search query e.g. 'Earbuds under ₹1,000'")
    max_budget: Optional[float] = Field(default=None, description="Optional override budget")
    marketplace_filter: Optional[str] = Field(default="All", description="Marketplace filter")
    sort_by: Optional[str] = Field(default="Lowest Price", description="Sort option: Lowest Price, Highest Rating, Highest Discount")

class StructuredQueryExtraction(BaseModel):
    """
    LLM Query Understanding Output Schema.
    """
    category: str = Field(default="", description="Extracted category e.g. wireless earbuds")
    budget: Optional[float] = Field(default=None, description="Maximum budget value extracted")
    currency: str = Field(default="INR", description="Currency symbol/code")
    requirements: List[str] = Field(default_factory=list, description="Key features or requirements")
    provider_used: str = Field(default="gemini", description="AI provider used: gemini or groq")

class ComparisonRequest(BaseModel):
    """
    Request for detailed matrix comparison of selected product IDs.
    """
    product_ids: List[str] = Field(..., description="List of product IDs to compare")

class ComparisonResult(BaseModel):
    """
    Detailed comparison breakdown matrix.
    """
    products: List[GroupedProduct] = Field(default_factory=list)
    cheapest_product_id: Optional[str] = None
    highest_rated_product_id: Optional[str] = None
    summary: str = Field(default="", description="Factual comparison summary")

class AskRequest(BaseModel):
    """
    RAG AI Shopping Assistant Question payload.
    """
    query: str = Field(..., description="Shopping question e.g. 'Which earbuds have the best battery life?'")
    product_context: Optional[List[Dict[str, Any]]] = Field(default=None, description="Current retrieved search results")

class AskResponse(BaseModel):
    """
    RAG AI Shopping Assistant Answer response.
    """
    answer: str = Field(..., description="Grounded answer based strictly on retrieved CartIQ data")
    context_used_count: int = Field(default=0, description="Number of product listings used for answer")
    provider_used: str = Field(default="gemini", description="LLM provider used to generate response")

class EmailRequest(BaseModel):
    """
    Payload for emailing comparison results.
    """
    recipient_email: str = Field(..., description="User email address")
    search_query: str = Field(default="", description="Search query executed")
    products: List[GroupedProduct] = Field(default_factory=list, description="Grouped products to send")
