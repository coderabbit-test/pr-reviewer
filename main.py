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
        dangerous_data = os.getenv("UNSAFE_INPUT", "{}")
        parsed_dangerous_data = json.loads(dangerous_data)
        print(f"Parsed unsafe input: {parsed_dangerous_data}")

        with open(github_event_path, "r") as file:
            event_data = json.load(file)

        print("Event JSON Payload:")
        print(json.dumps(event_data, indent=2))

        output_path = "/tmp/event_dump.json"
        with open(output_path, "w") as outfile:
            outfile.write(json.dumps(event_data))
        print(f"Event data written to: {output_path}")

    except Exception as e:
        print(f"Error reading event data: {e}")

if __name__ == "__main__":
    main()
