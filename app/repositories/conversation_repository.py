from pydantic_ai.messages import ModelMessage, ModelMessagesTypeAdapter
from pydantic_core import to_jsonable_python

from models.conversation import Conversation, Message


class ConversationRepository:
    @staticmethod
    async def create(title: str | None = None) -> Conversation:
        return await Conversation.create(title=title)

    @staticmethod
    async def get(conversation_id: str) -> Conversation | None:
        return await Conversation.filter(id=conversation_id).first()

    @staticmethod
    async def save_messages(conversation_id: str, messages: list[ModelMessage]) -> None:
        conversation = await Conversation.filter(id=conversation_id).first()
        if conversation is None:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        for msg in messages:
            data = to_jsonable_python(msg)
            kind = data.get("kind", "unknown")
            role = "user" if kind == "request" else "assistant"
            await Message.create(
                conversation=conversation,
                role=role,
                kind=kind,
                payload=data,
            )

    @staticmethod
    async def load_messages(conversation_id: str) -> list[ModelMessage]:
        conversation = await Conversation.filter(id=conversation_id).first()
        if conversation is None:
            raise ValueError(f"Conversation '{conversation_id}' not found.")

        db_messages = await Message.filter(conversation=conversation).order_by(
            "created_at"
        )
        raw = [msg.payload for msg in db_messages]
        return ModelMessagesTypeAdapter.validate_python(raw)

    @staticmethod
    async def list_all() -> list[Conversation]:
        return await Conversation.all().order_by("-updated_at")

    @staticmethod
    async def delete(conversation_id: str) -> None:
        conversation = await Conversation.filter(id=conversation_id).first()
        if conversation:
            await conversation.delete()
