import asyncio
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import json
from typing import Union, Optional, List, Dict
from config import (
    PUBSUB_BASEDIR,
    PUBSUB_MAILBOX,
    PUBSUB_SUBDIR,
    PUBSUB_HOST,
    PUBSUB_PORT,
)
from helper import (
    create_folder,
    get_subfiles,
    read_file,
    create_file,
    TempException,
    log_info,
    log_issue,
    create_unique_id,
    ClientException,
    append_to_file,
    read_file_list,
    update_file,
)


class User:
    def __init__(
        self,
        user_id: str,
        displayname: str = "",
        displaypicture: str = "",
        contacts: list = [],
        groups: list = [],
    ):
        pass
        self.user_id = user_id
        self.displayname = displayname
        self.displaypicture = displaypicture
        self.contacts = contacts
        self.groups = groups
        self.connection: Optional[WebSocketServerProtocol] = None

    def details(self) -> dict:
        return {
            "user_id": self.user_id,
            "displayname": self.displayname,
            "displaypicture": self.displaypicture,
            "contacts": self.contacts,
            "groups": self.groups,
        }


users: Dict[str, User] = {}
"""
user:
 {
    "user_id": "",
    "displayname": "",
    "displaypicture": "",
    "contacts": [],
    "groups": [],
    "messages": "file"
}
"""


def is_registered_user(user_id: str) -> bool:
    if user_id in users:
        return True

    return False


def invalid_password(user_id: str, password: str) -> bool:
    # authenticate the user
    return False


async def send_message(client: WebSocketServerProtocol, message: dict = {}) -> None:
    await client.send(json.dumps(message))


async def get_messages(user_id: str, contacts: list = []) -> dict:
    global users
    data = {}
    messages = read_file_list(f"{PUBSUB_MAILBOX}/{user_id}.json")
    for message in messages:
        msg_to = message.get("msg_to")
        msg_from = message.get("msg_from")
        if msg_to != user_id:
            old = data.get(msg_to, [])
            old.append(message)
            data[msg_to] = old

        else:
            old = data.get(msg_from, [])
            old.append(message)
            data[msg_from] = old

    data.pop(user_id, None)
    return data


async def handle_incoming_requests_from_client(
    user_id: str, client: WebSocketServerProtocol
) -> None:
    global users
    async for message in client:
        for u_id, u in users.items():
            print(u_id, u.connection)

        user = users.get(user_id)
        if user is None:
            return

        try:
            req = json.loads(message)
            action = req.get("action", "").lower()
            if action == "add_contact":
                contacts = req.get("contacts", [])
                user.contacts.extend(contacts)
                update_file(f"{PUBSUB_SUBDIR}/{user_id}.json", user.details())
                await send_message(
                    client,
                    {
                        "action": action,
                        "status": "success",
                        "msg": "Contact Added",
                        "data": user.details(),
                    },
                )
            elif action == "message":
                text = req.get("message", "")
                msg_from = user_id
                msg_to = req.get("msg_to", "")
                data = {
                    "action": "message",
                    "message": text,
                    "msg_from": msg_from,
                    "msg_to": msg_to,
                    "msg_id": create_unique_id(),
                }
                append_to_file(f"{PUBSUB_MAILBOX}/{user_id}.json", data)
                append_to_file(f"{PUBSUB_MAILBOX}/{msg_to}.json", data)
                to_user = users.get(msg_to)
                if to_user is None:
                    continue

                conn = to_user.connection
                if conn:
                    await conn.send(json.dumps(data))
            elif action == "get_details":
                await client.send(
                    json.dumps(
                        {"action": action, "status": "success", "data": user.details()}
                    )
                )

            elif action == "get_chat":
                chat_contacts = req.get("contacts", [])
                messages = await get_messages(user_id, chat_contacts)
                await client.send(
                    json.dumps(
                        {"action": action, "status": "success", "data": messages}
                    )
                )
        except ConnectionClosedOK:
            break

        except Exception as e:
            await client.send(json.dumps({"status": "failed", "msg": str(e)}))
            log_issue("Something failed.", excp=e)


async def signup(user_id, password, displayname, displaypicture) -> User:
    user = User(user_id=user_id, displayname=displayname, displaypicture=displaypicture)
    details = user.details()
    details["password"] = password
    create_file(f"{PUBSUB_SUBDIR}/{user_id}.json", details)

    return user


