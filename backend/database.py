from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from urllib.parse import quote
from models import Base, UserContacts, UserGroups, Users, ChatGroups, Messages
from sqlalchemy.exc import SQLAlchemyError
from helper import TempException


class DatabaseManager:
    def __init__(
        self,
        username: str,
        password: str,
        host: str,
        port: int,
        dbname: str,
        debug_mode: bool = False,
    ):
        db_url = f"mysql+mysqlconnector://{username}:{quote(password)}@{host}:{port}/{dbname}"
        self.engine = create_engine(db_url, echo=debug_mode)
        Base.metadata.create_all(self.engine)
        Session = sessionmaker(bind=self.engine)
        self.session = Session()

    def create_user(
        self,
        firstname,
        lastname,
        phone_number,
        displayname,
        email,
        password,
        displaypicture=None,
        caption=None,
        status=None,
    ) -> Users:
        try:
            user = Users(
                user_id=phone_number,
                firstname=firstname,
                lastname=lastname,
                phone_number=phone_number,
                displayname=displayname,
                displaypicture=displaypicture,
                email=email,
                password=password,
                caption=caption,
                status=status,
            )
            self.session.add(user)
            self.session.commit()
            return user
        except SQLAlchemyError as e:
            raise TempException("Failed to create user.", excp=e)

    def create_user_contact(
        self,
        user_id: int,
        nickname: str,
        contact_number: str,
        status=None,
    ) -> UserContacts:
        try:
            user_contact = UserContacts(
                user_id=user_id,
                nickname=nickname,
                contact_number=contact_number,
                contact_of=contact_number,
                status=status,
            )
            self.session.add(user_contact)
            self.session.commit()

            return user_contact
        except SQLAlchemyError as e:
            raise TempException("Failed to create user contact.", excp=e)

    def create_chat_group(
        self,
        nickname: str,
        created_by: str,
        profile_image=None,
        caption=None,
        status=None,
    ) -> ChatGroups:
        try:
            group = ChatGroups(
                nickname=nickname,
                created_by=created_by,
                profile_image=profile_image,
                caption=caption,
                status=status,
            )
            self.session.add(group)
            self.session.commit()
            return group
        except SQLAlchemyError as e:
            raise TempException("Failed to create Chat group.", excp=e)

    def create_user_group(
        self,
        group_id: int,
        user_id: int,
        access_level=None,
        joined_on=None,
        status=None,
    ) -> UserGroups:
        try:
            user_group = UserGroups(
                group_id=group_id,
                user_id=user_id,
                access_level=access_level,
                joined_on=joined_on,
                status=status,
            )
            self.session.add(user_group)
            self.session.commit()
            return user_group
        except SQLAlchemyError as e:
            raise TempException("Failed to create User group.", excp=e)

    def create_message(
        self,
        message_text: str,
        sent_by: int,
        sent_to: int,
        message_media_filename=None,
        status=None,
    ) -> Messages:
        try:
            message = Messages(
                message_text=message_text,
                sent_by=sent_by,
                sent_to=sent_to,
                message_media_filename=message_media_filename,
                status=status,
            )
            self.session.add(message)
            self.session.commit()
            return message
        except SQLAlchemyError as e:
            raise TempException("Failed to create message", excp=e)

    def update_user(
        self,
        user_id,
        firstname=None,
        lastname=None,
        displayname=None,
        email=None,
        password=None,
        caption=None,
        status=None,
    ):
        try:
            user = self.get_user_by_id(user_id)
            if firstname:
                user.firstname = firstname

            if lastname:
                user.lastname = lastname

            if displayname:
                user.displayname = displayname

            if email:
                user.email = email

            if password:
                user.password = password

            if caption:
                user.caption = caption

            if status:
                user.status = status
            self.session.commit()
        except SQLAlchemyError as e:
            raise TempException("Update User failed.", excp=e)

    def update_user_contact(
        self,
    ):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def update_message(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def update_chat_group(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def update_user_group(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def deactivate_user(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def activate_user(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def block_user_contact(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def unblock_user_contact(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def delete_user_contact(self, user_id, contact_number):
        try:
            contact = self.get_user_contact(user_id, contact_number)
            self.session.delete(contact)
            self.session.commit()
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def add_user_to_group(self):
        try:
            pass
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def remove_user_from_group(self, user_id, group_id):
        try:
            user_group = self.get_user_group_by_id(user_id, group_id)
            self.session.delete(user_group)
            self.session.commit()
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def delete_group(self, group_id):
        try:
            group = self.get_chat_group_by_id(group_id=group_id)
            self.session.delete(group)
            self.session.commit()
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def delete_message(self, message_id):
        try:
            message = self.get_message_by_id(message_id)
            self.session.delete(message)
            self.session.commit()
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_all_users(self) -> list:
        try:
            users = self.session.query(Users).all()
            return users
        except SQLAlchemyError as e:
            raise TempException("Failed to get users", excp=e)

    def get_user_by_id(self, user_id) -> Users:
        try:
            user = self.session.query(Users).filter_by(user_id=user_id).first()

            return user
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_chat_group_by_id(self, group_id) -> ChatGroups:
        try:
            group = (
                self.session.query(ChatGroups)
                .filter_by(group_id=group_id)
                .first()
            )
            return group
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_message_by_id(self, message_id):
        try:
            message = (
                self.session.query(Messages)
                .filter_by(message_id=message_id)
                .first()
            )
            return message
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_user_group_by_id(self, user_id, group_id) -> UserGroups:
        try:
            user_group = (
                self.session.query(UserGroups)
                .where(user_id=user_id, group_id=group_id)
                .first()
            )
            return user_group
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_user_groups(self, user_id, group_id) -> list:
        try:
            user_groups = (
                self.session.query(UserGroups).filter(user_id == user_id).all()
            )
            return user_groups
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_user_contacts(self, user_id):
        try:
            contacts = (
                self.session.query(UserContacts)
                .filter_by(user_id=user_id)
                .all()
            )
            return contacts
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_user_contact(self, user_id, contact_number):
        try:
            contact = (
                self.session.query(UserContacts)
                .filter_by(user_id=user_id, contact_number=contact_number)
                .first()
            )
            return contact
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_group_memebers(self, group_id):
        try:
            members = (
                self.session.query(UserGroups)
                .filter_by(group_id=group_id)
                .all()
            )
            return members
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def get_messages_of_two_users(self, user1: str, user2: str):
        try:
            messages = (
                self.session.query(Messages)
                .filter(
                    Messages.sent_by.in_([user1, user2]),
                    Messages.sent_to.in_([user1, user2]),
                )
                .order_by(Messages.timestamp)
                .all()
            )
            return messages
        except SQLAlchemyError as e:
            raise TempException("", excp=e)

    def is_user_exists(self, user_id: str) -> bool:
        try:
            user = self.get_user_by_id(user_id)
            if user:
                return True
            return False
        except SQLAlchemyError as e:
            raise TempException("", excp=e)
