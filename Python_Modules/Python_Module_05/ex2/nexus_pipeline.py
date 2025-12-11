from abc import ABC, abstractmethod
from typing import Any, List, Union, Protocol


# Protocol for stages
class ProcessingStage(Protocol):
    def process(self, data: Any) -> Any:
        ...


# Abstract base for pipelines
class ProcessingPipeline(ABC):
    def __init__(self) -> None:
        self.stages: List[ProcessingStage] = []

    def add_stage(self, stage: ProcessingStage) -> None:
        self.stages.append(stage)

    @abstractmethod
    def process(self, data: Any) -> Any:
        pass


# Stage implementations
class InputStage:
    def process(self, data: Any) -> Any:
        # Example: validate or parse input
        return data


class TransformStage:
    def process(self, data: Any) -> Any:
        # Example: enrich or transform data
        return f"Transformed({data})"


class OutputStage:
    def process(self, data: Any) -> Any:
        # Example: format output
        return f"Output({data})"

# Adapter classes for specific formats

class JSONAdapter(ProcessingPipeline):
    def __init__(self, pipeline_id: str) -> None:
        super().__init__()
        self.pipeline_id = pipeline_id

    def process(self, data: Any) -> str:
        result = data
        for stage in self.stages:
            result = stage.process(result)
        return f"[JSONAdapter-{self.pipeline_id}] {result}"


class CSVAdapter(ProcessingPipeline):
    def __init__(self, pipeline_id: str) -> None:
        super().__init__()
        self.pipeline_id = pipeline_id

    def process(self, data: Any) -> str:
        result = data
        for stage in self.stages:
            result = stage.process(result)
        return f"[CSVAdapter-{self.pipeline_id}] {result}"


class StreamAdapter(ProcessingPipeline):
    def __init__(self, pipeline_id: str) -> None:
        super().__init__()
        self.pipeline_id = pipeline_id

    def process(self, data: Any) -> str:
        result = data
        for stage in self.stages:
            result = stage.process(result)
        return f"[StreamAdapter-{self.pipeline_id}] {result}"


# Manager to orchestrate multiple pipelines
class NexusManager:
    def __init__(self) -> None:
        self.pipelines: List[ProcessingPipeline] = []

    def add_pipeline(self, pipeline: ProcessingPipeline) -> None:
        self.pipelines.append(pipeline)

    def process_all(self, data: Any) -> None:
        for pipeline in self.pipelines:
            try:
                output = pipeline.process(data)
                print(output)
            except Exception as e:
                print(f"Error in pipeline: {e}")

    def process_all_concatenate(self, initial_data: Any) -> None:
        data = initial_data
        for idx, pipeline in enumerate(self.pipelines):
            try:
                print(f"\n--- Processing Pipeline {idx + 1} ---")
                data = pipeline.process(data)
                print(f"Pipeline output: {data}")
            except Exception as e:
                print(f"Error in pipeline: {e}")
                # Recovery logic could be added here
        print("\n=== All pipelines processed successfully ===")

# Example usage
if __name__ == "__main__":
    print("=== CODE NEXUS - ENTERPRISE PIPELINE SYSTEM ===")

    # Create manager
    manager = NexusManager()

    # JSON pipeline
    json_pipeline = JSONAdapter("JSON_001")
    json_pipeline.add_stage(InputStage())
    json_pipeline.add_stage(TransformStage())
    json_pipeline.add_stage(OutputStage())
    manager.add_pipeline(json_pipeline)

    # CSV pipeline
    csv_pipeline = CSVAdapter("CSV_001")
    csv_pipeline.add_stage(InputStage())
    csv_pipeline.add_stage(TransformStage())
    csv_pipeline.add_stage(OutputStage())
    manager.add_pipeline(csv_pipeline)

    # Stream pipeline
    stream_pipeline = StreamAdapter("STREAM_001")
    stream_pipeline.add_stage(InputStage())
    stream_pipeline.add_stage(TransformStage())
    stream_pipeline.add_stage(OutputStage())
    manager.add_pipeline(stream_pipeline)

    # Process all pipelines
    manager.process_all("Raw Data")
    manager.process_all_concatenate("Raw Data")
