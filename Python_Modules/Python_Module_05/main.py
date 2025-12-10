#!/usr/bin/env python3
"""
Code Nexus - Polymorphism Testing Suite with Type Checking

This testing suite validates your implementation of polymorphic data processing systems.
It checks for proper method overriding, inheritance relationships, polymorphic behavior,
and type annotations across all three exercises.

Usage:
    python3 main.py

Requirements:
    - Python 3.11 or later
    - Your exercise files must be in the solution/ directory
    - All code must include proper type annotations
"""

import sys
import importlib.util
import ast
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path


class TestResult:
    """Encapsulates test results with detailed feedback."""

    def __init__(self, name: str) -> None:
        self.name: str = name
        self.passed: bool = False
        self.errors: List[str] = []
        self.warnings: List[str] = []

    def add_error(self, error: str) -> None:
        """Add an error message."""
        self.errors.append(error)

    def add_warning(self, warning: str) -> None:
        """Add a warning message."""
        self.warnings.append(warning)

    def mark_passed(self) -> None:
        """Mark test as passed."""
        self.passed = True


class TypeChecker:
    """Validates type annotations in Python code."""

    def __init__(self) -> None:
        self.required_imports = ["typing", "Any", "List", "Dict", "Union", "Optional"]

    def check_file_typing(self, file_path: str) -> Tuple[bool, List[str]]:
        """Check if file has proper type annotations."""
        try:
            with open(file_path, 'r') as f:
                content = f.read()

            tree = ast.parse(content)
            issues = []
            has_typing_imports = False

            # Check for typing imports
            for node in ast.walk(tree):
                if isinstance(node, ast.ImportFrom) and node.module == "typing":
                    has_typing_imports = True
                elif isinstance(node, ast.Import):
                    for alias in node.names:
                        if alias.name == "typing":
                            has_typing_imports = True

            if not has_typing_imports:
                issues.append("Missing typing imports")

            # Check function definitions for type annotations
            function_count = 0
            typed_functions = 0

            for node in ast.walk(tree):
                if isinstance(node, ast.FunctionDef):
                    function_count += 1

                    # Check return type annotation
                    if node.returns is not None:
                        typed_functions += 1

                    # Check parameter type annotations
                    for arg in node.args.args:
                        if arg.annotation is None and arg.arg != "self":
                            issues.append(f"Function '{node.name}' parameter '{arg.arg}' missing type annotation")

            if function_count > 0:
                typing_coverage = (typed_functions / function_count) * 100
                if typing_coverage < 80:
                    issues.append(f"Low typing coverage: {typing_coverage:.1f}% of functions have return type annotations")

            return len(issues) == 0, issues

        except Exception as e:
            return False, [f"Error checking types: {str(e)}"]


