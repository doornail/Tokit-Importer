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


class OmnicookIngredient(BaseModel):
    """Ingredient formatted for Tokit Omnicook."""

    name: str = Field(description="Ingredient name (e.g., 'water', 'flour')")
    quantity: str = Field(description="Quantity with unit (e.g., '100g', '2 cups', '1 tsp')")


class OmnicookStepParameters(BaseModel):
    """Parameters for a Tokit Omnicook cooking step."""

    duration_minutes: int = Field(default=0, ge=0, description="Duration in minutes")
    duration_seconds: int = Field(default=0, ge=0, lt=60, description="Duration in seconds (0-59)")
    temperature_on: bool = Field(default=False, description="Whether heating element is on")
    temperature_celsius: int = Field(default=0, ge=0, le=120, description="Temperature in Celsius (0-120)")
    speed: float = Field(default=0, ge=0, le=10, description="Blade speed 0-10 in 0.5 increments")

    def __init__(self, **data):
        """Validate that speed is in 0.5 increments."""
        super().__init__(**data)
        # Validate speed is in 0.5 increments
        if self.speed % 0.5 != 0:
            raise ValueError(f"Speed must be in 0.5 increments, got {self.speed}")


class OmnicookStep(BaseModel):
    """A cooking step for Tokit Omnicook."""

    step_number: int = Field(ge=1, description="Step number (1-indexed)")
    description: str = Field(description="Step description/instructions")
    parameters: OmnicookStepParameters = Field(description="Cooking parameters for this step")

    def format_for_display(self) -> str:
        """Format step for display."""
        params = self.parameters
        parts = [f"Step {self.step_number}: {self.description}"]

        # Duration
        if params.duration_minutes > 0 or params.duration_seconds > 0:
            time_str = f"{params.duration_minutes}:{params.duration_seconds:02d}"
            parts.append(f"Time: {time_str}")

        # Temperature
        if params.temperature_on:
            parts.append(f"Temp: {params.temperature_celsius}°C")
        else:
            parts.append("Temp: OFF")

        # Speed
        if params.speed > 0:
            direction = "reverse (stir)" if params.speed < 0 else "forward (chop)"
            parts.append(f"Speed: {abs(params.speed)} {direction}")
        else:
            parts.append("Speed: 0 (no mixing)")

        return " | ".join(parts)


class OmnicookRecipe(BaseModel):
    """Recipe formatted specifically for Tokit Omnicook."""

    name: str = Field(description="Recipe name")
    description: Optional[str] = Field(default=None, description="Recipe description")
    image_url: Optional[str] = Field(default=None, description="URL to recipe cover image")
    servings: int = Field(default=4, ge=1, description="Number of servings")

    # Ingredients - Tokit specific format
    ingredients: List[OmnicookIngredient] = Field(
        default_factory=list,
        description="List of ingredients with name and quantity"
    )

    # Steps - Tokit specific format with parameters
    steps: List[OmnicookStep] = Field(
        default_factory=list,
        description="List of cooking steps with detailed parameters"
    )

    # Metadata
    total_time_minutes: Optional[int] = Field(default=None, description="Total cooking time")
    difficulty: str = Field(default="Medium", description="Easy, Medium, or Hard")
    category: Optional[str] = Field(default=None, description="Recipe category")
    source: Optional[str] = Field(default=None, description="Original recipe URL")
    notes: Optional[str] = Field(default=None, description="Additional notes or tips")
