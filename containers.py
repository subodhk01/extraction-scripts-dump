from dependency_injector.containers import DeclarativeContainer
from dependency_injector.providers import Singleton

from common.boto3_session import Boto3Session
from services.s3 import S3
from services.extract_domain import ExtractDomainService
from services.email_verify import VerifyEmailService
from services.email_creator import CreateEmailService

class ExtractionContainer(DeclarativeContainer):
    session: Boto3Session = Singleton(Boto3Session)
    s3: S3 = Singleton(S3, session=session().session)
    extract_domain = Singleton(ExtractDomainService)
    email_creator = Singleton(CreateEmailService)
    email_verify = Singleton(VerifyEmailService, source_addr="")