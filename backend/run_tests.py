"""
测试运行脚本
提供便捷的测试执行方式
"""
import sys
import subprocess


def run_all_tests():
    """运行所有测试"""
    print("🧪 运行所有测试...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/"])


def run_unit_tests():
    """只运行单元测试"""
    print("🧪 运行单元测试...")
    subprocess.run([sys.executable, "-m", "pytest", "tests/", "-m", "unit"])


def run_integration_tests():
    """运行集成测试（需要真实服务）"""
    print("🧪 运行集成测试...")
    subprocess.run([
        sys.executable, "-m", "pytest", "tests/",
        "-m", "integration",
        "--run-integration"
    ])


def run_with_coverage():
    """运行测试并生成覆盖率报告"""
    print("🧪 运行测试并生成覆盖率报告...")
    subprocess.run([
        sys.executable, "-m", "pytest", "tests/",
        "--cov=app",
        "--cov-report=html",
        "--cov-report=term"
    ])
    print("\n📊 覆盖率报告已生成: htmlcov/index.html")


def run_specific_test(test_file):
    """运行特定测试文件"""
    print(f"🧪 运行测试文件: {test_file}")
    subprocess.run([sys.executable, "-m", "pytest", f"tests/{test_file}", "-v"])


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="运行测试")
    parser.add_argument(
        "--mode",
        choices=["all", "unit", "integration", "coverage"],
        default="all",
        help="测试模式"
    )
    parser.add_argument(
        "--file",
        help="运行特定测试文件（如 test_rag_service.py）"
    )

    args = parser.parse_args()

    if args.file:
        run_specific_test(args.file)
    elif args.mode == "all":
        run_all_tests()
    elif args.mode == "unit":
        run_unit_tests()
    elif args.mode == "integration":
        run_integration_tests()
    elif args.mode == "coverage":
        run_with_coverage()
