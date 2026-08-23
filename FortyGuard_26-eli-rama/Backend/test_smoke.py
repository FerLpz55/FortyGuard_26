#!/usr/bin/env python3
"""Smoke test for OmniTherm API endpoints.

Runs a quick end-to-end test against a running API instance:
  register → login → me → create site → get sites → temperature latest
  → alerts summary → energy consumption → agent stub → health

Usage:
    python test_smoke.py [base_url]

Default base_url: http://localhost:8000
"""

import sys
import httpx
import uuid

BASE_URL = sys.argv[1] if len(sys.argv) > 1 else "http://localhost:8000"
API = f"{BASE_URL}/api/v1"

# Unique email to avoid conflicts on re-runs
TEST_EMAIL = f"smoke_{uuid.uuid4().hex[:8]}@test.com"
TEST_PASSWORD = "SecurePass123!"
TEST_NAME = "Smoke Tester"

passed = 0
failed = 0
errors: list[str] = []


def check(name: str, response: httpx.Response, expected_status: int) -> dict | None:
    global passed, failed
    status = response.status_code
    if status == expected_status:
        passed += 1
        print(f"  ✅ {name} → {status}")
        try:
            return response.json()
        except Exception:
            return None
    else:
        failed += 1
        detail = ""
        try:
            detail = response.text[:200]
        except Exception:
            pass
        errors.append(f"{name}: expected {expected_status}, got {status} — {detail}")
        print(f"  ❌ {name} → {status} (expected {expected_status})")
        print(f"     Detail: {detail}")
        return None


