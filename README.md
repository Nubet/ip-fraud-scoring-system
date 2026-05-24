# IP Fraud Scoring System 

## Quick start

1. Install dependencies: `pip install -r requirements.txt`
2. Optional `.env` file:

```env
VALID_API_KEYS=dev-key,another-key
MAXMIND_DB_PATH=./GeoLite2-ASN.mmdb
VELOCITY_TTL_SECONDS=60
VELOCITY_MAX_SIZE=100000
VELOCITY_HIGH_THRESHOLD=10
```

3. Run server: `uvicorn app.main:app --reload`

## API

- `GET /v1/health`
- `GET /v1/score?ip=8.8.8.8` with `X-API-Key: dev-key`

## Testing stack

- `pytest` for test runner
- `pytest-asyncio` for async unit tests
- `fastapi.testclient` for integration tests

## What tests cover

- scoring rules and risk thresholds in `EvaluateIPUseCase`
- API key auth behavior (valid, invalid, inactive)
- API contract and HTTP mapping (401/403/422/200)
- in-memory adapters logic (velocity counter + TTL, API key parsing)
- MaxMind adapter decision logic (data center vs non-data-center)

## Run tests

- Quick run: `python run_tests.py`
- Full output: `python -m pytest`
- Unit only: `python -m pytest tests/unit -q`
- Integration only: `python -m pytest tests/integration -q`

## Project layout

- `app/domain` - entities and interfaces
- `app/usecases` - business logic
- `app/adapters` - framework and infrastructure code
- `app/config.py` - runtime settings
