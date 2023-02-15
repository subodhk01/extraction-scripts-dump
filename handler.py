import sys, csv, requests, time, threading
from slugify import slugify
from dotenv import load_dotenv
load_dotenv()

from containers import ExtractionContainer

BACKEND_URL = "https://api.massemail.pro"
# BACKEND_URL = "http://localhost:8000"

BUCKET_NAME = "emailer-backend-static"
FOUND_ENTRIES_UPLOAD_PATH = "extraction_data/{extraction_id}/stage2/output.csv"
FAILED_ENTRIES_UPLOAD_PATH = "extraction_data/{extraction_id}/stage2/failed_entries.csv"

FOUND_ENTRIES_OUTPUT_FILE = "output.csv"
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

def process_data(data):
    for line in data:
        data_found = False
        try:
            line = line.strip()
            name = line.split(",")[0]
            
            first_name = name.split(" ")[0].lower().replace(" ", "").replace(".", "").strip()
            first_name = slugify(first_name)

            last_name = name.split(" ")[-1].lower().replace(" ", "").replace(".", "").strip()
            last_name = slugify(last_name)

            company_name = line.split(",")[2]
            if not company_name:
                print("No company name found for: ", first_name, last_name)
                with open('failed_entries.csv', 'a') as f:
                    f.write(f"{first_name},{last_name},No company name found\n")
                continue
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
                    # print('\t\tResult: ', email_verify_result)
                    if email_verify_result['catch_all']:
                        is_catch_all_domain = True
                        print(f"\t{domain} - Catch all domain found")
                    elif email_verify_result.get('message'):
                        is_error = True
                        print(f"\t{domain} - Error: {email_verify_result['message']}")
                    elif email_verify_result['deliverable']:
                        data_found = True
                        print(f"\t*** Email found: {email} ***")
                        with open(FOUND_ENTRIES_OUTPUT_FILE, 'a') as f:
                            f.write(f"{first_name},{last_name},{company_name},{email}\n")
                        break
            
            if not data_found:
                with open(FAILED_ENTRIES_OUTPUT_FILE, 'a') as f:
                    f.write(f"{first_name},{last_name},{company_name},Email not found\n")
        except Exception as e:
            print("Error: ", e)
            with open(FAILED_ENTRIES_OUTPUT_FILE, 'a') as f:
                f.write(f"{first_name},{last_name},{company_name},Error: {e}\n")

if __name__ == "__main__":
    extraction_id = sys.argv[1]
    offset = int(sys.argv[2]) if len(sys.argv) > 2 else 0

    # clear_output_files()

    data_file = "data2.csv"
    file_key = "extraction_data/{extraction_id}/stage1/output.csv".format(extraction_id=extraction_id)
    s3.download_file(
        bucket=BUCKET_NAME, key=file_key, download_path=data_file
    )

    data = []
    
    with open(data_file, "r") as f:
        data = f.readlines()
    
    data = data[offset:]
    
    start_time = time.perf_counter()
    threads = []
    for i in range(0, 10):
        t = threading.Thread(target=process_data, args=(data[i::10],))
        threads.append(t)
        t.start()
    for t in threads:
        t.join()
    end_time = time.perf_counter()
    print(f"Total time: {end_time - start_time} seconds")

    data = data[offset+1:]
    process_data(data)
        

    print("starting found entries file upload to s3")
    s3.upload_object(
        BUCKET_NAME, FOUND_ENTRIES_UPLOAD_PATH.format(extraction_id=extraction_id), FOUND_ENTRIES_OUTPUT_FILE
    )
    r = requests.post(
        f"{BACKEND_URL}/extraction/stage2/complete/",
        json={
            "uuid": extraction_id,
            "result_file_url": f"https://{BUCKET_NAME}.s3.amazonaws.com/{FOUND_ENTRIES_UPLOAD_PATH.format(extraction_id=extraction_id)}"
        }
    )
    print("found entries backend response: ", r)

    print("starting failed entries file upload to s3")
    s3.upload_object(
        BUCKET_NAME, FAILED_ENTRIES_UPLOAD_PATH.format(extraction_id=extraction_id), FAILED_ENTRIES_OUTPUT_FILE
    )
    r = requests.post(
        f"{BACKEND_URL}/extraction/stage2/failed/",
        json={
            "uuid": extraction_id,
            "result_file_url": f"https://{BUCKET_NAME}.s3.amazonaws.com/{FAILED_ENTRIES_UPLOAD_PATH.format(extraction_id=extraction_id)}"
        }
    )
    print("failed entries backend response: ", r)

        