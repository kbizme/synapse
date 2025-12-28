import math



def scientific_calculator(expression: str) -> dict:
    """
    Evaluates mathematical expressions. 
    Supports both direct calls like 'sqrt(16)' and prefixed calls like 'math.sqrt(16)'.
    
    Args:
        expression: The math string to evaluate (e.g., 'sqrt(pi)' or 'math.pow(2, 3)')
    """
    try:
        # getting all functions from math module
        context = {k: v for k, v in math.__dict__.items() if not k.startswith("__")}
        
        # adding the 'math' module itself to the context
        context["math"] = math 
        
        # executing in a restricted environment
        result = eval(expression, {"__builtins__": {}}, context)
        
        return {
            "result": result,
            "status": "success"
        }
    except Exception as e:
        return {
            "error": str(e),
            "tip": "Ensure you use Python math syntax."
        }



x = scientific_calculator("factorial(100)")
print(x)