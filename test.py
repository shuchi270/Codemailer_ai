"""
Sample Python code for fallback analysis.

When no unread emails with code attachments are found, CodeMailer AI
falls back to analyzing this file as a demo.
"""


def fibonacci(n: int) -> list[int]:
    """Generate the first *n* Fibonacci numbers."""
    if n <= 0:
        return []

    sequence = [0, 1]
    while len(sequence) < n:
        sequence.append(sequence[-1] + sequence[-2])

    return sequence[:n]


def is_prime(num: int) -> bool:
    """Check whether *num* is a prime number."""
    if num < 2:
        return False
    for i in range(2, int(num**0.5) + 1):
        if num % i == 0:
            return False
    return True


if __name__ == "__main__":
    print("Fibonacci(10):", fibonacci(10))
    primes = [n for n in range(50) if is_prime(n)]
    print("Primes < 50:", primes)
