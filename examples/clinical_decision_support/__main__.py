"""Run the clinical decision support demo from the command line."""

from examples.clinical_decision_support import run

if __name__ == "__main__":
    chain = run()
    print(f"Built and persisted {len(chain)} entries.")
    for e in chain:
        print(f"  {e.gate.value:<10}  {e.id}")
