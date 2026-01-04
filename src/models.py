"""Data models for recipe handling."""

from typing import List, Optional
from pydantic import BaseModel, Field


class Ingredient(BaseModel):
    """Represents a recipe ingredient."""

    quantity: Optional[str] = None
    unit: Optional[str] = None
    item: str
    preparation: Optional[str] = None

    def __str__(self) -> str:
        """Format ingredient as a string."""
        parts = []
        if self.quantity:
            parts.append(self.quantity)
        if self.unit:
            parts.append(self.unit)
        parts.append(self.item)
        if self.preparation:
            parts.append(f"({self.preparation})")
        return " ".join(parts)


class RecipeStep(BaseModel):
    """Represents a recipe instruction step."""

    step_number: int
    instruction: str
    duration: Optional[str] = None
    temperature: Optional[str] = None


class Recipe(BaseModel):
    """Represents a complete recipe."""

    title: str
    description: Optional[str] = None
    source_url: Optional[str] = None
    servings: Optional[str] = None
    prep_time: Optional[str] = None
    cook_time: Optional[str] = None
    total_time: Optional[str] = None

    ingredients: List[Ingredient] = Field(default_factory=list)
    steps: List[RecipeStep] = Field(default_factory=list)

    tags: List[str] = Field(default_factory=list)
    notes: Optional[str] = None
    author: Optional[str] = None


class OmnicookRecipe(BaseModel):
    """Recipe formatted specifically for Tokit Omnicook."""

    name: str
    description: Optional[str] = None
    servings: int = 4

    # Omnicook-specific fields
    ingredients: List[str] = Field(default_factory=list)
    steps: List[str] = Field(default_factory=list)

    # Cooking parameters
    total_time_minutes: Optional[int] = None
    difficulty: str = "Medium"  # Easy, Medium, Hard
    category: Optional[str] = None  # e.g., "Main Course", "Dessert"

    # Metadata
    source: Optional[str] = None
    notes: Optional[str] = None
