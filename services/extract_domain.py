from bs4 import BeautifulSoup
import requests

class ExtractDomainService:
    def domain_search_1(self, company_name):
        url = 'https://www.google.com/search'
        headers = {
            'Accept' : '*/*',
            'Accept-Language': 'en-US,en;q=0.5',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/98.0.4758.82',
        }
        parameters = {'q': company_name}

        content = requests.get(url, headers = headers, params = parameters).text
        soup = BeautifulSoup(content, 'html.parser')

        search = soup.find(id = 'search')
        first_link = search.find('a')

        domain = first_link['href']
        domain = domain.split('/')[2]
        domain = domain.split('www.')[-1]
        return domain

    def domain_search_2(self, company_name):
        response = requests.get(f'https://autocomplete.clearbit.com/v1/companies/suggest?query={company_name}')
        data = response.json()
        if len(data) > 0:
            domain = data[0]['domain']
            return domain
        else:
            print(f'No domain found for {company_name} in domain_search_2')
            return None

    def extract_domains(self, company_name):
        domains = []
        domains.append(self.domain_search_1(company_name))
        domains.append(self.domain_search_2(company_name))
        domains = list(set([domain for domain in domains if domain is not None]))
        return domains