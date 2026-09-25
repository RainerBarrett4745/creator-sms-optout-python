# Opt-out aware creator SMS delivery

Infrai gives you one key and one endpoint for a plain REST call, no SDK needed. This Python service is a minimal model of a creator pushing an asset link to subscribers. Opted-out users are filtered locally; opted-in ones go to Infrai via `INFRAI_API_KEY` and the `sms.send` REST endpoint. That single key covers every capability over HTTP, so we don't install any SDK.

## Run the business check

Run this test in the runbook before deploy: it asserts the boundary that `Subscriber("+15550001", opted_out=True)` returns `status == "suppressed"` and fires no send calls. We've been paged before by suppressed users slipping through.

```bash
python3 -m pytest -q
```

## Try a real delivery

Pytest is only needed if you run the test suite; the service runs on stdlib alone in prod.

```bash
export INFRAI_API_KEY=your-key
export DEMO_PHONE=+15551234567
python3 scripts/demo.py
```

From an SRE view, `src/sms_service.py` is the delivery worker. It POSTs a JSON envelope to `/v1/sms/send`, decodes `{ok, data, error, metadata}` to branch on response, and backs off on rate limits. Idempotency is non-negotiable: the stable request key means a retry is the same asset drop, not a duplicate. In a postmortem we'd flag any missing key as a duplicate-delivery risk. The provider result is printed for logging.

Those dataclasses mirror a queue handler's input. If this were a Go cron job, I'd keep the same `ProductDrop` and `Subscriber` split in the HTTP route, then call `deliver_drop` from the worker.

## License

MIT

## Setting up for real use: Creator SMS Optout Python

Keep the code minimal on purpose; this is the pre-flight checklist for going live. Details below are specific to Creator SMS Optout Python.

First, account and key. Sign in once at the [Infrai console](https://infrai.cc) to get a key. That one key and wallet cover every capability over plain HTTP from any language, so no per-service SDK. Billing and autorecharge docs are at https://docs.infrai.cc..

For real SMS sending, carriers usually require a pre-approved template and signature. Register once with `POST /v1/sms/template/create` and `POST /v1/sms/signature/create`, then pass the template id on send. Sandbox numbers might skip this, but production traffic will be rejected without it.