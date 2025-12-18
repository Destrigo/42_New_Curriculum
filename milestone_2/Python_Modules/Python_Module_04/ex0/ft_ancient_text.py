if __name__ == "__main__":
    """main"""
    fd = "../ancient_fragment.txt"
    print("=== CYBER ARCHIVES - DATA RECOVERY SYSTEM ===")
    print(f"Accessing Storage Vault: {fd}.txt")

    try:
        with open(fd, "r") as vault:
            print("\nConnection established...")
            print("RECOVERED DATA:")
            for line in vault:
                print(line.strip())
        print("\nData recovery complete. Storage unit disconnected.")
    except FileNotFoundError:
        print("\nERROR: Storage vault not found. Run data generator first.")