class PolymorphismTester:
    """Main testing class for polymorphic implementations with type checking."""

    def __init__(self) -> None:
        self.results: List[TestResult] = []
        self.type_checker = TypeChecker()

    def load_module(self, file_path: str, module_name: str) -> Optional[Any]:
        """Dynamically load a Python module from file path."""
        try:
            spec = importlib.util.spec_from_file_location(module_name, file_path)
            if spec is None or spec.loader is None:
                return None

            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            return module
        except Exception as e:
            print(f"Error loading module {module_name}: {e}")
            return None

    def run_all_tests(self) -> bool:
        """Execute all test suites and return overall success status."""
        print("CODE NEXUS - POLYMORPHISM TESTING SUITE WITH TYPE CHECKING")
        print("=" * 60)
        print("This will test if your classes are properly implemented with type annotations.")
        print("Each test will only pass if you've correctly created the required classes with typing!\n")

        # Run individual test suites
        self._test_exercise_0()
        self._test_exercise_1()
        self._test_exercise_2()

        # Display summary
        self._display_summary()

        return all(result.passed for result in self.results)

    def _test_exercise_0(self) -> None:
        """Test Exercise 0: Data Processor Foundation with type checking."""
        result = TestResult("Exercise 0: Data Processor Foundation")

        print("=== Testing Exercise 0: Data Processor Foundation ===")

        try:
            file_path = "../solution/ex0/stream_processor.py"

            # Check type annotations first
            has_proper_typing, typing_issues = self.type_checker.check_file_typing(file_path)
            if not has_proper_typing:
                result.add_error("Type annotation issues found:")
                for issue in typing_issues:
                    result.add_error(f"  • {issue}")
            else:
                print("✓ Type annotations properly implemented")

            # Import the learner's implementation
            stream_processor = self.load_module(file_path, "stream_processor")
            if not stream_processor:
                result.add_error("Could not load stream_processor.py module")
            else:
                # Verify required classes exist
                required_classes = ['DataProcessor', 'NumericProcessor', 'TextProcessor', 'LogProcessor']
                missing_classes = []

                for class_name in required_classes:
                    if not hasattr(stream_processor, class_name):
                        missing_classes.append(class_name)

                if missing_classes:
                    result.add_error(f"Missing classes: {', '.join(missing_classes)}")
                else:
                    print("✓ All required classes found")

                    # Test inheritance relationships
                    DataProcessor = getattr(stream_processor, 'DataProcessor')
                    NumericProcessor = getattr(stream_processor, 'NumericProcessor')
                    TextProcessor = getattr(stream_processor, 'TextProcessor')
                    LogProcessor = getattr(stream_processor, 'LogProcessor')

                    if not issubclass(NumericProcessor, DataProcessor):
                        result.add_error("NumericProcessor must inherit from DataProcessor")
                    if not issubclass(TextProcessor, DataProcessor):
                        result.add_error("TextProcessor must inherit from DataProcessor")
                    if not issubclass(LogProcessor, DataProcessor):
                        result.add_error("LogProcessor must inherit from DataProcessor")

                    if not result.errors:
                        print("✓ Inheritance relationships verified")

                        # Test method overriding
                        try:
                            numeric_proc = NumericProcessor()
                            text_proc = TextProcessor()
                            log_proc = LogProcessor()

                            # Verify methods exist and are callable
                            for processor in [numeric_proc, text_proc, log_proc]:
                                for method in ['process', 'validate', 'format_output']:
                                    if not hasattr(processor, method) or not callable(getattr(processor, method)):
                                        result.add_error(f"{processor.__class__.__name__} missing method: {method}")

                            if not result.errors:
                                print("✓ Method overriding implemented correctly")
                                if has_proper_typing:
                                    result.mark_passed()

                        except Exception as e:
                            result.add_error(f"Error testing method overriding: {str(e)}")

        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        if not result.passed:
            print("✗ Exercise 0 failed - check implementation and type annotations")

        self.results.append(result)

    def _test_exercise_1(self) -> None:
        """Test Exercise 1: Polymorphic Streams with type checking."""
        result = TestResult("Exercise 1: Polymorphic Streams")

        print("\n=== Testing Exercise 1: Polymorphic Streams ===")

        try:
            file_path = "../solution/ex1/data_stream.py"

            # Check type annotations first
            has_proper_typing, typing_issues = self.type_checker.check_file_typing(file_path)
            if not has_proper_typing:
                result.add_error("Type annotation issues found:")
                for issue in typing_issues:
                    result.add_error(f"  • {issue}")
            else:
                print("✓ Type annotations properly implemented")

            # Import the learner's implementation
            data_stream = self.load_module(file_path, "data_stream")
            if not data_stream:
                result.add_error("Could not load data_stream.py module")
            else:
                # Verify required classes exist
                required_classes = ['DataStream', 'SensorStream', 'TransactionStream', 'EventStream', 'StreamProcessor']
                missing_classes = []

                for class_name in required_classes:
                    if not hasattr(data_stream, class_name):
                        missing_classes.append(class_name)

                if missing_classes:
                    result.add_error(f"Missing classes: {', '.join(missing_classes)}")
                else:
                    print("✓ All required classes found")

                    # Test inheritance and polymorphism
                    DataStream = getattr(data_stream, 'DataStream')
                    SensorStream = getattr(data_stream, 'SensorStream')
                    TransactionStream = getattr(data_stream, 'TransactionStream')
                    EventStream = getattr(data_stream, 'EventStream')
                    StreamProcessor = getattr(data_stream, 'StreamProcessor')

                    # Verify inheritance
                    stream_classes = [SensorStream, TransactionStream, EventStream]
                    for stream_class in stream_classes:
                        if not issubclass(stream_class, DataStream):
                            result.add_error(f"{stream_class.__name__} must inherit from DataStream")

                    if not result.errors:
                        print("✓ Inheritance relationships verified")

                        # Test polymorphic behavior
                        try:
                            processor = StreamProcessor()
                            sensor = SensorStream("SENSOR_001")
                            transaction = TransactionStream("TRANS_001")
                            event = EventStream("EVENT_001")

                            # Verify polymorphic processing
                            streams = [sensor, transaction, event]
                            for stream in streams:
                                if not hasattr(stream, 'process_batch') or not callable(getattr(stream, 'process_batch')):
                                    result.add_error(f"{stream.__class__.__name__} missing process_batch method")

                            if not result.errors:
                                print("✓ Polymorphic behavior implemented correctly")
                                if has_proper_typing:
                                    result.mark_passed()

                        except Exception as e:
                            result.add_error(f"Error testing polymorphic behavior: {str(e)}")

        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        if not result.passed:
            print("✗ Exercise 1 failed - check implementation and type annotations")

        self.results.append(result)

    def _test_exercise_2(self) -> None:
        """Test Exercise 2: Nexus Integration with type checking."""
        result = TestResult("Exercise 2: Nexus Integration")

        print("\n=== Testing Exercise 2: Nexus Integration ===")

        try:
            file_path = "../solution/ex2/nexus_pipeline.py"

            # Check type annotations first
            has_proper_typing, typing_issues = self.type_checker.check_file_typing(file_path)
            if not has_proper_typing:
                result.add_error("Type annotation issues found:")
                for issue in typing_issues:
                    result.add_error(f"  • {issue}")
            else:
                print("✓ Type annotations properly implemented")

            # Import the learner's implementation
            nexus_pipeline = self.load_module(file_path, "nexus_pipeline")
            if not nexus_pipeline:
                result.add_error("Could not load nexus_pipeline.py module")
            else:
                # Verify required classes exist
                required_classes = ['ProcessingPipeline', 'InputStage', 'TransformStage', 'OutputStage',
                                  'JSONAdapter', 'CSVAdapter', 'StreamAdapter', 'NexusManager']
                missing_classes = []

                for class_name in required_classes:
                    if not hasattr(nexus_pipeline, class_name):
                        missing_classes.append(class_name)

                if missing_classes:
                    result.add_error(f"Missing classes: {', '.join(missing_classes)}")
                else:
                    print("✓ All required classes found")

                    # Test complex inheritance hierarchy
                    ProcessingPipeline = getattr(nexus_pipeline, 'ProcessingPipeline')
                    JSONAdapter = getattr(nexus_pipeline, 'JSONAdapter')
                    CSVAdapter = getattr(nexus_pipeline, 'CSVAdapter')
                    StreamAdapter = getattr(nexus_pipeline, 'StreamAdapter')

                    # Verify inheritance
                    adapter_classes = [JSONAdapter, CSVAdapter, StreamAdapter]
                    for adapter_class in adapter_classes:
                        if not issubclass(adapter_class, ProcessingPipeline):
                            result.add_error(f"{adapter_class.__name__} must inherit from ProcessingPipeline")

                    if not result.errors:
                        print("✓ Complex inheritance hierarchy verified")

                        # Test enterprise-level polymorphism
                        try:
                            NexusManager = getattr(nexus_pipeline, 'NexusManager')
                            manager = NexusManager()

                            # Verify manager can handle different pipeline types
                            json_adapter = JSONAdapter("JSON_001")
                            csv_adapter = CSVAdapter("CSV_001")
                            stream_adapter = StreamAdapter("STREAM_001")

                            adapters = [json_adapter, csv_adapter, stream_adapter]
                            for adapter in adapters:
                                if not hasattr(adapter, 'process') or not callable(getattr(adapter, 'process')):
                                    result.add_error(f"{adapter.__class__.__name__} missing process method")

                            if not result.errors:
                                print("✓ Enterprise-level polymorphism implemented correctly")
                                if has_proper_typing:
                                    result.mark_passed()

                        except Exception as e:
                            result.add_error(f"Error testing enterprise polymorphism: {str(e)}")

        except Exception as e:
            result.add_error(f"Unexpected error: {str(e)}")

        if not result.passed:
            print("✗ Exercise 2 failed - check implementation and type annotations")

        self.results.append(result)

    def _display_summary(self) -> None:
        """Display comprehensive test summary."""
        print("\n" + "=" * 60)
        print("TESTING SUMMARY")
        print("=" * 60)

        passed_count = sum(1 for result in self.results if result.passed)
        total_count = len(self.results)

        print(f"Exercises passed: {passed_count}/{total_count}")

        if passed_count == total_count:
            print("🎉 All tests passed! Your polymorphic implementations with type annotations are working correctly.")
        else:
            print("⚠️  Some exercises need work. Check the error messages above.")
            print("Make sure you've implemented all required classes, methods, and type annotations.")

        # Display detailed errors if any
        for result in self.results:
            if result.errors:
                print(f"\n❌ {result.name}:")
                for error in result.errors:
                    print(f"   • {error}")

        print("\nRemember: This tests basic functionality and type annotations.")
        print("Make sure your code demonstrates proper polymorphic behavior with complete typing!")


def main() -> None:
    """Main entry point for the testing suite."""
    # Verify solution directory exists
    solution_dir = Path("../solution")
    if not solution_dir.exists():
        print("❌ Solution directory not found!")
        print("Please ensure your solutions are in the 'solution/' directory")
        sys.exit(1)

    tester = PolymorphismTester()
    success = tester.run_all_tests()

    # Exit with appropriate code
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
