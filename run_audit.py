import subprocess
import sys

def main():
    print("=" * 50)
    print("🚀 Starting Automated LLM Audit Pipeline...")
    print("=" * 50)

    # 1. Generate Responses
    print("\n[Step 1/3] Generating Responses from Model...")
    res_1 = subprocess.run([sys.executable, "generate_responses.py"])
    if res_1.returncode != 0:
        print("❌ Error in generating responses. Pipeline stopped.")
        return

    # 2. Run Audit Engine
    print("\n[Step 2/3] Scoring Toxicity and Implicit Bias...")
    res_2 = subprocess.run([sys.executable, "audit_engine.py"])
    if res_2.returncode != 0:
        print("❌ Error in audit engine. Pipeline stopped.")
        return

    # 3. Launch Streamlit Dashboard
    print("\n[Step 3/3] Launching Dashboard...")
    print("=" * 50)
    print("✨ Audit Complete! Opening Streamlit Dashboard...")
    print("=" * 50)
    
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py"])

if __name__ == "__main__":
    main()