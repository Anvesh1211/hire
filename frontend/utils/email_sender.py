# utils/email_sender.py
from alerts.GmailAlertService_v2 import GmailAlertServiceV2

def send_sar_email(case_data: dict, recipient_email: str) -> dict:
    """
    Send SAR report details to a specified email before final SAR generation.
    """
    service = GmailAlertServiceV2()

    subject = f"SAR Report Notification - Case {case_data.get('case_id', 'UNKNOWN')}"

    customer_profile = case_data.get('customer_profile', {})
    reasoning = case_data.get('reasoning_results', "No reasoning generated yet")
    risk_score = case_data.get('detection_results', {}).get('risk_score', "N/A")

    body = f"""
    Dear Compliance Officer,

    A new SAR case has been generated in ProofSAR AI.

    Case ID: {case_data.get('case_id', 'N/A')}
    Customer Name: {customer_profile.get('customer_name', 'N/A')}
    Account Number: {customer_profile.get('account_number', 'N/A')}
    Risk Score: {risk_score}

    Reasoning Summary:
    {reasoning}

    Please review this case for compliance purposes.

    Regards,
    ProofSAR AI
    """

    response = service.send_alert(
        alert_type="SAR_NOTIFICATION",
        case_id=case_data.get('case_id', 'UNKNOWN'),
        subject=subject,
        body=body,
        recipients=[recipient_email]
    )

    return response
