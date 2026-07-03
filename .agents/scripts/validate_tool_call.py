import sys
import json
import re

# Block list of destructive patterns (case-insensitive)
BLOCKED_PATTERNS = [
    r'rm\s+-rf',
    r'rm\s+-r\s+/',
    r'rmdir\s+/s\s+/q',
    r'del\s+/s\s+/q',
    r'format\s+[a-z]:',
    r'mkfs',
    r'dd\s+if=',
    r'drop\s+database',
]

def check_text(text: str) -> bool:
    for pattern in BLOCKED_PATTERNS:
        if re.search(pattern, text, re.IGNORECASE):
            return False
    return True

def main():
    try:
        raw_input = sys.stdin.read().strip()
        if not raw_input:
            sys.exit(0)

        # Check raw text first as a fallback
        if not check_text(raw_input):
            sys.stderr.write("Error: Destructive command execution blocked by PreToolUse hook!\n")
            sys.exit(2)

        # Parse as JSON to inspect specific fields
        try:
            data = json.loads(raw_input)

            # Helper to recursively check strings in JSON structure
            def check_val(val):
                if isinstance(val, str):
                    if not check_text(val):
                        return False
                elif isinstance(val, dict):
                    for k, v in val.items():
                        if not check_val(k) or not check_val(v):
                            return False
                elif isinstance(val, list):
                    for item in val:
                        if not check_val(item):
                            return False
                return True

            if not check_val(data):
                sys.stderr.write("Error: Destructive command execution blocked by PreToolUse hook!\n")
                sys.exit(2)

        except json.JSONDecodeError:
            pass

        sys.exit(0)

    except Exception as e:
        sys.stderr.write(f"Validator error: {e}\n")
        sys.exit(0)

if __name__ == "__main__":
    main()
