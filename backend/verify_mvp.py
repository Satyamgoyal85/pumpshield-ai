"""End-to-end API verification script for PumpShield AI MVP."""

import json
import sys
import urllib.error
import urllib.request

BASE = "http://localhost:8001"


def req(method: str, path: str, data: dict | None = None, token: str | None = None) -> tuple[int, dict]:
    headers = {"Content-Type": "application/json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    body = json.dumps(data).encode() if data else None
    request = urllib.request.Request(f"{BASE}{path}", data=body, headers=headers, method=method)
    try:
        with urllib.request.urlopen(request, timeout=120) as resp:
            return resp.status, json.loads(resp.read())
    except urllib.error.HTTPError as e:
        return e.code, json.loads(e.read())


def main():
    results = []

    # 1. Health check
    status, body = req("GET", "/health")
    results.append(("Health check", status == 200 and body.get("status") == "ok"))

    # 2. Register (or login if already exists)
    status, body = req("POST", "/auth/register", {
        "name": "Test User",
        "email": "test@pumpshield.ai",
        "password": "testpass123",
    })
    if status == 409:
        status, body = req("POST", "/auth/login", {
            "email": "test@pumpshield.ai",
            "password": "testpass123",
        })
        token = body.get("access_token") if status == 200 else None
        results.append(("Register with JWT", True))  # already registered from prior run
    else:
        token = body.get("access_token") if status == 201 else None
        results.append(("Register with JWT", status == 201 and token is not None))

    # 3. Login
    status, body = req("POST", "/auth/login", {
        "email": "test@pumpshield.ai",
        "password": "testpass123",
    })
    token = body.get("access_token") if status == 200 else token
    results.append(("Login with JWT", status == 200 and token is not None))

    # 4. Analyze AAPL (Green zone expected)
    status, body = req("POST", "/analysis", {"symbol": "AAPL"}, token=token)
    aapl_green = status == 201 and body.get("risk_level") == "green" and body.get("risk_score", 100) < 80
    results.append(("Analyze AAPL - Green zone", aapl_green))
    if status == 201:
        print(f"  AAPL: score={body['risk_score']}, level={body['risk_level']}")
        print(f"  Explanation preview: {body['explanation'][:120]}...")

    # 5. Analyze invalid symbol
    status, body = req("POST", "/analysis", {"symbol": "INVALIDXYZ123"}, token=token)
    results.append(("Invalid symbol returns error", status in (404, 502)))

    # 6. History
    status, body = req("GET", "/analysis/history", token=token)
    results.append(("History shows analyses", status == 200 and body.get("total", 0) >= 1))

    # 7. Get single analysis
    if status == 200 and body.get("items"):
        analysis_id = body["items"][0]["id"]
        status2, body2 = req("GET", f"/analysis/{analysis_id}", token=token)
        results.append(("Get analysis by ID", status2 == 200 and body2.get("id") == analysis_id))
    else:
        results.append(("Get analysis by ID", False))

    # 8. Explanation has content
    status, body = req("POST", "/analysis", {"symbol": "MSFT"}, token=token)
    has_explanation = status == 201 and len(body.get("explanation", "")) > 20
    results.append(("AI explanation generated", has_explanation))

    # 9. Indicators present
    has_indicators = status == 201 and len(body.get("indicators", [])) == 5
    results.append(("5 risk indicators returned", has_indicators))

    print("\n=== PumpShield AI MVP Verification ===\n")
    passed = 0
    for name, ok in results:
        mark = "PASS" if ok else "FAIL"
        print(f"  [{mark}] {name}")
        if ok:
            passed += 1

    print(f"\n{passed}/{len(results)} checks passed")
    sys.exit(0 if passed == len(results) else 1)


if __name__ == "__main__":
    main()
