import asyncio
import websockets
from websockets import WebSocketServerProtocol
from websockets.exceptions import ConnectionClosedOK
import json
from typing import Dict
from config import (
    MYSQL_PORT,
    MYSQL_USERNAME,
    MYSQL_DBNAME,
    MYSQL_HOST,
    MYSQL_PASSWORD,
    MYSQL_DEBUG_MODE,
    APP_HOST,
    APP_PORT,
)
from database import DatabaseManager
from models import Users, UserGroups, UserContacts, Messages, ChatGroups
from helper import TempException, log_info, log_issue, ClientException

db: DatabaseManager
clients: Dict[str, WebSocketServerProtocol] = {}


def is_invalid_password(actual_pwd: str, password: str) -> bool:
    print(actual_pwd, password)
    return actual_pwd != password


async def send_resp_to_client(
    client: WebSocketServerProtocol, resp: dict
) -> None:
    try:
        await client.send(json.dumps(resp))
    except Exception as e:
        log_info("Failed to send resp.", excp=e)
        # raise ClientException("Failed to send resp.", excp=e)


async def signup(req_body: dict) -> dict:
    firstname = req_body.get("firstname", "")
    lastname = req_body.get("lastname", "")
    displayname = req_body.get("displayname", "")
    phone_number = req_body.get("phone_number", "")
    displaypicture = req_body.get("displaypicture", "")
    email = req_body.get("email", "")
    caption = req_body.get("caption", "")
    password = req_body.get("password", "")
    # validates input data

    if db.is_user_exists(phone_number):
        raise ClientException("Account already created please do login.")

    user = db.create_user(
        firstname=firstname,
        lastname=lastname,
        phone_number=phone_number,
        displayname=displayname,
        displaypicture=displaypicture,
        password=password,
        email=email,
        caption=caption,
    )
    return user.details()


async def login(req_body: dict) -> dict:
    phone_number = req_body.get("phone_number")
    password = req_body.get("password")

    user = db.get_user_by_id(user_id=phone_number)
    if is_invalid_password(user.password, password):
        raise ClientException("Invalid password")

    return user.details()


async def get_user_details(user_id: str) -> dict:
    user = db.get_user_by_id(user_id)
    if not user:
        raise ClientException(f"User {user_id} not found")

    return user.details()


async def get_user_contacts_list(user_id: str) -> list:
    contacts = db.get_user_contacts(user_id=user_id)

    contacts = [c.details() for c in contacts]

    return contacts


async def get_users_chat(user_id: str, contact_number: str) -> list:
    messages = db.get_messages_of_two_users(user_id, contact_number)
    print(messages)

    messages = [m.details() for m in messages]

    return messages


async def add_contact(user_id, req_body: dict) -> dict:
    nickname = req_body.get("nickname", "")
    contact_number = req_body.get("contact_number", "")
    contact = db.create_user_contact(
        user_id, nickname=nickname, contact_number=contact_number
    )
    if not db.is_user_contact_exists(contact_number, user_id):
        db.create_user_contact(
            contact_number, nickname=contact_number, contact_number=user_id
        )
    return contact.details()


async def remove_contact(user_id, req_body: dict) -> None:
    contact_number = req_body.get("contact_number")
    db.delete_user_contact(user_id, contact_number)


async def handle_message(user_id, req_body: dict) -> None:
    global clients
    message_text = req_body.get("message_text")
    sent_to = req_body.get("sent_to")
    sent_by = user_id
    media_filename = req_body.get("message_media_filename")
    message = db.create_message(message_text, sent_by, sent_to, media_filename)

    data = {
        "status": 200,
        "action": "message",
        "msg": "sent successfully",
        "data": message.details(),
    }

    receiver = clients.get(sent_to)
    if receiver:
        await send_resp_to_client(receiver, data)

    return message.details()


