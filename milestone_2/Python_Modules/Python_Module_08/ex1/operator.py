import sys
import numpy as np
import matplotlib.pyplot as plt


def check_import(pkg_name, import_name=None):
    import_name = import_name or pkg_name
    try:
        module = __import__(import_name)
        version = getattr(module, '__version__', 'unknown')
        print(f"[OK] {pkg_name} ({version}) - ready")
        return module
    except ImportError:
        print(f"[MISSING] {pkg_name} is not installed!")
        return None


def main():
    print("OPERATOR STATUS: Loading programs...")
    print("Checking dependencies:")

    pd = check_import('pandas')
    requests = check_import('requests')
    line = check_import('matplotlib', 'matplotlib.pyplot')

    if not all([pd, requests, line]):
        print("\nERROR: Missing dependencies. "
              "Please install them with pip or Poetry.")
        print("pip: pip install -r requirements.txt")
        print("Poetry: poetry install && poetry run python operator.py")
        sys.exit(1)

    print("Analyzing Matrix data...")
    data = pd.DataFrame({
        'signal': np.random.randn(1000).cumsum(),
        'noise': np.random.randn(1000)
    })
    print("Processing 1000 data points...")

    data['signal_ma'] = data['signal'].rolling(window=20).mean()

    print("Generating visualization...")
    plt.figure(figsize=(10, 5))
    plt.plot(data['signal'], label='Signal')
    plt.plot(data['signal_ma'], label='Signal MA', linewidth=2)
    plt.title("Matrix Data Analysis")
    plt.xlabel("Time Step")
    plt.ylabel("Value")
    plt.legend()
    plt.tight_layout()
    plt.savefig("matrix_analysis.png")
    print("Analysis complete!")
    print("Results saved to: matrix_analysis.png")


if __name__ == "__main__":
    main()
