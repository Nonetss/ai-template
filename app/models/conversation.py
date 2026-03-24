import uuid

from tortoise import fields
from tortoise.models import Model


class Conversation(Model):
    id = fields.CharField(pk=True, max_length=64, default=lambda: uuid.uuid7().hex)
    title = fields.TextField(null=True)
    created_at = fields.DatetimeField(auto_now_add=True)
    updated_at = fields.DatetimeField(auto_now=True)

    messages: fields.ReverseRelation["Message"]

    class Meta:
        table = "conversations"
        ordering = ["-updated_at"]


class Message(Model):
    id = fields.CharField(pk=True, max_length=64, default=lambda: uuid.uuid7().hex)
    conversation: fields.ForeignKeyRelation[Conversation] = fields.ForeignKeyField(
        "models.Conversation", related_name="messages", on_delete=fields.CASCADE
    )
    role = fields.CharField(max_length=32)  # user | assistant
    kind = fields.CharField(max_length=32)  # request | response
    payload = fields.JSONField()
    created_at = fields.DatetimeField(auto_now_add=True)

    class Meta:
        table = "messages"
        ordering = ["created_at"]
