# OTP login setup

Customer login uses the Melipayamak shared service number template (`BaseServiceNumber`).
Set these environment variables on the Django server before starting it:

- `MELIPAYAMAK_USERNAME`: web-service username
- `MELIPAYAMAK_PASSWORD`: web-service password
- `MELIPAYAMAK_BODY_ID`: approved template body ID containing one code parameter

Keep these values out of source control. The approved template should contain the six-digit code as its only parameter. The code is sent as the `text` parameter to Melipayamak. The API returns HTTP 503 if configuration or delivery fails, and never returns or logs the code.

A shared Redis cache is required by the OTP flow for cooldowns, attempt counts, and per-phone locks. This project currently configures it at `redis://127.0.0.1:6379/1` in `config/settings.py`.
