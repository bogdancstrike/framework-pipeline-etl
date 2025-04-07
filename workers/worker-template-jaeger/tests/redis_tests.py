import json
from framework.redis.redis_utils import *

redis_util = RedisUtils(host='127.0.0.1', port=6379, db=0, password='redis2024')

# Storing a simple string
redis_util.set_key('greeting', 'Hello, Redis!')
print(redis_util.get_key('greeting'))  # Output: Hello, Redis!

# Setting an initial value for an integer
redis_util.set_key('counter', 0)
# Increment the value
redis_util.increment_key('counter')
print(redis_util.get_key('counter'))  # Output: 1

# Adding elements to a list
redis_util.redis.lpush('my_list', 'item1')
redis_util.redis.lpush('my_list', 'item2')
redis_util.redis.lpush('my_list', 'item3')

# Retrieving all elements from the list
print(redis_util.redis.lrange('my_list', 0, -1))  # Output: ['item3', 'item2', 'item1']

# Storing a dictionary as a hash
user_data = {'name': 'Alice', 'age': '30', 'city': 'Wonderland'}
for key, value in user_data.items():
    redis_util.set_hash('user:1001', key, value)

# Retrieving the entire hash
print(redis_util.get_all_hash('user:1001'))  # Output: {'name': 'Alice', 'age': '30', 'city': 'Wonderland'}

# Storing a JSON object
user_profile = {'username': 'bob', 'email': 'bob@example.com', 'preferences': {'theme': 'dark'}}
redis_util.set_key('user:profile', json.dumps(user_profile))

# Retrieving and parsing the JSON object
profile_data = json.loads(redis_util.get_key('user:profile'))
print(profile_data)  # Output: {'username': 'bob', 'email': 'bob@example.com', 'preferences': {'theme': 'dark'}}

# Adding elements to a set
redis_util.redis.sadd('unique_items', 'apple', 'banana', 'orange')

# Checking membership
print(redis_util.redis.sismember('unique_items', 'banana'))  # Output: True

# Getting all members of the set
print(redis_util.redis.smembers('unique_items'))  # Output: {'apple', 'banana', 'orange'}

# Setting a key with a 10-second expiration
redis_util.set_key('temp_key', 'This is temporary', expire=10)
print(redis_util.get_key('temp_key'))  # Output: 'This is temporary'
# After 10 seconds, this key will no longer exist in Redis.

# List all keys
print(redis_util.list_all_keys())

# Check list lenght
redis_util.redis.lpush('my_list', 'item1')
redis_util.redis.lpush('my_list', 'item2')
redis_util.redis.lpush('my_list', 'item3')
print(redis_util.get_list_length('my_list'))  # Output: 3
