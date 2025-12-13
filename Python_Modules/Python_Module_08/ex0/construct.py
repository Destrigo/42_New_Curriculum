import sys
import os
import site


def main():
    print("=== MATRIX STATUS CHECK ===\n")

    venv = getattr(sys, 'real_prefix',
                   None) or getattr(sys, 'base_prefix', sys.prefix)
    in_venv = sys.prefix != getattr(sys, "base_prefix", sys.prefix)

    current_python = sys.executable
    print(f"Current Python: {current_python}")

    if in_venv:
        # Inside virtual environment
        venv_path = sys.prefix
        venv_name = os.path.basename(venv_path)
        print(f"Virtual Environment: {venv_name}")
        print(f"Environment Path: {venv_path}")
        print("\nSUCCESS: You're in an isolated environment!")
        print("Safe to install packages without affecting the global system.")
        print("Package installation "
              f"path:\n{site.getsitepackages()[0] if
                        site.getsitepackages() else
                        site.getusersitepackages()}")
    else:
        print("Virtual Environment: None detected")
        print("\nWARNING: You're in the global environment!")
        print("The machines can see everything you install.")
        print("To enter the construct, run:")
        print("python -m venv matrix_env")
        print("source matrix_env/bin/activate  # On Unix")
        print("matrix_env\\Scripts\\activate     # On Windows")
        print("Then run this program again.")


if __name__ == "__main__":
    main()
