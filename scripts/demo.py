import os

from src.sms_service import InfraiClient, ProductDrop, Subscriber, deliver_drop


def main() -> None:
    phone = os.environ.get("DEMO_PHONE")
    if not phone:
        raise SystemExit("Set DEMO_PHONE to run the live example")
    drop = ProductDrop("Mina", "Studio pack", "https://example.test/download/pack")
    print(deliver_drop(drop, Subscriber(phone), InfraiClient()))


if __name__ == "__main__":
    main()

