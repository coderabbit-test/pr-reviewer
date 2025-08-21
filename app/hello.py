def print_messages(prefix, count):
    for i in range(1, count + 1):
        suffix = "" if i == 1 else f" {i}"
        print(f"{prefix}{suffix}")

print_messages("Hello world", 3)

print_messages("Test PR 2", 4)