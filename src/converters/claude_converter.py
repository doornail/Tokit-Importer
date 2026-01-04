"""Claude AI-powered recipe converter for Tokit Omnicook."""

import json
from typing import Optional
from anthropic import Anthropic

from ..models import Recipe, OmnicookRecipe, OmnicookIngredient, OmnicookStep, OmnicookStepParameters
from ..config import config


class ClaudeConverter:
    """Converts recipes to Tokit Omnicook format using Claude AI."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        """Initialize the converter."""
        self.client = Anthropic(api_key=api_key or config.ANTHROPIC_API_KEY)
        self.model = model or config.CLAUDE_MODEL

    def convert(self, recipe: Recipe) -> OmnicookRecipe:
        """Convert a recipe to Omnicook format using Claude."""
        prompt = self._build_conversion_prompt(recipe)

        response = self.client.messages.create(
            model=self.model,
            max_tokens=4096,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.3  # Lower temperature for more consistent formatting
        )

        # Parse Claude's response
        response_text = response.content[0].text

        # Extract JSON from the response
        omnicook_recipe = self._parse_response(response_text, recipe)

        return omnicook_recipe

    def _build_conversion_prompt(self, recipe: Recipe) -> str:
        """Build the prompt for Claude to convert the recipe."""
        # Format the recipe data
        recipe_text = f"""
Recipe to Convert:

Title: {recipe.title}
{f'Description: {recipe.description}' if recipe.description else ''}
{f'Servings: {recipe.servings}' if recipe.servings else ''}
{f'Prep Time: {recipe.prep_time}' if recipe.prep_time else ''}
{f'Cook Time: {recipe.cook_time}' if recipe.cook_time else ''}
{f'Total Time: {recipe.total_time}' if recipe.total_time else ''}

Ingredients:
{self._format_ingredients(recipe)}

Instructions:
{self._format_steps(recipe)}

{f'Notes: {recipe.notes}' if recipe.notes else ''}
"""

        prompt = f"""You are a culinary expert assistant specialized in converting recipes for the Tokit Omnicook, a smart cooking appliance similar to Thermomix with precise control over temperature, timing, and blade speed.

TOKIT OMNICOOK CAPABILITIES:
- Temperature control: 0-120°C with heating element on/off
- Blade speed: 0-10 (in 0.5 increments)
  * Speed > 0 (forward/positive): CHOPPING, BLENDING, MIXING vigorously
  * Speed < 0 (reverse/negative): STIRRING gently without chopping
  * Speed 0: No blade movement (heating only, resting, etc.)
- Precise timing: Minutes and seconds
- Can heat, mix, chop, steam, and blend all in one bowl

{recipe_text}

CONVERSION REQUIREMENTS:

1. **INGREDIENTS** - Format as structured objects:
   - "name": ingredient name (e.g., "water", "onion", "flour")
   - "quantity": amount with unit (e.g., "200g", "2 cups", "1 tsp")
   - Use metric measurements when possible
   - Be specific and clear

2. **STEPS** - Each step MUST have:
   - "step_number": Sequential number (1, 2, 3...)
   - "description": Clear instruction for what to do
   - "parameters": Object containing ALL of these fields:
     * "duration_minutes": Integer 0+ (how many minutes for this step)
     * "duration_seconds": Integer 0-59 (additional seconds)
     * "temperature_on": Boolean (true = heating element ON, false = OFF)
     * "temperature_celsius": Integer 0-120 (target temperature, 0 if heating is off)
     * "speed": Float 0-10 in 0.5 increments (blade speed and direction)
       - Use positive speeds (0.5-10) for chopping, blending, mixing
       - Use NEGATIVE speeds (-0.5 to -10) for gentle stirring without chopping
       - Use 0 for no blade movement (pure heating, resting, etc.)

SPEED GUIDELINES:
- Stirring/mixing liquids gently: -1 to -3 (NEGATIVE = reverse)
- Sautéing (stir while heating): -2 to -4
- Simmering soups: -1 to -2
- Chopping vegetables: 3 to 5
- Blending smooth: 6 to 8
- Grinding/pulverizing: 9 to 10
- Just heating with no movement: 0

EXAMPLE STEP:
{{
  "step_number": 1,
  "description": "Sauté onions until translucent",
  "parameters": {{
    "duration_minutes": 5,
    "duration_seconds": 0,
    "temperature_on": true,
    "temperature_celsius": 100,
    "speed": -3.0
  }}
}}

CRITICAL:
- Every step MUST have ALL parameter fields
- Speed must be in 0.5 increments (0, 0.5, 1, 1.5, 2, etc.)
- Use NEGATIVE speed for stirring (reverse blade)
- Use POSITIVE speed for chopping/blending
- Break down manual steps into Omnicook-automated steps with specific parameters

Please respond with a JSON object in this EXACT format:
{{
  "name": "Recipe name",
  "description": "Brief description",
  "image_url": null,
  "servings": 4,
  "ingredients": [
    {{"name": "ingredient name", "quantity": "amount with unit"}},
    ...
  ],
  "steps": [
    {{
      "step_number": 1,
      "description": "Step instruction",
      "parameters": {{
        "duration_minutes": 0,
        "duration_seconds": 30,
        "temperature_on": false,
        "temperature_celsius": 0,
        "speed": 5.0
      }}
    }},
    ...
  ],
  "total_time_minutes": 45,
  "difficulty": "Medium",
  "category": "Main Course",
  "source": "{recipe.source_url if recipe.source_url else null}",
  "notes": "Any additional tips"
}}

