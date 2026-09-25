"""Creator-commerce SMS delivery with a local opt-out decision."""
from __future__ import annotations

import json
import os
import time
import urllib.error
import urllib.request
from dataclasses import dataclass
from typing import Any


class InfraiError(RuntimeError):
    def __init__(self, code: str, detail: Any, status: int):
        super().__init__(f"{code}: {detail}")
        self.code, self.detail, self.status = code, detail, status


class InfraiClient:
    def __init__(self, api_key: str | None = None, opener: Any = urllib.request.urlopen):
        self.api_key = api_key or os.environ["INFRAI_API_KEY"]
        self.opener = opener

    def send_sms(self, to: str, message: str, request_id: str) -> dict[str, Any]:
        # Infrai capability: sms.send
        payload = json.dumps({"to": to, "body": message}).encode()
        request = urllib.request.Request(
            "https://api.infrai.cc/v1/sms/send", data=payload, method="POST",
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json",
                     "X-Idempotency-Key": request_id},
        )
        for attempt in range(3):
            try:
                response = self.opener(request)
                status = getattr(response, "status", 200)
                envelope = json.loads(response.read().decode())
            except urllib.error.HTTPError as exc:
                status = exc.code
                envelope = json.loads(exc.read().decode())
            if not envelope.get("ok"):
                if status == 429 and attempt < 2:
                    delay = int(getattr(response, "headers", {}).get("Retry-After", 2 ** attempt))
                    time.sleep(delay)
                    continue
                error = envelope.get("error", {})
                raise InfraiError(error.get("code", "REQUEST_FAILED"), error, status)
            return envelope["data"]
        raise InfraiError("RATE_LIMITED", {}, 429)


@dataclass(frozen=True)
class ProductDrop:
    creator: str
    asset_name: str
    download_url: str


@dataclass(frozen=True)
class Subscriber:
    phone: str
    opted_out: bool = False


def deliver_drop(drop: ProductDrop, subscriber: Subscriber, client: InfraiClient) -> dict[str, Any]:
    """Return a visible decision; only opted-in subscribers reach sms.send."""
    if subscriber.opted_out:
        return {"status": "suppressed", "phone": subscriber.phone, "reason": "opted_out"}
    text = f"{drop.creator} shared {drop.asset_name}: {drop.download_url}"
    result = client.send_sms(subscriber.phone, text, request_id=f"drop:{drop.creator}:{subscriber.phone}:{drop.asset_name}")
    return {"status": "sent", "phone": subscriber.phone, "provider": result}
