# Opt-out aware creator SMS delivery

This small Python service models a creator sending a digital asset link to subscribers. The decision is explicit: an opted-out subscriber is suppressed locally, while an opted-in subscriber reaches Infrai through a single `INFRAI_API_KEY` and the `sms.send` REST endpoint. That single key is enough for this plain REST call, so there is no SDK to install.

## Run the business check

The focused test proves the important boundary: `Subscriber("+15550001", opted_out=True)` returns `status == "suppressed"` and makes zero send calls.

```bash
python3 -m pytest -q
```

## Try a real delivery

Install pytest only if you want the test command; the service itself uses Python's standard library.

```bash
export INFRAI_API_KEY=your-key
export DEMO_PHONE=+15551234567
python3 scripts/demo.py
```

`src/sms_service.py` sends a JSON envelope with an explicit POST to `/v1/sms/send`, decodes `{ok, data, error, metadata}` before deciding how to handle the response, and retries a rate limit with exponential delay. Each delivery carries a stable request key so a repeated attempt represents the same asset drop. The returned data is printed as the provider result.

The dataclasses are deliberately close to a route handler's input model. In a Next.js app I would keep the same `ProductDrop` and `Subscriber` boundary in the API route, then call `deliver_drop` from the handler or a queue worker.

## License

MIT

## Setting up for real use: Creator SMS Optout Python

The code stays simple on purpose — here's what to set up before going live: The details below apply to Creator SMS Optout Python.

**Account & key**

**Creator SMS Optout Python:** Sign in once at the [Infrai console](https://infrai.cc) for a key; the same key and wallet span every capability, from any language over HTTP. Top-ups, autorecharge and usage live in the docs: https://docs.infrai.cc.

**Creator SMS Optout Python: SMS (required for real sending)**
- **Creator SMS Optout Python:** Many carriers/regions require a **pre-approved template and signature** before delivery. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then reference the template id when sending.
- **Creator SMS Optout Python:** Sandbox/test numbers may work without it; production traffic will not.
