import requests
import time
import re

BASE_URL = "http://127.0.0.1:5000"
session = requests.Session()

print("\n===  SECURITY AUTOMATED TESTS STARTING  ===\n")

# -------------------------------------------------------------------------
# Helper to print results
# -------------------------------------------------------------------------
def result(title, ok, detail=""):
    status = "✔ SAFE" if ok else " VULNERABLE"
    print(f"[{status}] {title}")
    if detail:
        print(f"    → {detail}\n")
    else:
        print("")

# -------------------------------------------------------------------------
# Test 1 : SQL Injection (quick test)
# -------------------------------------------------------------------------
def test_sql_injection():
    print("=== TEST SQL INJECTION ===")
    payload = "' OR '1'='1"

    try:
        r = session.get(f"{BASE_URL}/notes/dashboard?q={payload}")
        if "error" in r.text.lower():
            result("SQL Injection", True, "The app returned an error but did NOT expose data — good.")
        elif len(r.text) > 20000:  # suspicious large output
            result("SQL Injection", False, "Output size suspiciously large → possible injection.")
        else:
            result("SQL Injection", True)
    except Exception as e:
        result("SQL Injection", False, str(e))

# -------------------------------------------------------------------------
# Test 2 : XSS Reflected
# -------------------------------------------------------------------------
def test_xss_reflected():
    print("=== TEST XSS REFLECTED ===")
    payload = "<img src=x onerror=alert('xss')>"
    r = session.get(f"{BASE_URL}/notes/dashboard?q={payload}")

    if payload in r.text:
        result("XSS Reflected", False, "Payload returned unescaped → vulnerable.")
    else:
        result("XSS Reflected", True)

# -------------------------------------------------------------------------
# Test 3 : CSRF — Test delete endpoint without token
# -------------------------------------------------------------------------
def test_csrf_delete():
    print("=== TEST CSRF ===")

    # try to delete note id 1 (non-destructive if not found)
    try:
        r = session.post(f"{BASE_URL}/notes/delete/1", allow_redirects=False)

        if r.status_code in [400, 403]:
            result("CSRF Protection", True, f"Server rejected request without token ({r.status_code}).")
        else:
            result("CSRF Protection", False,
                   f"Server accepted deletion without CSRF ({r.status_code}) → VULNERABLE.")
    except Exception as e:
        result("CSRF Protection", False, str(e))

#

# -------------------------------------------------------------------------
# Run all tests
# -------------------------------------------------------------------------
test_sql_injection()
test_xss_reflected()
test_csrf_delete()

print("\n===  SECURITY TESTS FINISHED ===")
