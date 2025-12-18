import sys


if __name__ == "__main__":
    """main"""
    print("=== CYBER ARCHIVES - PRESERVATION SYSTEM ===")
    print("")
    id = input("Input Stream active. Enter archivist ID: ")
    status_report = input("Input Stream active. Enter status report: ")

    str1 = "{[}STANDARD{]} Archive status from " + f"{id}: {status_report}"
    str2 = "{[}ALERT{]} System diagnostic: Communication channels verified"
    str3 = "{[}STANDARD{]} Data transmission complete"
    print("\nConnection established...")
    sys.stdout.write(f"{str1}\n")
    sys.stderr.write(f"{str2}\n")
    sys.stdout.write(f"{str3}\n")
    print("\nThree-channel communication test successful.")
