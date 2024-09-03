import datetime
import os

from dotenv import load_dotenv
from sqlalchemy import DateTime, BigInteger, Text, create_engine
from sqlalchemy.orm import DeclarativeBase, Mapped, Session, mapped_column

load_dotenv()


engine = create_engine(
    f"postgresql://{os.getenv('POSTGRES_USER')}:{os.getenv('POSTGRES_PASSWORD')}@db:{os.getenv('DB_PORT')}/{os.getenv('POSTGRES_DB')}",  # noqa: E501
    echo=True
)


class Base(DeclarativeBase):
    ...


class Conversation(Base):
    __tablename__ = "conversation"

    id: Mapped[int] = mapped_column(BigInteger(), primary_key=True, autoincrement=True)
    user_id: Mapped[int] = mapped_column(BigInteger())
    user_request: Mapped[str] = mapped_column(Text())
    bot_response: Mapped[str] = mapped_column(Text())
    log_ts: Mapped[datetime.datetime] = mapped_column(DateTime())

    def __repr__(self) -> str:
        return f"User(id={self.user_id}, request={self.user_request}, response={self.bot_response}"


def init_database():
    Base.metadata.create_all(engine)


def add_conversation(
    user_id: int,
    user_request: str,
    bot_response: str,
) -> None:
    with Session(engine) as session:
        print(f"user_id: {user_id}")
        print(f"user_request: {user_request}")
        print(f"bot_response: {bot_response}")
        conv = Conversation(
            user_id=user_id,
            user_request=user_request,
            bot_response=bot_response,
            log_ts=datetime.datetime.utcnow(),
        )
        session.add_all([conv])
        session.commit()
