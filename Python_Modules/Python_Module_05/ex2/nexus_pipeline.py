from abc import ABC, abstractmethod
from typing import Any, List, Optional, Union, Dict
from typing import Protocol


class ProcessingPipeline(ABC):
    """abstract base class"""
    def __init__(self, id: str):
        """initialise"""
        self.pipeline_id = id
        self.stages = List[ProcessingStage] = []

    @abstractmethod
    def process(self, data: Any) -> Any:
        """abstract so in subclasses"""
        pass


class ProcessingStage(Protocol):
    """contains stages"""

    def process(self, data: Any) -> Any:
        ...


class InputStage():
    """ """
    def process(self, data: Any) -> Dict:
        """InputStage"""



class TransformStage():
    """ """
    def process(self, data: Any) -> Dict:
        """TransformStage"""


class OutputStage():
    """ """
    def process(self, data: Any) -> str:
        """OutputStage"""


class JSONAdapter(ProcessingPipeline):
    def __init__(self, id):
        super().__init__(id)
        pass

    def process(self, data: Any) -> Union[str, Any]:
        """overriding parent-process"""


class CSVAdapter(ProcessingPipeline):
    def __init__(self, id):
        super().__init__(id)
        pass

    def process(self, data: Any) -> Union[str, Any]:
        """overriding parent-process"""


class StreamAdapter(ProcessingPipeline):
    def __init__(self, id):
        super().__init__(id)
        pass

    def process(self, data: Any) -> Union[str, Any]:
        """overriding parent-process"""


class NexusManager():
    """multiple pipelines"""
    pass


if __name__ == "__name__":
    """main"""
    pass
