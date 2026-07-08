import africastalking
import logging
from django.conf import settings

logger = logging.getLogger(__name__)


def init_sms():
    africastalking.initialize(
        username=settings.AFRICASTALKING_USERNAME,
        api_key=settings.AFRICASTALKING_API_KEY,
    )
    return africastalking.SMS


def send_sms(phone, message):
    """
    Send a single SMS. Returns True on success, False on failure.
    Never raises — app continues even if SMS fails.
    """
    if not phone:
        logger.warning("SMS skipped — no phone number provided.")
        return False

    # ensure number starts with +234
    if phone.startswith('0'):
        phone = '+234' + phone[1:]
    elif not phone.startswith('+'):
        phone = '+234' + phone

    try:
        sms      = init_sms()
        response = sms.send(message, [phone])
        logger.info(f"SMS sent to {phone}: {response}")
        return True
    except Exception as e:
        logger.error(f"SMS failed to {phone}: {e}")
        return False


# ─────────────────────────────────────────
# NOTIFICATION FUNCTIONS
# ─────────────────────────────────────────

def notify_student_status_change(application):
    """
    Notify student when company updates their application status.
    """
    student = application.student
    phone   = student.user.phone
    print(f"DEBUG: Notifying student {student.user.get_full_name()} at {phone} about status change to '{application.status}'.")
    status_messages = {
        'reviewed': (
            f"Hi {student.user.first_name}, your SIWES application to "
            f"{application.listing.company.company_name} for "
            f"'{application.listing.title}' has been reviewed. "
            f"Log in to check your status."
        ),
        'offered': (
            f"Congratulations {student.user.first_name}! "
            f"{application.listing.company.company_name} has offered you "
            f"the '{application.listing.title}' SIWES placement. "
            f"Log in to accept or decline this offer."
        ),
        'accepted': (
            f"Hi {student.user.first_name}, your SIWES application to "
            f"{application.listing.company.company_name} for "
            f"'{application.listing.title}' has been accepted. "
            f"Log in for more details."
        ),
        'rejected': (
            f"Hi {student.user.first_name}, your SIWES application to "
            f"{application.listing.company.company_name} for "
            f"'{application.listing.title}' was not successful. "
            f"Log in to search for other placements."
        ),
    }

    message = status_messages.get(application.status)
    if message:
        send_sms(phone, message)


def notify_admin_offer_accepted(application):
    """
    Notify admin and SIWES office when a student accepts a placement offer.
    """
    student = application.student
    company = application.listing.company

    message = (
        f"SIWES PLACEMENT UPDATE: "
        f"{student.user.get_full_name()} ({student.matric_number}) "
        f"from {student.institution} has accepted a placement offer from "
        f"{company.company_name} for '{application.listing.title}' "
        f"in {application.listing.lga}, {application.listing.state}."
    )

    admin_phone      = getattr(settings, 'ADMIN_PHONE', None)
    siwes_office     = getattr(settings, 'SIWES_OFFICE_PHONE', None)

    if admin_phone:
        send_sms(admin_phone, message)

    if siwes_office and siwes_office != admin_phone:
        send_sms(siwes_office, message)


def notify_company_offer_response(application):
    """
    Notify company contact when student responds to an offer.
    """
    student  = application.student
    company  = application.listing.company
    phone    = company.user.phone

    if application.status == 'offer_accepted':
        message = (
            f"SIWES Portal: {student.user.get_full_name()} has ACCEPTED "
            f"your placement offer for '{application.listing.title}'. "
            f"Please contact them to proceed with onboarding."
        )
    elif application.status == 'offer_declined':
        message = (
            f"SIWES Portal: {student.user.get_full_name()} has DECLINED "
            f"your placement offer for '{application.listing.title}'."
        )
    else:
        return

    send_sms(phone, message)