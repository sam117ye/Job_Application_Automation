import unittest
from unittest.mock import patch, MagicMock
from bs4 import BeautifulSoup
import requests
from scrappy import get_job_ids, get_job_details

class TestScrappy(unittest.TestCase):

    @patch('requests.get')
    @patch('bs4.BeautifulSoup')
    def test_get_job_ids(self, mock_beautifulsoup, mock_requests_get):
        # Mock response from requests.get
        mock_response = MagicMock()
        mock_response.text = 'mocked response'
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_beautifulsoup.return_value = mock_soup

        # Mock find_all result
        mock_job_li = MagicMock()
        mock_job_li.find_all.return_value = [
            MagicMock(attrs={'class': 'base-card', 'data-entity-urn': 'urn:li:job:12345'}),
            MagicMock(attrs={'class': 'base-card', 'data-entity-urn': 'urn:li:job:67890'})
        ]
        mock_soup.find_all.return_value = [mock_job_li]

        # Call function
        job_ids = get_job_ids(page_number=0, title='engineer', location='New York')

        # Assertions
        self.assertEqual(job_ids, ['12345', '67890'])
        mock_requests_get.assert_called_once_with(
            'https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search?keywords=engineer&location=New York&start=0'
        )
        mock_beautifulsoup.assert_called_once_with('mocked response', 'html.parser')
        mock_soup.find_all.assert_called_once_with('li')

    @patch('requests.get')
    def test_get_job_details_success(self, mock_requests_get):
        # Mock response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 200
        mock_response.text = 'mocked response'
        mock_requests_get.return_value = mock_response

        # Mock BeautifulSoup
        mock_soup = MagicMock()
        mock_beautifulsoup = MagicMock(return_value=mock_soup)

        with patch('scrappy.BeautifulSoup', mock_beautifulsoup):
            # Mock find results
            mock_soup.find.return_value = MagicMock(text='Job Title')
            mock_soup.find_all.return_value = [
                MagicMock(text='Company Name'),
                MagicMock(text='Company Location'),
                MagicMock(text='Seniority Level'),
                MagicMock(text='Employment Type'),
                MagicMock(text='Job Description')
            ]

            # Call function
            job_details = get_job_details(job_id='12345')

            # Assertions
            self.assertEqual(job_details['job_title'], 'Job Title')
            self.assertEqual(job_details['company_name'], 'Company Name')
            self.assertEqual(job_details['company_location'], 'Company Location')
            self.assertEqual(job_details['seniority_level'], 'Seniority Level')
            self.assertEqual(job_details['employment_type'], 'Employment Type')
            self.assertEqual(job_details['job_description'], 'Job Description')
            mock_requests_get.assert_called_once_with(
                'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/12345'
            )

    @patch('requests.get')
    def test_get_job_details_not_found(self, mock_requests_get):
        # Mock response from requests.get
        mock_response = MagicMock()
        mock_response.status_code = 404
        mock_requests_get.return_value = mock_response

        # Call function
        job_details = get_job_details(job_id='12345')

        # Assertions
        self.assertIsNone(job_details)
        mock_requests_get.assert_called_once_with(
            'https://www.linkedin.com/jobs-guest/jobs/api/jobPosting/12345'
        )

if __name__ == '__main__':
    unittest.main()


