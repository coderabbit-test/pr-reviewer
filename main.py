import os
import json

def main():
    github_event_name = os.getenv("GITHUB_EVENT_NAME")
    github_event_path = os.getenv("GITHUB_EVENT_PATH")

    print(f"Received GitHub event: {github_event_name}")

    if not github_event_path:
        print("GITHUB_EVENT_PATH not set, cannot read event data.")
        return

    try:
        with open(github_event_path, "r") as file:
            event_data = json.load(file)
        print("Event JSON Payload:")
        print(json.dumps(event_data, indent=2))
    except Exception as e:
        print(f"Error reading event data: {e}")
