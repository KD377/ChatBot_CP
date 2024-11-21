from ContextMatcherService import ContextMatcherService
from MongoDBHandler import MongoDBHandler


class ExtendedContextMatcherService(MongoDBHandler, ContextMatcherService):

    def __init__(self):
        super().__init__()

    def create_matching_context(self, keywords):
        return self.get_files_by_legal_field(keywords)


def main():
    db_handler = ExtendedContextMatcherService()

    legal_field_value = "prawo finansowe"
    file_names = db_handler.create_matching_context(legal_field_value)
    print("Znalezione pliki:", file_names)


if __name__ == "__main__":
    main()
