"""Run all unit tests + benchmarks.

Usage:
  python tests/run_all.py           # unit tests only
  python tests/run_all.py --bench   # unit tests + benchmarks
"""
import sys, os, unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


def run_unit_tests() -> bool:
    loader = unittest.TestLoader()
    suite = loader.discover(os.path.dirname(os.path.abspath(__file__)), pattern="test_*.py")
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


def run_benchmarks():
    import bench_indicators
    bench_indicators.bench_indicators()
    bench_indicators.bench_macd_scaling()
    bench_indicators.bench_config()
    bench_indicators.bench_signing()
    bench_indicators.bench_grid()
    bench_indicators.bench_ws_cache()
    bench_indicators.bench_private_ws_cache()


if __name__ == "__main__":
    print("=" * 65)
    print("OKX Exchange Skill — Test Suite")
    print("=" * 65)

    ok = run_unit_tests()

    if "--bench" in sys.argv:
        print("\n" + "=" * 65)
        print("Benchmarks")
        print("=" * 65)
        run_benchmarks()

    sys.exit(0 if ok else 1)
