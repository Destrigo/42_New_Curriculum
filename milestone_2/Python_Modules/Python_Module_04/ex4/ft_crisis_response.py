def crisis_handler(filename, routine=False):
    """Handles archive access attempts."""
    try:
        if routine:
            print(f"ROUTINE ACCESS: Attempting access to '{filename}'...")
        else:
            print(f"CRISIS ALERT: Attempting access to '{filename}'...")

        with open(filename, "r") as vault:
            print(f"SUCCESS: Archive recovered - ``{vault.read()}``")
            print("STATUS: Normal operations resumed")

    except FileNotFoundError:
        print("RESPONSE: Archive not found in storage matrix")
        print("STATUS: Crisis handled, system stable")

    except PermissionError:
        print("RESPONSE: Security protocols deny access")
        print("STATUS: Crisis handled, security maintained")

    except Exception:
        print("RESPONSE: Unexpected system anomaly detected")
        print("STATUS: Crisis contained, analysis required")


if __name__ == "__main__":
    """main"""
    print("=== CYBER ARCHIVES - CRISIS RESPONSE SYSTEM ===\n")

    crisis_handler("../lost_archive.txt")
    print("")
    crisis_handler("../classified_vault.txt")
    print("")
    crisis_handler("../standard_archive.txt", routine=True)
    print("\nAll crisis scenarios handled successfully. Archives secure.")
