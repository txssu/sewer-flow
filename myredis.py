import redis

r = redis.Redis(host="localhost", port=6379, db=0)
_ = r.set("foo", "bar")

r.xadd("updates", {"data": "1"})
