
import argparse
import getpass
import json
import os
import re
import subprocess
import sys

import keyring

sys.path.append(os.getcwd())

try:
    from titech_portal_kit.client import TitechPortal
    from titech_portal_kit.utils import TitechPortalMatrix
except ImportError:
    print("Error: Could not import titech_portal_kit. Please ensure you are running this script from the directory containing titech_portal_kit.")
    sys.exit(1)

VPN_HOST = "apm.nap.gsic.titech.ac.jp"
RP_HOST = "rp.nap.gsic.titech.ac.jp"
VPN_INDEX_URL = f"https://{VPN_HOST}/"
VPN_POLICY_URL = f"https://{VPN_HOST}/my.policy"
VPN_SERVICE_URL = f"https://{RP_HOST}/vpnaccess_apm/service/"
VPN_SIGNIN_URL = f"https://{RP_HOST}/vpnaccess_apm/signin"
USER_AGENT = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15"
KEYRING_SERVICE = "titech-f5vpn-login"


def _read_multiline_json(prompt: str) -> str:
    """Read potentially multi-line JSON input, accumulating lines until valid."""
    lines = [input(prompt).strip()]
    if not lines[0]:
        return ""
    while True:
        try:
            json.loads("\n".join(lines))
            return "\n".join(lines)
        except json.JSONDecodeError:
            try:
                lines.append(input())
            except EOFError:
                return "\n".join(lines)


def _parse_matrix(input_string: str):
    input_string = input_string.strip()
    if input_string.startswith("[") and input_string.endswith("]"):
        # input_string is a list
        # convert to dict
        matrix_map = {}
        for i, val in enumerate(json.loads(input_string)):
            matrix_map[f"{chr(ord('a') + i // 7)}{i % 7 + 1}"] = str(val)
        return matrix_map
    else:
        return {str(k): str(v) for k, v in json.loads(input_string).items()}


def set_credentials(matrix_map_file=None):
    username = input("Portal username: ").strip()
    password = getpass.getpass("Portal password: ")

    matrix_map = {}
    if matrix_map_file:
        with open(matrix_map_file, "r") as f:
            matrix_map = _parse_matrix(f.read())
    else:
        raw = _read_multiline_json("Matrix map JSON (empty to skip): ")
        if raw:
            matrix_map = _parse_matrix(raw)

    keyring.set_password(KEYRING_SERVICE, "username", username)
    keyring.set_password(KEYRING_SERVICE, "password", password)
    keyring.set_password(KEYRING_SERVICE, "matrix_map", json.dumps(matrix_map))
    print("Saved credentials to keyring.")

def get_credentials():
    username = keyring.get_password(KEYRING_SERVICE, "username")
    password = keyring.get_password(KEYRING_SERVICE, "password")
    matrix_map_raw = keyring.get_password(KEYRING_SERVICE, "matrix_map")

    if not username or not password:
        raise RuntimeError("Credentials not found in keyring. Run with --set-key to store them.")

    matrix_map = {}
    if matrix_map_raw:
        try:
            matrix_map = json.loads(matrix_map_raw)
        except json.JSONDecodeError:
            raise RuntimeError("matrix_map in keyring is invalid JSON. Re-run with --set-key.")

    return username, password, matrix_map

