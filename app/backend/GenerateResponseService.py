import vertexai
from vertexai.generative_models import GenerativeModel
from ContextMatcherService import MockContextMatcherService
import os


class LanguageModelService:
    def __init__(self):
        vertexai.init(project="gentle-cable-441612-q2", location="europe-central2")
        self.model = GenerativeModel("gemini-1.5-flash-002")

        self.law_domains = self._read_law_domains("law_domains.txt")

        self.context_matcher = MockContextMatcherService() #TODO: change for real implementation

    def _read_law_domains(self, filepath):
        """Read the list of law domains from a text file."""
        try:
            with open(filepath, 'r', encoding='utf-8') as file:
                domains = [line.strip() for line in file if line.strip()]
            return domains
        except FileNotFoundError:
            raise Exception(f"Law domains file not found at {filepath}")
        except Exception as e:
            raise Exception(f"Error reading law domains: {e}")

    def _match_law_domain(self, question):
        """Match the user's question to a law domain using the language model."""
        prompt = (
            f"Given the following list of law domains:\n"
            f"{', '.join(self.law_domains)}.\n\n"
            f"Determine which law domain best fits the question below.\n"
            f"Provide only the law domain name in your response.\n\n"
            f"Question: {question}"
        )

        response = self.model.generate_content(prompt)
        matched_domain = response.text.strip().lower()
        # Validate the matched domain
        if matched_domain in self.law_domains:
            return matched_domain
        else:
            raise Exception(f"Model returned an invalid law domain: {matched_domain}")

    def _read_pdf_contents(self, pdf_files):
        from PyPDF2 import PdfReader  # for mock purposes

        content = ""
        for pdf_file in pdf_files:
            try:
                reader = PdfReader(pdf_file)
                for page in reader.pages:
                    content += page.extract_text()
            except Exception as e:
                print(f"Error reading {pdf_file}: {e}")
        return content

    def get_model_response(self, question):
        """Main method to get the model's response to the user's question."""
        try:

            law_domain = self._match_law_domain(question)
            print(f"Matched Law Domain: {law_domain}")

            pdf_files = self.context_matcher.create_matching_context(law_domain)
            if not pdf_files:
                raise Exception(f"No PDF files found for law domain: {law_domain}")

            context = self._read_pdf_contents(pdf_files)

            final_prompt = (
                f"You are a legal assistant specializing in {law_domain}.\n"
                f"Based on the following documents, answer the user's question.\n\n"
                f"Documents:\n{context}\n\n"
                f"Question: {question}\n"
                f"Answer:"
            )

            response = self.model.generate_content(final_prompt)
            answer = response.text.strip()
            return answer

        except Exception as e:
            return f"An error occurred: {e}"
