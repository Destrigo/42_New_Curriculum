if __name__ == "__main__":
    """main"""
    print("=== CYBER ARCHIVES - DATA RECOVERY SYSTEM ===")
    print(f"Accessing Storage Vault: ancient_fragment.txt")

    try:
        with open("data-generator-tools.tar.gz", "r") as vault:
            print("Connection established...")
            print("RECOVERED DATA:")
            for line in vault:
                print(line.strip())
        print("Data recovery complete. Storage unit disconnected.")
    except FileNotFoundError:
        print("ERROR: Storage vault not found. Run data generator first.")