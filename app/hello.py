def print_messages(prefix, count):
    for i in range(1, count + 1):
        suffix = "" if i == 1 else f" {i}"
        try:
            print(f"{prefix}{suffix}")
        except IOError as e:
            import sys
            sys.stderr.write(f"Error writing to stdout: {e}\n")
            break

print_messages("Hello world", 3)

print_messages("Test PR 2", 4)