Respond ONLY with the JSON object, no additional text."""

        return prompt

    def _format_ingredients(self, recipe: Recipe) -> str:
        """Format ingredients list for the prompt."""
        if not recipe.ingredients:
            return "(No ingredients listed)"

        lines = []
        for ing in recipe.ingredients:
            lines.append(f"- {str(ing)}")

        return "\n".join(lines)

    def _format_steps(self, recipe: Recipe) -> str:
        """Format cooking steps for the prompt."""
        if not recipe.steps:
            return "(No steps listed)"

        lines = []
        for step in recipe.steps:
            lines.append(f"{step.step_number}. {step.instruction}")

        return "\n".join(lines)

    def _parse_response(self, response_text: str, original_recipe: Recipe) -> OmnicookRecipe:
        """Parse Claude's JSON response into an OmnicookRecipe."""
        # Try to extract JSON from response
        try:
            # Look for JSON in the response
            json_start = response_text.find('{')
            json_end = response_text.rfind('}') + 1

            if json_start != -1 and json_end > json_start:
                json_str = response_text[json_start:json_end]
                data = json.loads(json_str)
            else:
                # If no JSON found, try parsing the whole response
                data = json.loads(response_text)

            # Parse ingredients
            ingredients = []
            for ing_data in data.get('ingredients', []):
                if isinstance(ing_data, dict):
                    ingredients.append(OmnicookIngredient(**ing_data))
                else:
                    # Fallback for old format
                    ingredients.append(OmnicookIngredient(name=str(ing_data), quantity="as needed"))

            # Parse steps
            steps = []
            for step_data in data.get('steps', []):
                if isinstance(step_data, dict) and 'parameters' in step_data:
                    # Ensure parameters is a dict
                    params_data = step_data['parameters']
                    parameters = OmnicookStepParameters(**params_data)

                    step = OmnicookStep(
                        step_number=step_data.get('step_number', len(steps) + 1),
                        description=step_data.get('description', ''),
                        parameters=parameters
                    )
                    steps.append(step)
                else:
                    # Fallback for old format or missing parameters
                    steps.append(OmnicookStep(
                        step_number=len(steps) + 1,
                        description=str(step_data) if isinstance(step_data, str) else step_data.get('description', ''),
                        parameters=OmnicookStepParameters()  # Default parameters
                    ))

            # Create OmnicookRecipe from parsed data
            return OmnicookRecipe(
                name=data.get('name', original_recipe.title),
                description=data.get('description'),
                image_url=data.get('image_url'),
                servings=self._parse_servings(data.get('servings', 4)),
                ingredients=ingredients,
                steps=steps,
                total_time_minutes=data.get('total_time_minutes'),
                difficulty=data.get('difficulty', 'Medium'),
                category=data.get('category'),
                source=data.get('source') or original_recipe.source_url,
                notes=data.get('notes')
            )

        except (json.JSONDecodeError, ValueError, KeyError) as e:
            # Fallback: create a basic conversion if parsing fails
            print(f"Warning: Failed to parse Claude response: {e}")
            print(f"Response was: {response_text[:500]}")

            return self._fallback_conversion(original_recipe)

    def _parse_servings(self, servings) -> int:
        """Parse servings to an integer."""
        if isinstance(servings, int):
            return servings

        if isinstance(servings, str):
            # Try to extract number from string like "4 servings"
            import re
            match = re.search(r'\d+', servings)
            if match:
                return int(match.group())

        return 4  # Default

    def _fallback_conversion(self, recipe: Recipe) -> OmnicookRecipe:
        """Create a basic conversion if Claude fails."""
        import re

        # Simple conversion without AI enhancement
        ingredients = [
            OmnicookIngredient(name=str(ing.item), quantity=f"{ing.quantity or ''} {ing.unit or ''}".strip() or "as needed")
            for ing in recipe.ingredients
        ]

        steps = [
            OmnicookStep(
                step_number=idx,
                description=step.instruction,
                parameters=OmnicookStepParameters()  # Default empty parameters
            )
            for idx, step in enumerate(recipe.steps, 1)
        ]

        # Try to parse servings
        servings = 4
        if recipe.servings:
            match = re.search(r'\d+', str(recipe.servings))
            if match:
                servings = int(match.group())

        # Estimate total time
        total_time_minutes = None
        if recipe.total_time:
            hours = re.search(r'(\d+)\s*hour', recipe.total_time)
            minutes = re.search(r'(\d+)\s*minute', recipe.total_time)

            total = 0
            if hours:
                total += int(hours.group(1)) * 60
            if minutes:
                total += int(minutes.group(1))

            if total > 0:
                total_time_minutes = total

        return OmnicookRecipe(
            name=recipe.title,
            description=recipe.description,
            servings=servings,
            ingredients=ingredients,
            steps=steps,
            total_time_minutes=total_time_minutes,
            difficulty="Medium",
            source=recipe.source_url,
            notes=recipe.notes
        )
