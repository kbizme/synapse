from langchain.tools import tool
from collections import Counter
from typing import Literal, List, Union
import numpy as np
import math



Number = Union[int, float]


@tool('scientific_calculator')
def scientific_calculator(
    operation: Literal[
        'add',
        'subtract',
        'multiply',
        'divide',
        'power',
        'sqrt',
        'log',
        'sin',
        'cos',
        'tan'
    ],
    operands: List[Number]) -> dict:
    """
    Perform a scientific or arithmetic calculation using explicit operations.

    Use this tool when the user asks for mathematical computation that requires
    precise numeric evaluation (e.g., square roots, powers, trigonometric functions,
    logarithms, or arithmetic).

    Args:
        operation: The mathematical operation to perform.
        operands: A list of numeric operands required for the operation.

    Returns:
        On success:
            { 'ok': true, 'data': { 'operation': str, 'operands': list, 'result': number } }
        On failure:
            { 'ok': false, 'error': str }
    """
    try:
        if not operands:
            return {'ok': False, 'error': 'Operands list cannot be empty.'}

        if operation == 'add':
            result = sum(operands)

        elif operation == 'subtract':
            if len(operands) != 2:
                return {'ok': False, 'error': 'Subtract requires exactly two operands.'}
            result = operands[0] - operands[1]

        elif operation == 'multiply':
            result = math.prod(operands)

        elif operation == 'divide':
            if len(operands) != 2:
                return {'ok': False, 'error': 'Divide requires exactly two operands.'}
            if operands[1] == 0:
                return {'ok': False, 'error': 'Division by zero is not allowed.'}
            result = operands[0] / operands[1]

        elif operation == 'power':
            if len(operands) != 2:
                return {'ok': False, 'error': 'Power requires exactly two operands.'}
            result = math.pow(operands[0], operands[1])

        elif operation == 'sqrt':
            if len(operands) != 1:
                return {'ok': False, 'error': 'Sqrt requires exactly one operand.'}
            if operands[0] < 0:
                return {'ok': False, 'error': 'Cannot compute square root of negative number.'}
            result = math.sqrt(operands[0])

        elif operation == 'log':
            if len(operands) not in (1, 2):
                return {'ok': False, 'error': 'Log requires one value and optional base.'}
            value = operands[0]
            base = operands[1] if len(operands) == 2 else math.e
            if value <= 0 or base <= 0:
                return {'ok': False, 'error': 'Logarithm arguments must be positive.'}
            result = math.log(value, base)

        elif operation == 'sin':
            if len(operands) != 1:
                return {'ok': False, 'error': 'Sin requires exactly one operand.'}
            result = math.sin(operands[0])

        elif operation == 'cos':
            if len(operands) != 1:
                return {'ok': False, 'error': 'Cos requires exactly one operand.'}
            result = math.cos(operands[0])

        elif operation == 'tan':
            if len(operands) != 1:
                return {'ok': False, 'error': 'Tan requires exactly one operand.'}
            result = math.tan(operands[0])

        else:
            return {'ok': False, 'error': f'Unsupported operation: {operation}'}

        return {
            'ok': True,
            'data': {
                'operation': operation,
                'operands': operands,
                'result': result
            }
        }

    except Exception as e:
        return {'ok': False, 'error': str(e)}



@tool('calculate_statistics')
def calculate_statistics(numbers: list) -> dict:
    """
    Compute descriptive statistics for a list of numeric values.

    Use this tool when the user provides a dataset and asks for:
    - summary statistics
    - mean, median, mode
    - spread or dispersion (std, variance, range, IQR)
    - percentiles or basic aggregations

    Args:
        numbers: A list of integers or floats.

    Returns:
        On success:
            {
              "ok": true,
              "data": {
                "central_tendency": {...},
                "dispersion": {...},
                "percentiles": {...},
                "aggregations": {...}
              }
            }
        On failure:
            { "ok": false, "error": "Reason for failure" }
    """
    try:
        if not numbers:
            return {'error': 'List is empty.'}
        
        nums = np.array(numbers)
        n = len(nums)
        
        # central Tendency
        mean = np.mean(nums)
        median = np.median(nums)
        # simple mode calculation using Counter
        data_counts = Counter(numbers)
        mode_val = data_counts.most_common(1)[0][0]

        # dispersion & range
        std = np.std(nums)
        var = np.var(nums)
        minimum = np.min(nums)
        maximum = np.max(nums)
        data_range = maximum - minimum
        
        # percentiles
        p10 = np.percentile(nums, 10)
        p25 = np.percentile(nums, 25)
        p75 = np.percentile(nums, 75)
        p90 = np.percentile(nums, 90)
        # interquartile Range
        iqr = p75 - p25
        
        processed_data =  {
            'central_tendency': {
                'mean': float(round(mean, 3)),
                'median': float(median),
                'mode': float(mode_val)
            },
            'dispersion': {
                'std': float(round(std, 3)),
                'var': float(round(var, 3)),
                'range': float(data_range),
                'iqr': float(iqr)
            },
            'percentiles': {
                'p10': float(p10),
                'p25': float(p25),
                'p75': float(p75),
                'p90': float(p90)
            },
            'aggregations': {
                'count': int(n),
                'sum': float(np.sum(nums)),
                'min': float(minimum),
                'max': float(maximum)
            }
        }
        return {'ok': True, 'data': processed_data}
    
    except Exception as e:
        return {'ok': False, 'error': str(e)}

