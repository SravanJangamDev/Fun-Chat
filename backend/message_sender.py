from uuid import uuid4
import json
import time


def create_unique_id() -> str:
    return str(uuid4())


messages = [
    {
        "topic": "bareja",
        "message": {"filename": "TWN00001", "bucket": "loan_application"},
    },
    {
        "topic": "karnataka",
        "message": {"filename": "TWN00001", "bucket": "loan_application"},
    },
]

basepath = "/tmp/pubsub/pub"

while True:
    for message in messages:
        filename = f"{basepath}/{create_unique_id()}.json"
        with open(filename, "w") as f:
            json.dump(message, f)

    time.sleep(2)