async def handle_incoming_requests_from_client(
    user_id: str, client: WebSocketServerProtocol
) -> None:
    resp = {"status": 200, "msg": "", "data": {}}
    async for message in client:
        try:
            req_body = json.loads(message)
            print(req_body)
            action = req_body.get("action", "").lower()
            resp["action"] = action
            if action == "get_account_details":
                resp["data"] = await get_user_details(user_id)
                await send_resp_to_client(client, resp)

            elif action == "get_contacts":
                resp["data"] = await get_user_contacts_list(user_id)
                await send_resp_to_client(client, resp)

            elif action == "get_chat":
                contact_number = req_body.get("contact_number")
                resp["data"] = await get_users_chat(user_id, contact_number)
                await send_resp_to_client(client, resp)

            elif action == "add_contact":
                resp["msg"] = "Contact added successfully"
                resp["data"] = await add_contact(user_id, req_body)
                await send_resp_to_client(client, resp)

            elif action == "remove_contact":
                await remove_contact(user_id, req_body)
                resp["msg"] = "Contact deleted."
                await send_resp_to_client(client, resp)

            elif action == "block_contact":
                pass

            elif action == "create_group":
                pass

            elif action == "add_user_to_group":
                pass

            elif action == "message":
                resp["data"] = await handle_message(user_id, req_body)
                resp["msg"] = "message sent successfully"
                await send_resp_to_client(client, resp)
            else:
                resp["msg"] = "Invalid action"
                await send_resp_to_client(client, resp)

        except (TempException, ClientException) as e:
            resp["status"] = 400
            resp["msg"] = e.err_msg
            await send_resp_to_client(client, resp)

        except Exception as e:
            print(e)
            log_issue("Something went wrong", excp=e)
            resp["status"] = 500
            resp["msg"] = "Something went wrong"
            await send_resp_to_client(client, resp)


async def handle_connection(websocket: WebSocketServerProtocol, path: str):
    global clients
    resp = {"status": 200, "msg": "", "data": {}}
    try:
        req_body = json.loads(await websocket.recv())
        action = req_body.get("action", "").lower()
        resp["action"] = action
        if action == "signup":
            user = await signup(req_body)
            resp["msg"] = "Registered Successfully"
            resp["data"] = user
            user_id = user.get("user_id")
            clients[user_id] = websocket
            await send_resp_to_client(websocket, resp)
            await handle_incoming_requests_from_client(user_id, websocket)

        elif action == "login":
            user = await login(req_body)
            resp["msg"] = "Login successful."
            resp["data"] = user
            user_id = user.get("user_id")
            clients[user_id] = websocket
            await send_resp_to_client(websocket, resp)
            await handle_incoming_requests_from_client(user_id, websocket)

        elif action == "heartbeat":
            await send_resp_to_client(websocket, resp)

        else:
            resp["msg"] = "Invalid action"
            await send_resp_to_client(websocket, resp)
            return

    except ConnectionClosedOK:
        log_info(f"Connection closed gracefully: {websocket.remote_address}")
    except (TempException, ClientException) as e:
        resp["msg"] = e.err_msg
        resp["status"] = 400
        await send_resp_to_client(websocket, resp)
    except Exception as e:
        log_issue("Error processing connection", excp=e)
        resp["msg"] = "Something went wrong."
        resp["status"] = 500
        await send_resp_to_client(websocket, resp)
    finally:
        await websocket.close()


async def main():
    global db
    db = DatabaseManager(
        username=MYSQL_USERNAME,
        password=MYSQL_PASSWORD,
        host=MYSQL_HOST,
        port=MYSQL_PORT,
        dbname=MYSQL_DBNAME,
        debug_mode=MYSQL_DEBUG_MODE,
    )

    # task to handle subscriptions from clients
    server = await websockets.serve(handle_connection, APP_HOST, APP_PORT)

    print(f"WebSocket server started on ws://{APP_HOST}:{APP_PORT}")
    # Keep the server running
    await server.wait_closed()


if __name__ == "__main__":
    asyncio.run(main())


"""
actions:
1. signup

2. login

3. add contact

4. create group

5. send message

6. add user to group

7. delete user from group

8. delete contact or deactivate

9. deactivate user

10. get user into

11. get all user contacts

12. get contact chat or group chat

"""
"""
****** Actions ******:
signup: 
{
    "action": "signup",
    "phone_number": "",
    "firstname": "Jangam",
    "lastname": "Sravan",
    "displayname": "Sravan",
    "displaypicture": "https://image.png",
    "email": "",
    "caption": "",
    "password": "",
    "status": ""
}

login:
{
    "action": "login",
    "phone_number": "",
    "password": ""
}

get_account_details:
{
    "action": "get_account_details"
}

get_contacts:
{
    "action": "get_contacts"
}

add new contact:
{
    "action": "add_contact",
    "nickname": "",
    "contact_number": ""
}

remove contact:
{
    "action": "remove_contact",
    "contact_number": ""
}

messages:
{
    "action": "message",
    "message_text": "What are you doing?",
    "sent_to": ""
}
"""
