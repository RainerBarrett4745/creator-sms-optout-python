from src.sms_service import ProductDrop, Subscriber, deliver_drop


class RecordingClient:
    def __init__(self):
        self.calls = []

    def send_sms(self, to, message, request_id):
        self.calls.append((to, message, request_id))
        return {"message_id": "msg_test"}


def test_opted_out_subscriber_is_suppressed_without_send():
    client = RecordingClient()
    drop = ProductDrop("Mina", "Studio pack", "https://example.test/download/pack")
    result = deliver_drop(drop, Subscriber("+15550001", opted_out=True), client)
    assert result == {"status": "suppressed", "phone": "+15550001", "reason": "opted_out"}
    assert client.calls == []

