#!/usr/bin/env python3
"""
Script to discover and test Skaleet OAuth token endpoint
Tests multiple endpoint paths and auth methods to find working configuration
"""
import httpx
import json
import sys
from urllib.parse import urljoin

# Credentials from .env
BASE_URL = "https://tmb-testbed.tagpay.fr/api/v2/admin"
CLIENT_ID = "49a6ffc645229592edb9a4969a346043"
CLIENT_SECRET = "ab15a0da05a75b83e77d04198a0d6139eecc5fd07246f9a269853234e5afcbac"

# Candidate token endpoints to test
CANDIDATE_PATHS = [
    "/oauth/token",
    "/oauth2/token", 
    "/token",
    "/auth/token",
    "/api/token",
    "/api/oauth/token",
    "/api/v2/oauth/token",
    "/api/v2/token",
]

# Build full URLs
base_variants = [
    "https://tmb-testbed.tagpay.fr/api/v2/admin",
    "https://tmb-testbed.tagpay.fr/api/v2",
    "https://tmb-testbed.tagpay.fr/api",
    "https://tmb-testbed.tagpay.fr",
]

test_urls = []
for base in base_variants:
    for path in CANDIDATE_PATHS:
        url = base.rstrip('/') + path
        if url not in test_urls:
            test_urls.append(url)


def test_oauth_endpoint(url: str, method: str = "form") -> dict:
    """Test a single OAuth endpoint with specified method"""
    try:
        client = httpx.Client(timeout=10.0, follow_redirects=True)
        
        if method == "form":
            # Standard OAuth2 form body
            response = client.post(
                url,
                data={
                    "grant_type": "client_credentials",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "scope": "CardUpdate"
                },
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        elif method == "json":
            # JSON body
            response = client.post(
                url,
                json={
                    "grant_type": "client_credentials",
                    "client_id": CLIENT_ID,
                    "client_secret": CLIENT_SECRET,
                    "scope": "CardUpdate"
                },
                headers={"Content-Type": "application/json"}
            )
        elif method == "basic":
            # HTTP Basic auth
            response = client.post(
                url,
                data={"grant_type": "client_credentials", "scope": "CardUpdate"},
                auth=(CLIENT_ID, CLIENT_SECRET),
                headers={"Content-Type": "application/x-www-form-urlencoded"}
            )
        else:
            return {"error": "Unknown method"}
        
        result = {
            "url": url,
            "method": method,
            "status": response.status_code,
            "headers": dict(response.headers),
        }
        
        # Try to parse JSON response
        try:
            body = response.json()
            result["body"] = body
            # Check if we got a token
            if "access_token" in body:
                result["SUCCESS"] = True
                result["token_preview"] = body["access_token"][:50] + "..."
        except:
            result["body_text"] = response.text[:500]
        
        client.close()
        return result
        
    except Exception as e:
        return {"url": url, "method": method, "error": str(e)}


def main():
    print("=" * 80)
    print("SKALEET OAUTH TOKEN ENDPOINT DISCOVERY")
    print("=" * 80)
    print(f"Base URL: {BASE_URL}")
    print(f"Client ID: {CLIENT_ID[:20]}...")
    print(f"Testing {len(test_urls)} candidate URLs with 3 auth methods each")
    print("=" * 80)
    print()
    
    successful = []
    
    for url in test_urls:
        for method in ["form", "json", "basic"]:
            result = test_oauth_endpoint(url, method)
            
            status = result.get("status", "ERROR")
            if result.get("SUCCESS"):
                print(f"✅ SUCCESS: {url} (method={method})")
                print(f"   Status: {status}")
                print(f"   Token: {result.get('token_preview')}")
                successful.append(result)
            elif status in [200, 201]:
                print(f"⚠️  200 OK but no token: {url} (method={method})")
                print(f"   Body: {result.get('body', result.get('body_text', ''))[:200]}")
            elif status in [400, 401, 403]:
                print(f"🔒 Auth issue ({status}): {url} (method={method})")
            elif status == 404:
                # Skip 404s to reduce noise
                pass
            elif "error" in result:
                print(f"❌ Error: {url} (method={method}) - {result['error']}")
            else:
                print(f"❓ {status}: {url} (method={method})")
    
    print()
    print("=" * 80)
    if successful:
        print(f"✅ FOUND {len(successful)} WORKING CONFIGURATION(S):")
        for result in successful:
            print(f"   URL: {result['url']}")
            print(f"   Method: {result['method']}")
            print(f"   Token preview: {result.get('token_preview')}")
            print()
        
        # Save first successful config
        with open("/tmp/skaleet_oauth_config.json", "w") as f:
            json.dump(successful[0], f, indent=2)
        print(f"Config saved to: /tmp/skaleet_oauth_config.json")
        return 0
    else:
        print("❌ NO WORKING OAUTH ENDPOINT FOUND")
        print("Possible reasons:")
        print("  - Endpoint not publicly accessible (IP restriction, VPN required)")
        print("  - Invalid credentials")
        print("  - OAuth flow requires different parameters")
        print("  - Need to use a static token instead")
        return 1


if __name__ == "__main__":
    sys.exit(main())
