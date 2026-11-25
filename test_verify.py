"""Independent checks for this entry: determinism, gate validity, exact bytes.

Runs main.py twice, hashes /output/entry.txt after each run, and asserts the
gate conditions (UTF-8, 1 to 199 characters, not only whitespace) plus the
no-trailing-newline requirement. Prints "Match: True" only when every check
holds; otherwise it prints the failures and exits non-zero.
"""

import hashlib
import subprocess
import sys
import unicodedata

ENTRY = "/output/entry.txt"
MAIN = "main.py"
FAILURES = []


def digest():
    with open(ENTRY, "rb") as handle:
        return hashlib.sha256(handle.read()).hexdigest()


def check(label, condition, detail=""):
    if not condition:
        FAILURES.append(label + (": " + detail if detail else ""))


def run_once():
    result = subprocess.run(
        [sys.executable, MAIN],
        capture_output=True,
        text=True,
        timeout=60,
    )
    check("main.py exit code", result.returncode == 0, result.stderr.strip())
    return digest()


def main():
    first = run_once()
    second = run_once()
    check("hashes identical", first == second, first + " != " + second)

    with open(ENTRY, "rb") as handle:
        raw = handle.read()

    try:
        text = raw.decode("utf-8")
    except UnicodeDecodeError as exc:
        text = ""
        check("utf-8 decodable", False, str(exc))
    check("not empty", len(text) > 0)
    check("length 1-199", 1 <= len(text) <= 199, "length=" + str(len(text)))
    check("not only whitespace", text.strip() != "")
    check("no trailing newline", not text.endswith("\n") and not raw.endswith(b"\n"))
    check("no carriage return", "\r" not in text)
    check(
        "no control characters",
        all(unicodedata.category(ch)[0] != "C" for ch in text),
    )

    print("chars:", len(text))
    print("bytes:", len(raw))
    print("sha256:", first)
    if FAILURES:
        for failure in FAILURES:
            print("FAIL " + failure)
        print("Match: False")
        return 1
    print("Match: True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
