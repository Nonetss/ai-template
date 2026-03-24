from pydantic_ai import ModelMessage, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python
from sqlalchemy import select
from models.conversation import Conversation
from utils.database import async_session


class ConversationRepository:
    @staticmethod
    async def create(title: str | None = None) -> Conversation:
        async with async_session() as session:
            conversation = Conversation(title=title)
            session.add(conversation)
            await session.commit()
            await session.refresh(conversation)
            return conversation

    @staticmethod
    async def get(conversation_id: str) -> Conversation | None:
        async with async_session() as session:
            return await session.get(Conversation, conversation_id)

    @staticmethod
    async def save_messages(conversation_id: str, messages: list[ModelMessage]) -> None:
        async with async_session() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation is None:
                raise ValueError(f"Conversation '{conversation_id}' not found.")
            data = to_jsonable_python(messages)
            import json

            conversation.messages_json = json.dumps(data)
            await session.commit()

    @staticmethod
    async def load_messages(conversation_id: str) -> list[ModelMessage]:
        async with async_session() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation is None:
                raise ValueError(f"Conversation '{conversation_id}' not found.")
            return ModelMessagesTypeAdapter.validate_json(conversation.messages_json)

    @staticmethod
    async def list_all() -> list[Conversation]:
        async with async_session() as session:
            result = await session.execute(
                select(Conversation).order_by(Conversation.updated_at.desc())
            )
            return list(result.scalars().all())

    @staticmethod
    async def delete(conversation_id: str) -> None:
        async with async_session() as session:
            conversation = await session.get(Conversation, conversation_id)
            if conversation:
                await session.delete(conversation)
                await session.commit()
