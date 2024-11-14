from abc import ABC, abstractmethod


class ContextMatcherService(ABC):
    @abstractmethod
    def create_matching_context(self, keywords):
        pass


class MockContextMatcherService(ContextMatcherService):
    def create_matching_context(self, keywords):
        return ["dziennik_ustaw/2010/D2010259176201.pdf", "dziennik_ustaw/2010/D2010259176301.pdf",
                "dziennik_ustaw/2010/D2010259176401.pdf"]
