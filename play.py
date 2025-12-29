from app.tools import time_tools

x = time_tools.calculate_date_relative(base_date='2024-03-08', direction='past', unit='days', value=-20)
print(x)