def run_f5vpn(session_id, host):
    script_dir = os.path.dirname(os.path.abspath(__file__))
    f5vpn_script = os.path.join(script_dir, "f5vpn-login.py")
    if not os.path.exists(f5vpn_script):
        print(f"Error: {f5vpn_script} not found.")
        return

    cmd = ["sudo", f5vpn_script, f"--sessionid={session_id}", host]
    print(f"Executing: {' '.join(cmd)}")
    try:
        subprocess.run(cmd, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error running f5vpn-login.py: {e}")
        sys.exit(1)
    except KeyboardInterrupt:
        print("\nExiting...")

def main():
    parser = argparse.ArgumentParser(description="Titech Portal + F5 VPN login")
    parser.add_argument("--set-key", action="store_true", help="Store credentials into keyring")
    parser.add_argument("--matrix-map-file", help="Path to JSON file for matrix_map (used with --set-key)")
    args = parser.parse_args()

    if args.set_key:
        try:
            set_credentials(matrix_map_file=args.matrix_map_file)
        except Exception as e:
            print(f"Failed to store credentials: {e}")
            sys.exit(1)
        return

    username, password, matrix_map = get_credentials()

    print("Logging into Titech Portal...")
    portal = TitechPortal(user_agent=USER_AGENT)
    try:
        portal.login(username, password, matrix_map)
        print("Portal Login Successful.")
    except Exception as e:
        print(f"Portal Login Failed: {e}")
        sys.exit(1)

    print("Starting VPN Login Flow...")

    session = portal.http_client.session
    session.headers.update({'User-Agent': USER_AGENT})

    print("--- Cookies after Portal Login ---")
    for cookie in session.cookies:
        print(f"{cookie.name}: {cookie.value} (Domain: {cookie.domain})")
    print("----------------------------------")

    try:
        print(f"Accessing {VPN_INDEX_URL}...")
        resp = session.get(VPN_INDEX_URL)
        content = resp.text

        print(f"Landed on: {resp.url}")

        mrh_session = session.cookies.get('MRHSession')

        if mrh_session and "userpass_key" not in resp.url:
             if "vdesk/webtop" in resp.url or "logout" in content:
                 print(f"Already logged in. MRHSession: {mrh_session}")
                 run_f5vpn(mrh_session, VPN_HOST)
                 return

    except Exception as e:
        print(f"Error accessing VPN index: {e}")
        print(content)
        sys.exit(1)

    client_data_match = re.search(r'name=client_data value="([^"]+)"', content)
    post_url_match = re.search(r'name=post_url value="([^"]+)"', content)
    
    if client_data_match and post_url_match:
        client_data = client_data_match.group(1)
        post_url = post_url_match.group(1)
        
        print("Redirecting to VPN Service...")
        service_url = "https://rp.nap.gsic.titech.ac.jp/vpnaccess_apm/service/"
        script_match = re.search(r'document\.external_data_post_cls\.action = unescape\("([^"]+)"\)', content)
        if script_match:
             service_url = script_match.group(1)

        data = {
            "client_data": client_data,
            "post_url": post_url
        }
        
        try:
            resp = session.post(service_url, data=data)
            content = resp.text
            print("Received VPN Auth Page.")
        except Exception as e:
            print(f"Error accessing VPN service: {e}")
            print(content)
            sys.exit(1)
            
        if "Password:" not in content:
            print("Warning: Unknown Auth Page format.")
        
        print("Submitting VPN Password...")
        signin_url = f"https://{RP_HOST}/vpnaccess_apm/signin"
        data = {"password": password}
        
        try:
            resp = session.post(signin_url, data=data)
            signin_resp = resp.text
            
            if signin_resp == '':
                print("VPN Signin Successful.")
            elif signin_resp == '0':
                print("VPN Signin Failed: Timeout")
                print(signin_resp)
                sys.exit(1)
            elif signin_resp == '1':
                print("VPN Signin Failed: Wrong Password")
                print(signin_resp)
                sys.exit(1)
            elif signin_resp == '2':
                print("VPN Signin Failed: Password Empty")
                print(signin_resp)
                sys.exit(1)
            else:
                print(f"VPN Signin Unknown Response: {signin_resp}")
                print(signin_resp)

        except Exception as e:
            print(f"Error signing in: {e}")
            sys.exit(1)
            
        username_match = re.search(r'name="username" value="([^"]+)"', content)
        form_username = username_match.group(1) if username_match else ""
        
        print("Finalizing Session...")
        data = {
            "username": form_username,
            "password": password_value 
        }
        
        try:
            resp = session.post(VPN_POLICY_URL, data=data)
            final_content = resp.text

            mrh_session = session.cookies.get('MRHSession')
            
            if mrh_session:
                print(f"Session Established. Session ID: {mrh_session}")
                run_f5vpn(mrh_session, VPN_HOST)
            else:
                print("Failed to get MRHSession.")
                print(final_content)

        except Exception as e:
            print(f"Error finalizing session: {e}")
            sys.exit(1)

    else:
        print("Could not find client_data or post_url in initial response.")
        print("--- Response Content Preview ---")
        print(content)
        print("--- End Preview ---")
        sys.exit(1)

if __name__ == "__main__":
    main()