async def login(user_id, password) -> User:
    global users
    if invalid_password(user_id, password):
        raise ClientException("Invalid credentials.")
    user = users.get(user_id)
    if not user:
        raise ClientException("Invalid credentials.")

    return user


async def handle_connection(websocket: WebSocketServerProtocol, path: str):
    global users
    status = "Success"
    msg = ""
    try:
        data = json.loads(await websocket.recv())
        print(data)
        action = data.get("action", "").lower()
        user_id = data.get("user_id", "")
        displayname = data.get("displayname", "")
        displaypicture = data.get("displaypicture", "")
        password = data.get("password", "")

        if action == "signup":
            user = await signup(user_id, password, displayname, displaypicture)
            user.connection = websocket
            msg = "Registered Successfully"
            users[user_id] = user

        elif action == "login":
            user = await login(user_id, password)
            user.connection = websocket
            msg = "Login successful."
            users[user_id] = user

        else:
            msg = "Invalid action."
            await websocket.send(
                json.dumps({"action": action, "status": status, "msg": msg})
            )
            return

        await websocket.send(
            json.dumps({"action": action, "status": status, "msg": msg})
        )
        await handle_incoming_requests_from_client(user_id, websocket)
    except ConnectionClosedOK:
        log_info(f"Connection closed gracefully: {websocket.remote_address}")
    except (TempException, ClientException) as e:
        status = "failed."
        msg = e.err_msg
    except Exception as e:
        log_issue("Error processing connection", excp=e)
        msg = "Something went Wrong."
    finally:
        await websocket.send(
            json.dumps({"action": "login", "status": status, "msg": msg})
        )
        await websocket.close()


# load current subscriptions
def load_subscriptions():
    global users
    files = get_subfiles(PUBSUB_SUBDIR)
    files = [f.replace(".json", "") for f in files]
    for file in files:
        data = {}
        try:
            data = read_file(f"{PUBSUB_SUBDIR}/{file}.json")
        except TempException:
            pass

        users[file] = User(
            user_id=data.get("user_id", ""),
            displayname=data.get("displayname", ""),
            displaypicture=data.get("displaypicture", ""),
            contacts=data.get("contacts", []),
            groups=data.get("groups", []),
        )


def initialize() -> None:
    create_folder(f"{PUBSUB_BASEDIR}")
    create_folder(f"{PUBSUB_MAILBOX}")
    create_folder(f"{PUBSUB_SUBDIR}")
    load_subscriptions()


async def main():
    initialize()

    # task to handle subscriptions from clients
    server = await websockets.serve(handle_connection, PUBSUB_HOST, PUBSUB_PORT)

    print(f"WebSocket server started on ws://{PUBSUB_HOST}:{PUBSUB_PORT}")
    # Keep the server running
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())


"""
reqtypes:
1. self sign up:
{
    "action": "signup",
    "user_id": "",
    "password": "",
    "displayname": "",
    "displaypicture": ""
}
2. login:
{
    "action": "login",
    "user-id": "",
    "password": ""
}
3. add user:
{
    "action": "add_contact",
    "contacts": [],
    "group": ""
}

4. send message:
{
    "action": "message",
    "type": "individual|group|",
    "message": "Hello sravan",
    "from": "vinay",
    "to": "groupname|person name",
    "timestamp": "",
    "message_id": "",
}

}
subscription table:
"user": {
    "user_id": "",
    "password": "",
    "displayname": "",
    "displaypicture": "",
    "contacts": [],
    "groups": [],
    "messages": "file"
}
"message": {
    "type": "individual|group|",
    "message": "Hello sravan",
    "from": "vinay",
    "to": "groupname|person name",
    "timestamp": "",
    "message_id": "",
}
"""


"""
{
    "action": "signup",
    "user_id": "sravan",
    "password": "sravan",
    "displayname": "sravan",
    "displaypicture": ""
}
{
    "action": "login",
    "user_id": "sravan",
    "password": "sravan"
}
{
    "action": "message",
   "msg_to": "vinay",
   "message": "hello Vinay"
}

{
    "action": "add_contact",
   "contacts": ["vinay"]
}

{
    "action": "get_details",
    "contacts": []
}

{
    "action": "get_chats",
    "contacts": []
}

"""
