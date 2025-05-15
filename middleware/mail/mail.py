import os
import sendgrid
from sendgrid.helpers.mail import Mail, Email, To, Content
from dotenv import load_dotenv
from middleware.mail.mail_temp import TEMPLATE_WELCOME_MAIL, TEMPLATE_RESET_MAIL
from middleware.auth.tokencreation import register_mail_token, forgot_mail_token

load_dotenv()  # Load environment variables

sg = sendgrid.SendGridAPIClient(api_key=os.getenv("SENDGRID_API_KEY"))

# Send Registration Email
def send_register_email(email, name, type):
    try:
        print("send_register_email")

        token_data = {'email': email, 'name': name}
        token = register_mail_token(token_data)
        print("token",token)

        verification_url = f"{os.getenv('STATIC_URL')}/password?token={token}#type=register"


        html_content = TEMPLATE_WELCOME_MAIL(name, verification_url)

        msg = Mail(
            from_email=os.getenv('EMAIL_FROM'),
            to_emails=email,
            subject="Linkedin - Verify Your Email and Set Your Password",
            plain_text_content=f"Hello {name},\n\nWelcome! Click the link below to verify your email and set your password:\n\n{verification_url}",
            html_content=html_content
        )

        # Send the email
        response = sg.send(msg)
        print("Register email sent successfully ✅")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")

    except Exception as error:
        print(f"Error sending register email ❌: {str(error)}")
        raise Exception('Error sending register email')


# Send Forgot Password Email
def send_forgot_email(email, name):
    try:
        print("send_forgot_email")

        token_data = {'email': email, 'name': name}
        token = forgot_mail_token(token_data)
        print(token)

        verification_url = f"{os.getenv('STATIC_URL')}/password?token={token}#type=forgot"

        html_content = TEMPLATE_RESET_MAIL(name, verification_url)

        msg = Mail(
            from_email=os.getenv('EMAIL_FROM'),
            to_emails=email,
            subject="Linkedin - Reset Your Password",
            plain_text_content=f"Hello {name},\n\nClick the link below to reset your password:\n\n{verification_url}",
            html_content=html_content
        )

        # Send the email
        response = sg.send(msg)
        print("Forgot password email sent successfully ✅")
        print(f"Status Code: {response.status_code}")
        print(f"Response Body: {response.body}")
        print(f"Response Headers: {response.headers}")

    except Exception as error:
        print(f"Error sending forgot password email ❌: {str(error)}")
        raise Exception('Error sending forgot password email')

