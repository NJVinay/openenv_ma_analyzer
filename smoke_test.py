"""
smoke_test.py — Automated smoke test for the M&A Due Diligence environment.

Starts uvicorn, hits /health, /reset, /step, /state endpoints,
and validates response schemas.

Exit code 0 = PASS, Exit code 1 = FAIL.
"""

import subprocess
import time
import sys
import os

# Ensure project root is on path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def test_environment():
    """Run smoke tests against the M&A environment."""
    results = []
    server_proc = None

    try:
        # Start server
        print("[SMOKE] Starting uvicorn server...")
        server_proc = subprocess.Popen(
            [
                sys.executable, "-m", "uvicorn",
                "server.app:app",
                "--host", "0.0.0.0",
                "--port", "7860",
            ],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
        time.sleep(3)

        # Import client and models after server starts
        from client import MADueDiligenceClient
        from models import Action

        client = MADueDiligenceClient(base_url="http://localhost:7860")

        # Test 1: /health
        print("[SMOKE] Testing /health...")
        try:
            health = client.health()
            assert "status" in health, "Missing 'status' key"
            results.append(("health", "PASS"))
            print(f"  -> PASS: {health}")
        except Exception as e:
            results.append(("health", f"FAIL: {e}"))
            print(f"  -> FAIL: {e}")

        # Test 2: /reset
        print("[SMOKE] Testing /reset...")
        try:
            obs = client.reset(seed=42)
            assert obs.deal_excerpt, "Missing deal_excerpt"
            assert obs.task_prompt, "Missing task_prompt"
            assert obs.done is False, "done should be False after reset"
            assert obs.step_count == 0, "step_count should be 0 after reset"
            results.append(("reset", "PASS"))
            print(f"  -> PASS: got excerpt ({len(obs.deal_excerpt)} chars)")
        except Exception as e:
            results.append(("reset", f"FAIL: {e}"))
            print(f"  -> FAIL: {e}")

        # Test 3: /step
        print("[SMOKE] Testing /step...")
        try:
            action = Action(
                agent_output='{"clause_type": "liability_cap", "reason": "test"}',
                action_type="identify",
            )
            obs = client.step(action)
            assert obs.reward is not None, "Missing reward"
            assert isinstance(obs.reward, float), "reward must be float"
            assert 0.0 <= obs.reward <= 1.0, f"reward {obs.reward} out of [0,1]"
            results.append(("step", "PASS"))
            print(f"  -> PASS: reward={obs.reward}, done={obs.done}")
        except Exception as e:
            results.append(("step", f"FAIL: {e}"))
            print(f"  -> FAIL: {e}")

        # Test 4: /state
        print("[SMOKE] Testing /state...")
        try:
            state = client.state()
            assert state.episode_id, "Missing episode_id"
            assert state.task_tier in ("easy", "medium", "hard"), f"Bad tier: {state.task_tier}"
            assert state.deal_type in (
                "NDA", "LOI", "SPA", "reps_and_warranties"
            ), f"Bad deal_type: {state.deal_type}"
            results.append(("state", "PASS"))
            print(f"  -> PASS: tier={state.task_tier}, deal={state.deal_type}")
        except Exception as e:
            results.append(("state", f"FAIL: {e}"))
            print(f"  -> FAIL: {e}")

    finally:
        # Cleanup
        if server_proc:
            server_proc.terminate()
            server_proc.wait(timeout=5)

    # Summary
    print("\n" + "=" * 50)
    print("SMOKE TEST RESULTS")
    print("=" * 50)
    all_pass = True
    for name, status in results:
        symbol = "+" if status == "PASS" else "X"
        print(f"  {symbol} {name}: {status}")
        if status != "PASS":
            all_pass = False

    if all_pass:
        print("\n  OVERALL: PASS")
        return 0
    else:
        print("\n  OVERALL: FAIL")
        return 1


if __name__ == "__main__":
    exit_code = test_environment()
    sys.exit(exit_code)
