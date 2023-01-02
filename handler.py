import sys, csv

from containers import ExtractionContainer

BUCKET_NAME = "emailer-backend-static"
FOUND_ENTRIES_UPLOAD_PATH = "extraction_data/stage2/{extraction_id}/found_entries.csv"
FAILED_ENTRIES_UPLOAD_PATH = "extraction_data/stage2/{extraction_id}/failed_entries.csv"

FOUND_ENTRIES_OUTPUT_FILE = "found_entries.csv"
FAILED_ENTRIES_OUTPUT_FILE = "failed_entries.csv"

def clear_output_files():
    with open(FOUND_ENTRIES_OUTPUT_FILE, "w") as f:
        f.write("first_name,last_name,company_name,email\n")
    with open(FAILED_ENTRIES_OUTPUT_FILE, "w") as f:
        f.write("first_name,last_name,company_name,message\n")

extraction_container = ExtractionContainer()

s3 = extraction_container.s3()
extract_domain = extraction_container.extract_domain()
email_creator = extraction_container.email_creator()
email_verify = extraction_container.email_verify()

if __name__ == "__main__":
    file_key = sys.argv[1]
    extraction_id = sys.argv[2]
    clear_output_files()

    data_file = "data2.csv"
    s3.download_file(
        bucket=BUCKET_NAME, key=file_key, download_path=data_file
    )
    
    with open(data_file, "r") as f:
        data = f.readlines()
        data = data[1:]
        for line in data:
            data_found = False

            line = line.strip()
            first_name = line.split(",")[0].lower().replace(" ", "").strip()
            last_name = line.split(",")[1].lower().replace(" ", "").strip()
            company_name = line.split(",")[2]
            domains = extract_domain.extract_domains(company_name)

            # if no domains found, skip
            if not domains:
                print("No domains found for company: ", company_name)
                with open('failed_entries.csv', 'a') as f:
                    f.write(f"{first_name},{last_name},{company_name},No domains found for company\n")
                continue
            
            print(f"----------------------------\n\nChecking for {first_name} {last_name} at {company_name} {domains}")
            for domain in domains:
                print('\nGenerating emails for domain: ', domain)
                is_catch_all_domain = False
                is_error = False
                emails = email_creator.create_emails({
                    "first_name": first_name,
                    "last_name": last_name,
                    "company_domain": domain,
                })
                for email in emails:
                    if is_catch_all_domain:
                        print('\tSkipping email: ', email)
                        continue
                    if is_error:
                        print('\tSkipping email: ', email)
                        continue
                    print('\tChecking email: ', email)
                    email_verify_result = email_verify.verify(email)
                    if email_verify_result['catch_all']:
                        is_catch_all_domain = True
                        print(f"\t{domain} - Catch all domain found")
                    elif email_verify_result.get('message'):
                        is_error = True
                        print(f"\t{domain} - Error: {email_verify_result['message']}")
                    elif email_verify_result['deliverable']:
                        data_found = True
                        print("\t*** Email found: {email} ***")
                        with open(FOUND_ENTRIES_OUTPUT_FILE, 'a') as f:
                            f.write(f"{first_name},{last_name},{company_name},{email}\n")
                        break
            
            if not data_found:
                with open(FAILED_ENTRIES_OUTPUT_FILE, 'a') as f:
                    f.write(f"{first_name},{last_name},{company_name},Email not found\n")

    s3.upload_object(
        BUCKET_NAME, FOUND_ENTRIES_UPLOAD_PATH.format(extraction_id=extraction_id), FOUND_ENTRIES_OUTPUT_FILE
    )
    s3.upload_object(
        BUCKET_NAME, FAILED_ENTRIES_UPLOAD_PATH.format(extraction_id=extraction_id), FAILED_ENTRIES_OUTPUT_FILE
    )

        