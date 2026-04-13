"""
Sample Python code for fallback analysis.

When no unread emails with code attachments are found, CodeMailer AI
falls back to analyzing this file as a demo.

This module covers several common algorithmic and data-processing
problems to exercise the AI's problem-statement alignment and testing
parameter detection.
"""

from typing import Optional


# ── 1. Number Theory ─────────────────────────────────────────────

def fibonacci(n: int) -> list[int]:
    """Generate the first *n* Fibonacci numbers.

    Problem: Return a list of length *n* starting from 0.
    Edge cases: n <= 0, n == 1.
    """
    if n <= 0:
        return []
    if n == 1:
        return [0]

    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])
    return sequence[:n]


def is_prime(num: int) -> bool:
    """Check whether *num* is a prime number.

    Problem: Determine primality.
    Edge cases: num < 0, num == 0, num == 1, num == 2.
    """
    if num < 2:
        return False
    if num == 2:
        return True
    if num % 2 == 0:
        return False
    for i in range(3, int(num**0.5) + 1, 2):
        if num % i == 0:
            return False
    return True


# ── 2. String Processing ─────────────────────────────────────────

def count_words(text: str) -> dict[str, int]:
    """Count the frequency of each word in *text* (case-insensitive).

    Problem: Word-frequency histogram.
    Edge cases: empty string, punctuation, multiple spaces.
    """
    if not text or not text.strip():
        return {}
    words = text.lower().split()
    freq: dict[str, int] = {}
    for word in words:
        word = word.strip(".,!?;:\"'")
        if word:
            freq[word] = freq.get(word, 0) + 1
    return freq


def is_palindrome(s: str) -> bool:
    """Return True if *s* is a palindrome (ignoring case and spaces).

    Problem: Palindrome detection.
    Edge cases: empty string, single char, all spaces, mixed case.
    """
    cleaned = "".join(c.lower() for c in s if c.isalnum())
    return cleaned == cleaned[::-1]


# ── 3. Data Validation ───────────────────────────────────────────

def clamp(value: float, lo: float, hi: float) -> float:
    """Clamp *value* into [lo, hi].

    Problem: Bound a numeric value within a safe range.
    Edge cases: lo > hi (mis-ordered bounds), value == lo, value == hi.
    """
    if lo > hi:
        raise ValueError(f"lo ({lo}) must be <= hi ({hi})")
    return max(lo, min(value, hi))


def safe_divide(numerator: float, denominator: float) -> Optional[float]:
    """Divide two numbers, returning None on division by zero.

    Problem: Safe division without raising exceptions.
    Edge cases: denominator == 0, both zero, negative values.
    """
    if denominator == 0:
        return None
    return numerator / denominator


# ── 4. List Utilities ────────────────────────────────────────────

def flatten(nested: list) -> list:
    """Flatten an arbitrarily nested list into a single-level list.

    Problem: Recursive tree flattening.
    Edge cases: empty list, already flat, deeply nested, mixed types.
    """
    result = []
    for item in nested:
        if isinstance(item, list):
            result.extend(flatten(item))
        else:
            result.append(item)
    return result


# ── Entry point ──────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== Fibonacci ===")
    print("fibonacci(10):", fibonacci(10))
    print("fibonacci(0):", fibonacci(0))
    print("fibonacci(1):", fibonacci(1))

    print("\n=== Prime Detection ===")
    primes = [n for n in range(50) if is_prime(n)]
    print("Primes < 50:", primes)

    print("\n=== Word Count ===")
    print(count_words("the quick brown fox jumps over the lazy dog"))
    print(count_words(""))

    print("\n=== Palindrome ===")
    print(is_palindrome("A man a plan a canal Panama"))   # True
    print(is_palindrome("hello"))                         # False

    print("\n=== Clamp ===")
    print(clamp(15, 0, 10))   # 10
    print(clamp(-5, 0, 10))   # 0
    print(clamp(5, 0, 10))    # 5

    print("\n=== Safe Divide ===")
    print(safe_divide(10, 2))   # 5.0
    print(safe_divide(10, 0))   # None

    print("\n=== Flatten ===")
    print(flatten([1, [2, [3, 4]], [5, 6]]))   # [1, 2, 3, 4, 5, 6]

