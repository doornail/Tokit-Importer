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

        prompt = f"""You are a recipe conversion assistant specialized in adapting recipes for the Tokit Omnicook smart cooking machine.

## About the Tokit Omnicook

The Tokit Omnicook is a multifunctional cooking machine with the following specifications:

**Capabilities:**
- Temperature range: 35°C to 180°C (95°F to 356°F)
- Speed settings: 0-10 forward, 0-10 reverse (use reverse for gentle stirring while cooking)
- Mixing bowl capacity: 2.2 liters
- Built-in scale for weighing ingredients
- Timer: up to 99 minutes per step

**Available Modes:**
- Manual mode (set custom time, temp, speed)
- Stewing mode (for simmering, braising)
- Steam cooking mode (with simmering basket accessory)
- Turbo mode (high-speed blending/chopping)
- Mincing mode
- Grinding mode
- Chopping mode
- Kneading mode
- Weighing mode

**Key Limitations:**
- Cannot blend at high speed when contents are above 60°C (safety risk)
- Lid must remain on during cooking (measuring cup can be removed for steam release)
- Maximum 99 minutes per cooking step
- Not suitable for: deep frying, baking, boiling large quantities of pasta/noodles, grilling
- Blade is always present and spinning interferes with some cooking methods

**Best Practices:**
- Use reverse speed (1-2) when cooking with heat to gently stir without aggressive mixing
- Speed 0 = no stirring (heating only)
- For sautéing: 120-140°C, speed 1-2 reverse
- For simmering: 100°C, speed 1 reverse
- For blending hot liquids: cool below 60°C first, or use low speed (3-4) with brief pulses
- For chopping/mincing: no heat, speed 5-10 depending on desired texture

{recipe_text}

## Your Task

Convert the recipe above into Tokit Omnicook format.

**CRITICAL RULES:**
- Create a NEW step every time temperature OR speed changes
- Mark steps done outside the Tokit as mode "*NOT TOKIT*"
- If a technique cannot be replicated in the Tokit (e.g., charring, deep frying, baking), note it must be done externally or suggest an alternative adaptation
- Be realistic about what the Tokit can and cannot do
- Use reverse speed for gentle stirring when cooking
- Never exceed 99 minutes per step
- Never use high speed (>4) when temperature is above 60°C

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
      "description": "Action to perform (e.g., 'Chop onions', 'Sauté garlic')",
      "parameters": {{
        "mode": "Manual",
        "temperature_celsius": 130,
        "speed": 1.0,
        "speed_reverse": true,
        "time_minutes": 5,
        "notes": "Add what ingredients or any special instructions"
      }}
    }},
    {{
      "step_number": 2,
      "description": "Char peppers",
      "parameters": {{
        "mode": "*NOT TOKIT*",
        "temperature_celsius": null,
        "speed": null,
        "speed_reverse": false,
        "time_minutes": 0,
        "notes": "Char peppers on stovetop or under broiler until blackened"
      }}
    }},
    ...
  ],
  "total_time_minutes": 45,
  "difficulty": "Medium",
  "category": "Main Course",
  "source": "{recipe.source_url if recipe.source_url else None}",
  "notes": "Any additional tips"
}}

**Step Parameters Explanation:**
- `mode`: One of: Manual, Stewing, Steam, Turbo, Mincing, Grinding, Chopping, Kneading, Weighing, or "*NOT TOKIT*"
- `temperature_celsius`: 35-180, or null if not applicable
- `speed`: 0-10 in 0.5 increments, or null if not applicable
- `speed_reverse`: true for gentle stirring (reverse), false for chopping/blending (forward)
- `time_minutes`: 0-99 minutes per step
- `notes`: What to add or special instructions

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
