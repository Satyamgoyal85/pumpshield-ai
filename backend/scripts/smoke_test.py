"""Quick smoke test for PumpShield AI backend API."""

import sys

import httpx

BASE = "http://127.0.0.1:8001"
EMAIL = "smoke@pumpshield.dev"
PASSWORD = "smokepass123"


def main() -> int:
    client = httpx.Client(base_url=BASE, timeout=60.0)

    health = client.get("/health").json()
    assert health["status"] == "ok", health
    print("[OK] Health check")

    try:
        auth = client.post("/auth/register", json={"name": "Smoke", "email": EMAIL, "password": PASSWORD}).json()
    except httpx.HTTPStatusError:
        auth = client.post("/auth/login", json={"email": EMAIL, "password": PASSWORD}).json()

    token = auth["access_token"]
    headers = {"Authorization": f"Bearer {token}"}
    print(f"[OK] Auth ({auth['user']['email']})")

    analysis = client.post("/analysis", json={"symbol": "AAPL"}, headers=headers).json()
    assert 0 <= analysis["risk_score"] <= 100
    assert analysis["risk_level"] in ("green", "red")
    assert len(analysis["indicators"]) == 5
    assert analysis["explanation"]
    print(f"[OK] Analysis AAPL: score={analysis['risk_score']} level={analysis['risk_level']}")

    history = client.get("/analysis/history", headers=headers).json()
    assert history["total"] >= 1
    print(f"[OK] History: {history['total']} records")

    detail = client.get(f"/analysis/{analysis['id']}", headers=headers).json()
    assert detail["stock_symbol"] == "AAPL"
    print("[OK] Analysis detail")

    bad = client.post("/analysis", json={"symbol": "INVALIDXYZ123"}, headers=headers)
    assert bad.status_code == 404
    print("[OK] Invalid symbol returns 404")

    print("\nAll smoke tests passed.")
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except httpx.ConnectError:
        print("ERROR: Backend not running. Start with: uvicorn app.main:app --reload --port 8001", file=sys.stderr)
        raise SystemExit(1)
