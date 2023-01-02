from boto3 import Session

ACCESS_KEY = "AKIA34ZZEVZ6BCEAKY7T"
SECRET_KEY = "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"


class Boto3Session:
    session = Session(
        aws_access_key_id=ACCESS_KEY,
        aws_secret_access_key=SECRET_KEY,
        region_name="ap-south-1",
    )