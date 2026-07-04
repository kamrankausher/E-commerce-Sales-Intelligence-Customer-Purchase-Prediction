"""
setup.py — One-command setup for the E-commerce Customer Analytics project.

Generates synthetic data if CSV files are missing, then prints next steps.

Usage:
    python setup.py
"""
import os
import sys

# ─── Configuration ────────────────────────────────────────────────────────
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PROJECT_ROOT, "data", "raw")
GEN_SCRIPT = os.path.join(PROJECT_ROOT, "data", "generate_fake_data.py")
sys.path.insert(0, PROJECT_ROOT)


def main():
    print("=" * 60)
    print("  E-commerce Customer Analytics — Setup")
    print("=" * 60)
    print()

    # Check if CSVs already exist
    required_csv = "olist_orders_dataset.csv"
    csv_path = os.path.join(DATA_DIR, required_csv)

    if os.path.exists(csv_path):
        print("[OK] Dataset found — CSVs already exist.")
        print(f"     Location: {DATA_DIR}")
    else:
        print("[1/1] Generating synthetic e-commerce data...")
        print("-" * 50)
        try:
            from data.generate_fake_data import generate_fake_data
            generate_fake_data()
            print("[OK] Data generated successfully!")
        except Exception as e:
            print(f"[ERROR] Data generation failed: {e}")
            print("  You can also download real data: python data/download_olist.py")
            return

    # Create models directory
    os.makedirs(os.path.join(PROJECT_ROOT, "models"), exist_ok=True)

    print()
    print("=" * 60)
    print("  Setup Complete!")
    print("=" * 60)
    print()
    print("  Next Steps:")
    print()
    print("  1. Run Jupyter notebooks (in order):")
    print("     jupyter notebook notebooks/")
    print()
    print("  2. Or launch the Streamlit dashboard:")
    print("     streamlit run app.py")
    print()
    print("  Note: Run notebooks 01-05 first to generate")
    print("  the cleaned data and trained model that the")
    print("  dashboard needs.")
    print()


if __name__ == "__main__":
    main()