def main() -> None:
    global passed, failed
    print(f"\n🔥 OmniTherm API Smoke Test")
    print(f"   Target: {BASE_URL}\n")

    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # ── 1. Health ──
    print("─── Health ───")
    check("GET /health", client.get("/health"), 200)

    # ── 2. Register ──
    print("\n─── Auth: Register ───")
    data = check(
        "POST /auth/register",
        client.post(f"{API}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": TEST_NAME,
        }),
        201,
    )

    access_token = data.get("access_token") if data else None
    refresh_token = data.get("refresh_token") if data else None
    user_id = data.get("user", {}).get("id") if data else None

    if not access_token:
        print("\n⚠️  Cannot continue without access token. Aborting.")
        _print_summary()
        return

    headers = {"Authorization": f"Bearer {access_token}"}

    # ── 3. Duplicate register (should fail) ──
    print("\n─── Auth: Duplicate Register ───")
    check(
        "POST /auth/register (duplicate)",
        client.post(f"{API}/auth/register", json={
            "email": TEST_EMAIL,
            "password": TEST_PASSWORD,
            "full_name": TEST_NAME,
        }),
        409,
    )

    # ── 4. Login ──
    print("\n─── Auth: Login ───")
    login_data = check(
        "POST /auth/login",
        client.post(f"{API}/auth/login", data={
            "username": TEST_EMAIL,
            "password": TEST_PASSWORD,
        }),
        200,
    )
    if login_data and login_data.get("access_token"):
        access_token = login_data["access_token"]
        headers = {"Authorization": f"Bearer {access_token}"}

    # ── 5. Me ──
    print("\n─── Auth: Me ───")
    me_data = check("GET /auth/me", client.get(f"{API}/auth/me", headers=headers), 200)

    # ── 6. Refresh ──
    print("\n─── Auth: Refresh ───")
    if refresh_token:
        check(
            "POST /auth/refresh",
            client.post(f"{API}/auth/refresh", headers={"Authorization": f"Bearer {refresh_token}"}),
            200,
        )

    # ── 7. Create site ──
    print("\n─── Sites: Create ───")
    site_data = check(
        "POST /sites",
        client.post(f"{API}/sites", json={
            "name": "Smoke Test Warehouse",
            "address": "123 Test St, Miami, FL",
            "lat": 25.7617,
            "lon": -80.1918,
            "site_type": "warehouse",
            "metadata": {"heat_threshold_c": 35.0},
        }, headers=headers),
        201,
    )
    site_id = site_data.get("id") if site_data else None

    # ── 8. List sites ──
    print("\n─── Sites: List ───")
    check("GET /sites", client.get(f"{API}/sites", headers=headers), 200)

    if site_id:
        # ── 9. Get site ──
        print("\n─── Sites: Get ───")
        check(f"GET /sites/{site_id}", client.get(f"{API}/sites/{site_id}", headers=headers), 200)

        # ── 10. Update site ──
        print("\n─── Sites: Update ───")
        check(
            f"PATCH /sites/{site_id}",
            client.patch(f"{API}/sites/{site_id}", json={"name": "Updated Warehouse"}, headers=headers),
            200,
        )

        # ── 11. Temperature latest (may be empty, but endpoint should respond) ──
        print("\n─── Temperature ───")
        check(
            f"GET /sites/{site_id}/temperature/latest",
            client.get(f"{API}/sites/{site_id}/temperature/latest", headers=headers),
            200,  # or 404 if no readings
        )

        # ── 12. Temperature history ──
        check(
            f"GET /sites/{site_id}/temperature/history",
            client.get(f"{API}/sites/{site_id}/temperature/history", params={
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-12-31T23:59:59Z",
            }, headers=headers),
            200,
        )

        # ── 13. Temperature stats ──
        check(
            f"GET /sites/{site_id}/temperature/stats",
            client.get(f"{API}/sites/{site_id}/temperature/stats", params={
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-12-31T23:59:59Z",
            }, headers=headers),
            200,
        )

        # ── 14. Temperature forecast (stub → 501) ──
        check(
            f"GET /sites/{site_id}/temperature/forecast (stub)",
            client.get(f"{API}/sites/{site_id}/temperature/forecast", headers=headers),
            501,
        )

        # ── 15. Alerts ──
        print("\n─── Alerts ───")
        check(
            f"GET /sites/{site_id}/alerts",
            client.get(f"{API}/sites/{site_id}/alerts", headers=headers),
            200,
        )

        # ── 16. Alerts summary ──
        check(
            "GET /alerts/summary",
            client.get(f"{API}/alerts/summary", headers=headers),
            200,
        )

        # ── 17. Energy consumption POST ──
        print("\n─── Energy ───")
        check(
            f"POST /sites/{site_id}/energy/consumption",
            client.post(f"{API}/sites/{site_id}/energy/consumption", json={
                "kwh": 245.5,
                "cost_usd": 36.83,
                "recorded_at": "2026-08-20T00:00:00Z",
                "zone_id": "test_zone",
            }, headers=headers),
            201,
        )

        # ── 18. Energy consumption GET ──
        check(
            f"GET /sites/{site_id}/energy/consumption",
            client.get(f"{API}/sites/{site_id}/energy/consumption", params={
                "start": "2026-01-01T00:00:00Z",
                "end": "2026-12-31T23:59:59Z",
            }, headers=headers),
            200,
        )

        # ── 19. Waste analysis (stub → 501) ──
        check(
            f"GET /sites/{site_id}/energy/waste-analysis (stub)",
            client.get(f"{API}/sites/{site_id}/energy/waste-analysis", headers=headers),
            501,
        )

        # ── 20. Delete site ──
        print("\n─── Sites: Delete ───")
        check(f"DELETE /sites/{site_id}", client.delete(f"{API}/sites/{site_id}", headers=headers), 204)

    # ── 21. Agent stubs ──
    print("\n─── Agent (stubs) ───")
    check("POST /agent/chat (stub)", client.post(f"{API}/agent/chat", json={"message": "test"}, headers=headers), 501)
    check("POST /agent/execute (stub)", client.post(f"{API}/agent/execute", json={"action": "test"}, headers=headers), 501)
    check("GET /agent/status (stub)", client.get(f"{API}/agent/status", headers=headers), 501)

    # ── 22. Unauthorized access ──
    print("\n─── Security: Unauthorized ───")
    check("GET /sites (no token)", client.get(f"{API}/sites"), 401)
    check("GET /auth/me (no token)", client.get(f"{API}/auth/me"), 401)

    client.close()
    _print_summary()


def _print_summary() -> None:
    total = passed + failed
    print(f"\n{'='*50}")
    print(f"  Results: {passed}/{total} passed, {failed} failed")
    if errors:
        print(f"\n  Failures:")
        for e in errors:
            print(f"    • {e}")
    print(f"{'='*50}\n")
    sys.exit(1 if failed > 0 else 0)


if __name__ == "__main__":
    main()
