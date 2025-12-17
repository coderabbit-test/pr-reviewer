import os
import json
import sys

def load_github_event():
    event_name = os.getenv("GITHUB_EVENT_NAME", "UNKNOWN_EVENT")
    event_path = os.getenv("GITHUB_EVENT_PATH")

    print(f"📦 Received GitHub event: {event_name}")

    if not event_path:
        print("⚠️  Environment variable GITHUB_EVENT_PATH is not set. Cannot read event data.")
        sys.exit(1)

    if not os.path.isfile(event_path):
        print(f"❌ Event file not found at: {event_path}")
        sys.exit(1)

    try:
        with open(event_path, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError as e:
        print(f"❌ Failed to parse event JSON: {e}")
    except Exception as e:
        print(f"❌ Unexpected error reading event file: {e}")
    
    sys.exit(1)

def main():
    event_data = load_github_event()
    print("✅ Event JSON Payload:")
    print(json.dumps(event_data, indent=2))

if __name__ == "__main__":
    main()
