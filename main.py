import os
import json
import sys
from typing import Optional, Any


def load_github_event(event_path: str) -> Optional[Any]:
    try:
        with open(event_path, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        print(f"❌ Event file not found: {event_path}")
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse JSON: {e}")
    except Exception as e:
        print(f"❌ Unexpected error reading event file: {e}")
    return None


def main():
    github_event_name = os.getenv("GITHUB_EVENT_NAME")
    github_event_path = os.getenv("GITHUB_EVENT_PATH")

    if not github_event_name:
        print("⚠️  GITHUB_EVENT_NAME not set.")
    else:
        print(f"📦 Received GitHub event: {github_event_name}")

    if not github_event_path:
        print("❌ GITHUB_EVENT_PATH not set. Cannot read event data.")
        sys.exit(1)

    event_data = load_github_event(github_event_path)
    if event_data is not None:
        print("📄 Event JSON Payload:")
        print(json.dumps(event_data, indent=2))
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
