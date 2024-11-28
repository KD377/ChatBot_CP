import sys
from unittest.mock import Mock, patch

import pytest

sys.modules['ExtendedContextMatcherService'] = Mock()

from ..GenerateResponseService import LanguageModelService


class TestLanguageModelService:

    @patch('app.backend.GenerateResponseService.LanguageModelService._read_law_domains',
           return_value=['prawo cywilne', 'prawo dupy', 'prawo ulicy'])
    @patch('app.backend.GenerateResponseService.GenerativeModel.generate_content')
    def test_match_law_domain_valid(self, mock_generate_content, mock_read_law_domains):
        mock_response = Mock()
        mock_response.text = 'prawo cywilne'

        mock_generate_content.return_value = mock_response

        service = LanguageModelService()

        matched_domain = service._match_law_domain(
            'co grozi za nie płacenie podatku VAT')

        assert matched_domain == 'prawo cywilne'

    @patch('app.backend.GenerateResponseService.LanguageModelService._read_law_domains',
           return_value=['prawo cywilne', 'prawo karne', 'prawo rodzinne'])
    @patch('app.backend.GenerateResponseService.GenerativeModel.generate_content')
    def test_match_law_domain_invalid(self, mock_generate_content, mock_read_law_domains):
        mock_response = Mock()
        mock_response.text = 'invalid law'

        mock_generate_content.return_value = mock_response

        service = LanguageModelService()

        with pytest.raises(Exception) as excinfo:
            service._match_law_domain('co grozi za nie płacenie podatku VAT')

        assert 'Model returned an invalid law domain: invalid law' in str(excinfo.value)
