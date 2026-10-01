import requests

NAVIGATION_SERVER = "http://127.0.0.1:5002"


def is_navigation_server_online():
    try:
        response = requests.get(
            f"{NAVIGATION_SERVER}/health",
            timeout=3
        )
        return response.status_code == 200
    except Exception:
        return False


def start_navigation(destination):
    try:
        response = requests.post(
            f"{NAVIGATION_SERVER}/start_navigation",
            json={
                "destination": destination
            },
            timeout=30
        )

        print(
            "Navigation response:",
            response.status_code,
            response.text
        )

        if response.status_code >= 400:
            return False

        data = response.json()

        return data.get("success", False)

    except Exception as error:
        print(
            "❌ Navigation error:",
            error
        )
        return False


def stop_navigation():
    try:
        response = requests.post(
            f"{NAVIGATION_SERVER}/stop_navigation",
            timeout=5
        )

        return response.status_code < 400

    except Exception as error:
        print(
            "⚠️ Stop navigation error:",
            error
        )
        return False


def get_navigation_status():
    try:
        response = requests.get(
            f"{NAVIGATION_SERVER}/last_summary",
            timeout=5
        )

        if response.status_code >= 400:
            return None

        return response.json()

    except Exception:
        return None


def get_next_instruction():
    try:
        response = requests.get(
            f"{NAVIGATION_SERVER}/next_instruction",
            timeout=5
        )

        if response.status_code >= 400:
            return None

        return response.json()

    except Exception:
        return None


def get_last_summary():
    try:
        response = requests.get(
            f"{NAVIGATION_SERVER}/last_summary",
            timeout=5
        )

        if response.status_code >= 400:
            return None

        return response.json()

    except Exception:
        return None