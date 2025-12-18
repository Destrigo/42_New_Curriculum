from abc import ABC, abstractmethod
from typing import Any


class DataProcessor(ABC):
    """dataprocessor"""

    @abstractmethod
    def process(self, data: Any) -> str:
        pass

    @abstractmethod
    def validate(self, data: Any) -> bool:
        pass

    def format_output(self, result: str) -> str:
        result = "Data_Processed result: " + result
        return result


class NumericProcessor(DataProcessor):
    def __init__(self) -> None:
        self.data = []

    def process(self, data: Any) -> str:
        if self.validate(data):
            self.data = data
            return "Validation: Numeric data verified"
        else:
            return "Allert! Data not valid"

    def validate(self, data: Any) -> bool:
        return isinstance(data,
                          list) and all(isinstance(x, (int,
                                                       float)) for x in data)

    def format_output(self, result: str) -> str:
        num = len(self.data)
        plus = sum(self.data)
        avg = plus / num
        result1 = f"Output: Processed {num} numeric values, "
        result2 = f"sum={plus}, avg={avg}"
        result = result1 + result2
        return result


class TextProcessor(DataProcessor):
    def __init__(self) -> None:
        self.data = ""

    def process(self, data: Any) -> str:
        if self.validate(data):
            self.data = data
            return "Validation: Text data verified"
        else:
            return "Allert! Text not valid"

    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def format_output(self, result: str) -> str:
        num = len(self.data)
        words = len(self.data.split(" "))
        result1 = f"Output: Processed text: {num} characters, "
        result2 = f"{words} words"
        result = result1 + result2
        return result


class LogProcessor(DataProcessor):
    def __init__(self) -> None:
        self.data = ""

    def process(self, data: Any) -> str:
        if self.validate(data):
            self.data = data
            return "Validation: Log entry verified"
        else:
            return "Allert! Log input not valid"

    def validate(self, data: Any) -> bool:
        return isinstance(data, str)

    def format_output(self, result: str) -> str:
        if self.data[:5] == "ERROR":
            result = "Output: [ALLERT] ERROR level detected: " + self.data[7:]
        elif self.data[:4] == "INFO":
            result = "Output: [INFO] INFO level detected: " + self.data[6:]
        return result


if __name__ == "__main__":
    """program"""
    print("=== CODE NEXUS - DATA PROCESSOR FOUNDATION ===")
    print("")

    print("Initializing Numeric Processor...")
    data = [1, 2, 3, 4, 5]
    num_pro = NumericProcessor()
    print(f"Processing data: {data}")
    print(f"{num_pro.process(data)}")
    print(f"{num_pro.format_output("")}")
    print("")

    print("Initializing Text Processor...")
    data = "Hello Nexus World"
    txt_pro = TextProcessor()
    print(f"Processing data: {data}")
    print(f"{txt_pro.process(data)}")
    print(f"{txt_pro.format_output("")}")
    print("")

    print("Initializing Log Processor...")
    data = "ERROR: Connection timeout"
    log_pro = LogProcessor()
    print(f"Processing data: {data}")
    print(f"{log_pro.process(data)}")
    print(f"{log_pro.format_output("")}")
    print("")
    print("")

    print("=== Polymorphic Processing Demo ===")
    print("Processing multiple data types through same interface...")

    processors = [
        NumericProcessor(),
        TextProcessor(),
        LogProcessor()
    ]
    datasets = [
        [1, 2, 3],
        "Hello Nexus",
        "INFO: System ready"
    ]
    results = []
    i = 1
    for processor, data in zip(processors, datasets):
        processor.process(data)
        print(f"Result {i}: {processor.format_output("")}")
        i += 1
    print("")
    print("Foundation systems online. Nexus ready for advanced streams.")
