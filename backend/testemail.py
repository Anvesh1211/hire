from alerts.GmailAlertService_v2 import GmailAlertServiceV2

service = GmailAlertServiceV2()

response = service.send_alert(
    alert_type="TEST_ALERT",
    case_id="CASE_001",
    subject="SMTP Test Email",
    body="If you received this email then the Profsar email serive by Anvesh GmailAlertServiceV2 is fully operational.",
    recipients=["anveshchaurpagar193@gmail.com"]  # must be a LIST
)

print(response)