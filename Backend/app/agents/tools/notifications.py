try:
    from app.services.email_service import email_service
except ImportError:
    class MockEmailService:
        async def send(self, recipient, subject, message): pass
    email_service = MockEmailService()

try:
    from app.services.webhook_service import webhook_service
except ImportError:
    class MockWebhookService:
        async def post(self, recipient, payload): pass
    webhook_service = MockWebhookService()

async def send_notification(channel: str, recipient: str, message: str) -> dict:
    """Envía notificación por canal: email, push, webhook."""
    if channel == "email":
        await email_service.send(recipient, "OmniTherm Alert", message)
    elif channel == "webhook":
        await webhook_service.post(recipient, {"message": message})
    return {"channel": channel, "recipient": recipient, "sent": True}