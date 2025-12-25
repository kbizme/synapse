from app.core import agents, memory

print('initial')
print(memory.get_messages())
print('-'*88)

# resp = agents.get_completion(prompt="Hello, how are you, I am Apex?")
resp = agents.get_completion(prompt="what is the top places to visit in the city paris?")
print(resp)
print('-'*88)
from pprint import pprint
print(memory.get_messages()[-1].content)

exit(5)


print('-'*88)
print('first')
print(memory.get_messages())

print('-'*88)
resp2 = agents.get_completion('What is the capital of France? and what is my name again please')
print('-'*88)
print('second')
print(memory.get_messages())


print('-'*88)
resp2 = agents.get_completion('glad you remenbered my name. what is the top places to visit in the city?')
print('-'*88)
print('second')
print(memory.get_messages())

# from app.core import config

# x = config.get_system_prompt('concise_assistant')
# print(x)