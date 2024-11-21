from abc import ABC, abstractmethod


class ContextMatcherService(ABC):
    @abstractmethod
    def create_matching_context(self, keywords):
        pass


class MockContextMatcherService(ContextMatcherService):
    def create_matching_context(self, keywords):
        return ["dziennik_ustaw/2000/D2000122131001.pdf", "dziennik_ustaw/2000/D2000122131101.pdf"]
