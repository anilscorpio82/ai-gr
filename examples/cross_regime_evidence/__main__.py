"""Run the cross-regime evidence demo from the command line."""

from examples.cross_regime_evidence import run

if __name__ == "__main__":
    chain = run()
    print(f"Built and persisted {len(chain)} entries demonstrating cross-regime evidence reuse.")
    print()
    for entry in chain:
        regime_count = len(entry.regime)
        print(f"  {entry.gate.value:<10}  {entry.id}")
        print(f"  {'':10}  {regime_count} simultaneous regime claims")
        for claim in entry.regime[:3]:
            print(f"  {'':12}- {claim.regime}")
        if regime_count > 3:
            print(f"  {'':12}- ... and {regime_count - 3} more")
        print()
