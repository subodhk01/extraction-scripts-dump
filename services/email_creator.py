EMAIL_COMBINATIONS = [
    lambda first_name, last_name, company_domain: f"{first_name}.{last_name}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{first_name}{last_name}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{first_name}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{last_name}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{first_name[0]}{last_name}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{first_name[0]}.{last_name}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{first_name}{last_name[0]}@{company_domain}",
    lambda first_name, last_name, company_domain: f"{first_name}.{last_name[0]}@{company_domain}",
]

class CreateEmailService:
    def create_emails(self, data):
        return [email_combination(data['first_name'], data['last_name'], data['company_domain']) for email_combination in EMAIL_COMBINATIONS]

# p1 = Person("Subodh", "Verma", "Company")

# email_combinations_generator = CreateEmailService(p1)
# for email in email_combinations_generator.generate():
#     print(email)
