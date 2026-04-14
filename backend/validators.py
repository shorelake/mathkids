"""Math validators for verifying exercise correctness and animation data integrity."""
import re
from typing import Optional


def evaluate_expression(expr: str) -> Optional[int]:
    """Safely evaluate a simple arithmetic expression (only +, -, integers)."""
    expr = expr.replace(" ", "")
    if not re.match(r'^[\d+\-()]+$', expr):
        return None
    try:
        result = eval(expr, {"__builtins__": {}})
        return int(result)
    except:
        return None


def validate_exercise(expression: str, correct_answer: str, max_value: int = 20) -> dict:
    """Validate that an exercise is mathematically correct and within range."""
    errors = []

    computed = evaluate_expression(expression)
    if computed is None:
        errors.append(f"Invalid expression: {expression}")
    else:
        try:
            ans = int(correct_answer)
        except ValueError:
            errors.append(f"Answer must be an integer, got: {correct_answer}")
            return {"valid": False, "errors": errors}

        if computed != ans:
            errors.append(f"Wrong answer: {expression} = {computed}, not {ans}")

        # Extract all numbers from expression
        numbers = [int(n) for n in re.findall(r'\d+', expression)]
        if any(n > max_value for n in numbers):
            errors.append(f"Number exceeds max value {max_value}")
        if computed < 0:
            errors.append(f"Result is negative: {computed}")
        if computed > max_value:
            errors.append(f"Result exceeds max value {max_value}: {computed}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_make_ten_steps(steps: list, expression: str) -> dict:
    """Validate that make-ten animation steps are logically consistent."""
    errors = []
    # Basic structure check
    required_actions = {"show_objects", "split", "combine"}
    actions = {s.get("action") for s in steps}
    missing = required_actions - actions
    if missing:
        errors.append(f"Missing required actions: {missing}")

    # Check split parts sum correctly
    for step in steps:
        if step.get("action") == "split":
            parts = step.get("parts", [])
            if len(parts) == 2:
                total_in_expr = re.findall(r'\d+', expression)
                if len(total_in_expr) >= 2:
                    right = int(total_in_expr[1])
                    if sum(parts) != right:
                        errors.append(f"Split parts {parts} don't sum to {right}")

        if step.get("action") == "combine":
            values = step.get("values", [])
            result = step.get("result")
            if values and result and sum(values) != result:
                errors.append(f"Combine: {values} doesn't equal {result}")

    return {"valid": len(errors) == 0, "errors": errors}


def validate_animation_data(data: dict) -> dict:
    """Validate complete animation data structure."""
    errors = []

    if "expression" not in data:
        errors.append("Missing 'expression' field")
    if "methods" not in data or not isinstance(data.get("methods"), list):
        errors.append("Missing or invalid 'methods' field")
        return {"valid": False, "errors": errors}

    for i, method in enumerate(data["methods"]):
        if "type" not in method:
            errors.append(f"Method {i}: missing 'type'")
        if "steps" not in method or not method["steps"]:
            errors.append(f"Method {i}: missing or empty 'steps'")
        if method.get("type") == "make_ten":
            result = validate_make_ten_steps(method.get("steps", []), data.get("expression", ""))
            errors.extend(result["errors"])

    return {"valid": len(errors) == 0, "errors": errors}
