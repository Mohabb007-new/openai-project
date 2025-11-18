Fake mode: $env:FORCE_FAKE_OPENAI="1"; pytest (offline, no real API calls)

Real API mode: Remove-Item Env:FORCE_FAKE_OPENAI; pytest (uses key from .env)