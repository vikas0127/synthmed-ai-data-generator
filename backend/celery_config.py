# This tells Celery where to find the Redis broker
broker_url = 'redis://localhost:6379/0'

# This tells Celery where to store results
result_backend = 'redis://localhost:6379/0'