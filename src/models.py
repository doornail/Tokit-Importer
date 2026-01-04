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

    mode: str = Field(default="Manual", description="Cooking mode: Manual, Stewing, Steam, Turbo, Mincing, Grinding, Chopping, Kneading, Weighing, or *NOT TOKIT*")
    temperature_celsius: Optional[int] = Field(default=None, ge=35, le=180, description="Temperature in Celsius (35-180°C), None if not applicable")
    speed: Optional[float] = Field(default=None, ge=0, le=10, description="Blade speed 0-10, None if not applicable")
    speed_reverse: bool = Field(default=False, description="True if using reverse speed for stirring")
    time_minutes: int = Field(default=0, ge=0, le=99, description="Duration in minutes (max 99 per step)")
    notes: Optional[str] = Field(default=None, description="Additional notes or instructions for this step")

    def __init__(self, **data):
        """Validate speed and parameters."""
        super().__init__(**data)
        # Validate speed is in 0.5 increments if provided
        if self.speed is not None and self.speed % 0.5 != 0:
            raise ValueError(f"Speed must be in 0.5 increments, got {self.speed}")
        # Warn if blending hot liquids at high speed
        if self.temperature_celsius and self.temperature_celsius > 60 and self.speed and self.speed > 4:
            import warnings
            warnings.warn("Warning: High speed (>4) with temperature >60°C is not recommended")


class OmnicookStep(BaseModel):
    """A cooking step for Tokit Omnicook."""

    step_number: int = Field(ge=1, description="Step number (1-indexed)")
    description: str = Field(description="Step description/instructions")
    parameters: OmnicookStepParameters = Field(description="Cooking parameters for this step")

    def format_for_display(self) -> str:
        """Format step for table display."""
        params = self.parameters

        # Mode
        mode = params.mode

        # Temperature
        temp = f"{params.temperature_celsius}°C" if params.temperature_celsius else "—"

        # Speed with reverse notation
        if params.speed is not None:
            speed_str = f"{params.speed}"
            if params.speed_reverse:
                speed_str += " (reverse)"
        else:
            speed_str = "—"

        # Time
        time_str = f"{params.time_minutes} min" if params.time_minutes > 0 else "—"

        # Notes
        notes = params.notes or ""

        return f"| {self.step_number} | {self.description} | {mode} | {temp} | {speed_str} | {time_str} | {notes} |"


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
