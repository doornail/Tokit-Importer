"""Claude AI-powered recipe converter for Tokit Omnicook."""

import json
from typing import Optional
from anthropic import Anthropic

from ..models import Recipe, OmnicookRecipe
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

        prompt = f"""You are a culinary expert assistant helping to convert recipes for the Tokit Omnicook, a smart cooking appliance similar to Thermomix.

Your task is to convert the following recipe into a format optimized for the Tokit Omnicook. The Omnicook can:
- Precisely control temperature and timing
- Mix, blend, chop, and steam ingredients
- Follow automated cooking programs
- Handle multi-step cooking processes

Please convert the recipe with these guidelines:

1. **Ingredients**:
   - List ingredients clearly with specific measurements
   - Convert to metric where appropriate
   - Group ingredients by when they're used if it helps clarity

2. **Steps**:
   - Break down into clear, sequential steps optimized for the Omnicook
   - Include specific temperatures and times where appropriate
   - Mention when to use specific Omnicook functions (mixing, heating, steaming, etc.)
   - Keep instructions concise but complete

3. **Timing**:
   - Calculate total cooking time in minutes

4. **Difficulty**:
   - Rate as Easy, Medium, or Hard based on complexity

5. **Category**:
   - Assign appropriate category (e.g., Main Course, Dessert, Appetizer, Soup, etc.)

{recipe_text}

Please respond with a JSON object in this exact format:
{{
  "name": "Recipe name",
  "description": "Brief description",
  "servings": 4,
  "ingredients": [
    "Specific measurement and ingredient",
    "..."
  ],
  "steps": [
    "Step 1 with specific instructions for Omnicook",
    "Step 2...",
    "..."
  ],
  "total_time_minutes": 45,
  "difficulty": "Medium",
  "category": "Main Course",
  "notes": "Any additional tips or notes"
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

            # Create OmnicookRecipe from parsed data
            return OmnicookRecipe(
                name=data.get('name', original_recipe.title),
                description=data.get('description'),
                servings=self._parse_servings(data.get('servings', 4)),
                ingredients=data.get('ingredients', []),
                steps=data.get('steps', []),
                total_time_minutes=data.get('total_time_minutes'),
                difficulty=data.get('difficulty', 'Medium'),
                category=data.get('category'),
                source=original_recipe.source_url,
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
        # Simple conversion without AI enhancement
        ingredients = [str(ing) for ing in recipe.ingredients]
        steps = [step.instruction for step in recipe.steps]

        # Try to parse servings
        servings = 4
        if recipe.servings:
            import re
            match = re.search(r'\d+', str(recipe.servings))
            if match:
                servings = int(match.group())

        # Estimate total time
        total_time_minutes = None
        if recipe.total_time:
            import re
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
