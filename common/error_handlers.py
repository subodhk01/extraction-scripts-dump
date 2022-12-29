blocked_keywords = [
    "spamhaus",
    "proofpoint",
    "cloudmark",
    "banned",
    "blacklisted",
    "blocked",
    "block list",
    "denied"
]

####
# SMTP RCPT error handlers
####
def handle_550(response):
    if any([keyword.encode() in response for keyword in blocked_keywords]):
        return dict(message="Blocked by mail server", deliverable=False, host_exists=True)
    else:
        return dict(deliverable=False, host_exists=True)


# https://www.greenend.org.uk/rjk/tech/smtpreplies.html#RCPT
# https://sendgrid.com/blog/smtp-server-response-codes-explained/
# Most of these errors return a dict that should be merged with 'lookup' afterwards
handle_error = {
    # 250 and 251 are not errors
    550: handle_550,
    551: lambda _: dict(deliverable=False, host_exists=True),
    552: lambda _: dict(deliverable=True, host_exists=True, full_inbox=True),
    553: lambda _: dict(deliverable=False, host_exists=True),
    450: lambda _: dict(deliverable=False, host_exists=True),
    451: lambda _: dict(deliverable=False, message="Local error processing, try again later."),
    452: lambda _: dict(deliverable=True, full_inbox=True),
    # Syntax errors
    # 500 (command not recognised)
    # 501 (parameter/argument not recognised)
    # 503 (bad command sequence)
    521: lambda _: dict(deliverable=False, host_exists=False),
    421: lambda _: dict(deliverable=False, host_exists=True, message="Service not available, try again later."),
    441: lambda _: dict(deliverable=True, full_inbox=True, host_exists=True)
}

handle_unrecognised = lambda a: dict(message=f"Unrecognised error: {a}", deliverable=False)
