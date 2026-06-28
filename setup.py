"""
setup.py - One-command setup for the E-commerce Growth Intelligence Platform.

Usage:
    python setup.py
"""
import os
import sys
import time
import io

# Fix Windows console encoding for emoji
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, PROJECT_ROOT)


def main():
    start = time.time()
    print("=" * 70)
    print("  E-commerce Growth Intelligence Platform - Setup")
    print("=" * 70)
    print()

    # Step 1: Generate Data (Optional if CSVs exist, but keeping for completeness)
    print("[1/2] Generating realistic e-commerce data (if missing)...")
    print("-" * 50)
    try:
        from data.generate_fake_data import generate_fake_data
        generate_fake_data()
    except Exception as e:
        print("Data generation skipped or failed (CSVs likely already exist).")
        pass
    print()

    # Step 2: Load into SQLite
    print("[2/2] Loading data into SQLite...")
    print("-" * 50)
    from data.load_data import load_all_data
    load_all_data()
    print()

    elapsed = time.time() - start
    print("=" * 70)
    print(f"  Setup complete in {elapsed:.1f} seconds!")
    print("=" * 70)
    print()
    print("  To start the backend API:")
    print()
    print("    python -m uvicorn app.main:app --reload --port 8000")
    print()
    print("  Then open: http://localhost:8000/docs for Swagger UI")
    print()


if __name__ == "__main__":
    main()
