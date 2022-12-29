import requests

class Person:
    def __init__(self, first_name, last_name, company_name):
        self.first_name = first_name.lower().replace(" ", "").strip()
        self.last_name = last_name.lower().replace(" ", "").strip()
        self.company_name = company_name
        # TODO company domain
        self.company_domain = company_name.lower().replace(" ", "")

    def __str__(self):
        return f"{self.first_name} {self.last_name} {self.company_name}"

EMAIL_COMBINATIONS = [
    lambda person: f"{person.first_name}.{person.last_name}@{person.company_domain}.com",
    lambda person: f"{person.first_name}{person.last_name}@{person.company_domain}.com",
    lambda person: f"{person.first_name}@{person.company_domain}.com",
    lambda person: f"{person.first_name[0]}{person.last_name}@{person.company_domain}.com",
    lambda person: f"{person.first_name[0]}.{person.last_name}@{person.company_domain}.com",
    lambda person: f"{person.first_name}{person.last_name[0]}@{person.company_domain}.com",
    lambda person: f"{person.first_name}.{person.last_name[0]}@{person.company_domain}.com",
]

class EmailCombinationsGenerator:
    def __init__(self, person):
        self.person = person

    def generate(self):
        return [email_combination(self.person) for email_combination in EMAIL_COMBINATIONS]

p1 = Person("Subodh", "Verma", "Company")

email_combinations_generator = EmailCombinationsGenerator(p1)
for email in email_combinations_generator.generate():
    print(email)
