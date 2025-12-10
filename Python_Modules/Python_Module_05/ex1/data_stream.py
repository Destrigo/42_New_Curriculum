from abc import ABC, abstractmethod
from typing import  Any, List, Dict, Union, Optional


class DataStream(ABC):
    """base class"""
    def __init__(self, stream_id: str):
        self.stream_id = stream_id
        self.data: List[Any] = []

    @abstractmethod
    def process_batch(self, data_batch: List[Any]) -> str:
        """Process incoming data"""
        pass

    def filter_data(self, data_batch: List[Any], criteria: Optional[str]
                    = None) -> List[Any]:
        """Filter data based on criteria"""
        filtered: List[Any] = []
        for item in data_batch:
            if criteria == "high_temp" and isinstance(item, dict) and "temp" in item and item["temp"] > 22:
                filtered.append(item)
            elif criteria == "critical_transaction" and isinstance(item, dict) and item.get("buy", 0) > 100:
                filtered.append(item)
            elif criteria is None:
                filtered.append(item)
        return filtered

    def get_stats(self) -> Dict[str, Union[str, int, float]]:
        """Return stream statistics"""
        return {"stream_id": self.stream_id, "count": len(self.data)}


class SensorStream(DataStream):
    def __init__(self, stream_id: str) -> None:
        super().__init__(stream_id)
        """initialize"""
        print("Initializing Sensor Stream...")
        print(f"Stream ID: {self.stream_id}, Type: Environmental Data")

    def process_batch(self, data_batch: List[Any]) -> str:
        """Process a batch of data"""
        try:
            total_temp = 0.0
            processed_count = 0
            for reading in data_batch:
                if isinstance(reading, dict) and "temp" in reading:
                    self.data.append(reading)
                    total_temp += reading["temp"]
                    processed_count += 1
            avg_temp = total_temp / processed_count if processed_count > 0 else 0
            return f"Sensor analysis: {processed_count} readings processed, avg temp: {avg_temp:.2f}°C"
        except Exception as e:
            return f"[{self.stream_id}] Error processing sensor batch: {e}"


    # def filter_data(self, data_batch: List[Any], criteria: Optional[str]
    #                 = None) -> List[Any]:
    #     """Filter data based on criteria"""

    # def get_stats(self) -> Dict[str, Union[str, int, float]]:
    #     """Return stream statistics"""


class TransactionStream(DataStream):
    def __init__(self, stream_id: str) -> None:
        super().__init__(stream_id)
        """initialize"""
        print("Initializing Transaction Stream...")
        print(f"Stream ID: {self.stream_id}, Type: Transactions Data")

    def process_batch(self, data_batch: List[Any]) -> str:
        """Process a batch of data"""
        try:
            net_flow = 0
            processed_count = 0
            for tx in data_batch:
                if isinstance(tx, dict):
                    buy = tx.get("buy", 0)
                    sell = tx.get("sell", 0)
                    net_flow += buy - sell
                    self.data.append(tx)
                    processed_count += 1
            return f"Transaction analysis: {processed_count} operations, net flow: {net_flow} units"
        except Exception as e:
            return f"[{self.stream_id}] Error processing transaction batch: {e}"

    # def filter_data(self, data_batch: List[Any], criteria: Optional[str]
    #                 = None) -> List[Any]:
    #     """Filter data based on criteria"""

    # def get_stats(self) -> Dict[str, Union[str, int, float]]:
    #     """Return stream statistics"""


class EventStream(DataStream):
    def __init__(self, stream_id: str) -> None:
        super().__init__(stream_id)
        """initialize"""
        print("Initializing Event Stream...")
        print(f"Stream ID: {self.stream_id}, Type: Events Data")

    def process_batch(self, data_batch: List[Any]) -> str:
        """Process a batch of data"""
        try:
            processed_count = 0
            error_count = 0
            for ev in data_batch:
                if isinstance(ev, str):
                    self.data.append(ev)
                    processed_count += 1
                    if ev.lower() == "error":
                        error_count += 1
            return f"Event analysis: {processed_count} events, {error_count} error(s) detected"
        except Exception as e:
            return f"[{self.stream_id}] Error processing event batch: {e}"


    # def filter_data(self, data_batch: List[Any], criteria: Optional[str]
    #                 = None) -> List[Any]:
    #     """Filter data based on criteria"""

    # def get_stats(self) -> Dict[str, Union[str, int, float]]:
    #     """Return stream statistics"""


class StreamProcessor:
    def __init__(self) -> None:
        self.streams: List[DataStream] = []

    def register_stream(self, stream: DataStream) -> None:
        self.streams.append(stream)

    def process_all_batches(self, batches: List[List[Any]]) -> None:
        for i in range(len(self.streams)):
            if i < len(batches):
                try:
                    result = self.streams[i].process_batch(batches[i])
                    print(result)
                except Exception as e:
                    print(f"Error processing {self.streams[i].stream_id}: {e}")


# if __name__ == "__main__":
#     """main"""
#     print("=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ===")
#     print("")
#     sensor = SensorStream("SENSOR_001")
#     sensor_data = [22.5, 65, 1013]
#     sensor.process_batch(sensor_data)

#     print("=== Polymorphic Stream Processing ===")
#     print("Processing mixed stream types through unified interface...")
#     print("")
#     data_stream = [10, "hello", 3.14, "world", 7, 2.718, [1, 2, 3]]

#     processor = StreamProcessor()
#     processor.process_stream(data_stream)
if __name__ == "__main__":
    print("=== CODE NEXUS - POLYMORPHIC STREAM SYSTEM ===")
    print("")
    # Initialize streams
    sensor_stream = SensorStream("SENSOR_001")
    tx_stream = TransactionStream("TRANS_001")
    event_stream = EventStream("EVENT_001")
    # Register streams
    processor = StreamProcessor()
    processor.register_stream(sensor_stream)
    processor.register_stream(tx_stream)
    processor.register_stream(event_stream)
    # Define batches
    sensor_batch = [{"temp": 22.5, "humidity": 65, "pressure": 1013}, {"temp": 23.0, "humidity": 63, "pressure": 1010}]
    transaction_batch = [{"buy": 100, "sell": 75}, {"buy": 150, "sell": 125}, {"buy": 50}]
    event_batch = ["login", "error", "logout"]
    print("")
    # Process batches polymorphically
    print("=== Polymorphic Stream Processing ===")
    processor.process_all_batches([sensor_batch, transaction_batch, event_batch])
    print("")
    # Filtering example
    filtered_sensors = sensor_stream.filter_data(sensor_batch, "high_temp")
    filtered_transactions = tx_stream.filter_data(transaction_batch, "critical_transaction")
    print("Filtered sensor readings:", filtered_sensors)
    print("Filtered transactions:", filtered_transactions)
    print("")
    # Stats
    print("Sensor stats:", sensor_stream.get_stats())
    print("Transaction stats:", tx_stream.get_stats())
    print("Event stats:", event_stream.get_stats())
