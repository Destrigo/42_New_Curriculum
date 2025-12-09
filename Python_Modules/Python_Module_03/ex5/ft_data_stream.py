if __name__ == "__main__":
    """first try"""
    print("=== Game Data Stream Processor ===")
    print("Processing 1000 game events...")

    def game_events(n):
        players = ["alice", "bob", "charlie", "dave"]
        for i in range(1, n + 1):
            player = players[i % len(players)]
            level = (i * 3) % 20 + 1
            if i % 10 == 0:
                yield f"Event {i}: Player {player} (level {level}) found "
                "treasure"
            elif i % 7 == 0:
                yield f"Event {i}: Player {player} (level {level}) "
                "leveled up"
            else:
                yield f"Event {i}: Player {player} (level {level}) "
                "killed monster"

    total_events = 0
    high_level = 0
    treasure_events = 0
    level_up_events = 0
    for event in game_events(1000):
        total_events += 1
        if "level " in event:
            level = int(event.split("level ")[1].split(")")[0])
            if level >= 10:
                high_level += 1
        if "treasure" in event:
            treasure_events += 1
        if "leveled up" in event:
            level_up_events += 1
        if total_events <= 3:
            print(event)

    print("...")
    print("=== Stream Analytics ===")
    print(f"Total events processed: {total_events}")
    print(f"High-level players (10+): {high_level}")
    print(f"Treasure events: {treasure_events}")
    print(f"Level-up events: {level_up_events}")
    print("Memory usage: Constant (streaming)")

    def fibonacci(n):
        a, b = 0, 1
        count = 0
        while count < n:
            yield a
            a, b = b, a + b
            count += 1

    def primes(n):
        found = 0
        candidate = 2
        while found < n:
            is_prime = True
            for i in range(2, candidate):
                if candidate % i == 0:
                    is_prime = False
            if is_prime:
                yield candidate
                found += 1
            candidate += 1

    print("=== Generator Demonstration ===")
    fib_list = []
    i = 0
    for num in fibonacci(10):
        fib_list[i] = num
        i += 1
    print(f"Fibonacci sequence (first 10): {fib_list}")

    prime_list = []
    i = 0
    for num in primes(5):
        prime_list[i] = num
        i += 1
    print(f"Prime numbers (first 5): {prime_list}")
