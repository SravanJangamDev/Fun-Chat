from database import DatabaseManager

USERNAME = "sravan"
PASSWORD = "Sravan123@"
HOST = "localhost"
PORT = 3306
DBNAME = "testdb"
debug_mode = False


db = DatabaseManager(
    username=USERNAME,
    password=PASSWORD,
    host=HOST,
    port=PORT,
    dbname=DBNAME,
    debug_mode=debug_mode,
)

# db.create_user(
#     "Jangam",
#     "sravan",
#     "8949284267",
#     "Sravan",
#     "jangamsravan@gmail.com",
#     "G928r93fejfhehr",
# )


user = db.get_user_by_id("8949284267")
user_id = user.user_id

print(f"{user.__dict__}")

# db.create_user(
#     "Bindu",
#     "Hima",
#     "8503358389",
#     "Bindu",
#     "bindu@gmail.com",
#     "G928r93fejfhehr",
# )

# db.create_user(
#     "Vinay",
#     "konda",
#     "8903358389",
#     "vinay",
#     "vinay@gmail.com",
#     "G928r93fejfhehr",
# )

# db.create_user_contact(user_id, "Bindu", "8503358389")
# db.create_user_contact(user_id, "Vinay", "8903358389")

user_contacts = db.get_user_contacts(user_id)

for contact in user_contacts:
    print(contact.__dict__)


# group = db.create_chat_group(
#     "funny boys", user_id, caption="Let's have fun together."
# )

# db.get_user_groups(user_id)
# print(group.__dict__)

db.create_user_group(1, user_id)
db.create_message("Hello Bindu", user_id, "8503358389")

messages = db.get_messages_of_two_users(user_id, "8503358389")
for message in messages:
    print(message.__dict__)
