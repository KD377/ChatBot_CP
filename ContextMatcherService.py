from abc import ABC, abstractmethod
class ContextMatcherService(ABC):
    @abstractmethod
    def create_matching_context(self, keywords):
        pass
