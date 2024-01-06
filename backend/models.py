from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, func
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class Users(Base):
    __tablename__ = "users"
    user_id = Column(String(10), primary_key=True)
    phone_number = Column(String(10), nullable=False, unique=True)
    firstname = Column(String(255), nullable=False)
    lastname = Column(String(255), nullable=False)
    displayname = Column(String(255), nullable=False)
    displaypicture = Column(String(255))
    email = Column(String(255), nullable=True)
    password = Column(String(255), nullable=False)
    caption = Column(String(255))
    status = Column(String(255))
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    def details(self) -> dict:
        return {
            "user_id": self.user_id,
            "phone_number": self.phone_number,
            "firstname": self.firstname,
            "lastname": self.lastname,
            "displayname": self.displayname,
            "displaypicture": self.displaypicture,
            "email": self.email,
            "caption": self.caption,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
            "status": self.status,
        }


# if possible delete contact
class UserContacts(Base):
    __tablename__ = "user_contacts"

    contact_id = Column(Integer, primary_key=True, autoincrement=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    nickname = Column(String(255), nullable=False)
    contact_number = Column(String(10), nullable=False)
    status = Column(String(255))
    contact_of = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    contact_list_user = relationship("Users", foreign_keys=[user_id])
    contact_of_user = relationship("Users", foreign_keys=[contact_of])

    def details(self) -> dict:
        return {
            "user_id": self.user_id,
            "contact_id": self.contact_id,
            "nickname": self.nickname,
            "contact_number": self.contact_number,
            "status": self.status,
            "contact_of": self.contact_of,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class ChatGroups(Base):
    __tablename__ = "chat_groups"

    group_id = Column(Integer, primary_key=True, autoincrement=True)
    nickname = Column(String(255), nullable=False)
    profile_image = Column(String(255))
    caption = Column(String(255))
    created_by = Column(String(10), ForeignKey("users.user_id"))
    status = Column(String(255))
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    def details(self) -> dict:
        return {
            "group_id": self.group_id,
            "nickname": self.nickname,
            "profile_image": self.profile_image,
            "caption": self.caption,
            "status": self.status,
            "created_by": self.created_by,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class UserGroups(Base):
    __tablename__ = "user_groups"

    group_id = Column(Integer, ForeignKey("chat_groups.group_id"), primary_key=True)
    user_id = Column(String(10), ForeignKey("users.user_id"), primary_key=True)
    access_level = Column(String(255))
    joined_on = Column(DateTime, default=func.now())
    status = Column(String(255))
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    def details(self) -> dict:
        return {
            "group_id": self.group_id,
            "user_id": self.user_id,
            "access_level": self.access_level,
            "joined_on": self.joined_on,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S"),
        }


class Messages(Base):
    __tablename__ = "messages"
    message_id = Column(Integer, primary_key=True, autoincrement=True)
    message_media_filename = Column(String(255))
    message_text = Column(String(255), nullable=False)
    # sent_by = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    # sent_to = Column(String(10), ForeignKey("users.user_id"), nullable=False)
    sent_by = Column(String(10), nullable=False)
    sent_to = Column(String(10), nullable=False)
    status = Column(String(255))
    timestamp = Column(DateTime, default=func.now(), onupdate=func.now())

    # sent_by_user = relationship("Users", foreign_keys=[sent_by])
    # sent_to_user = relationship("Users", foreign_keys=[sent_to])

    def details(self) -> dict:
        return {
            "message_id": self.message_id,
            "message_media_filename": self.message_media_filename,
            "message_text": self.message_text,
            "sent_by": self.sent_by,
            "sent_to": self.sent_to,
            "status": self.status,
            "timestamp": self.timestamp.strftime("%Y %b %d %I:%M %p"),
        }
