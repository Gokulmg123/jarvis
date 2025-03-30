import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import subprocess
import google.generativeai as genai

# Securely configure Gemini API
genai.configure(api_key="AIzaSyAa8E8dLIcExVhRLZ_uXEEwfR_xG5L2GDE")


def email(subject):

    def OpenNotepad(File):
        default_text_editor = 'notepad.exe'
        subprocess.Popen([default_text_editor, File]) 

    def generate_email(subject):
        """Generates an email body using Gemini AI based on the subject."""
        model = genai.GenerativeModel("gemini-1.5-pro")
        prompt = f"Write a professional email about {subject}. End with a proper closing statement."
        response = model.generate_content(prompt)

        return response.text.strip() if response and hasattr(response, "text") and response.text else "Error generating email content."
    
    email_text = generate_email(subject)  # ✅ Call the function and store the output
    
    file_path = rf"Data\{subject.lower().replace(' ','')}.txt"

    with open(file_path, "w", encoding="utf-8") as file:
        file.write(email_text)

    OpenNotepad(file_path)

    return email_text  # ✅ Return the generated email



def sendmail(subject):
    """Gets email details from user and sends an email with AI-generated content."""
    receiver_email = input("Enter recipient email: ")
    #subject = input("Enter email subject: ")
    
    body = email(subject)
    print("\nGenerated Email:\n", body)

    sender_email = "pmajor391@gmail.com"  # Use environment variable
    sender_password = "czwkmlgalyervtte"  # Use App Password

    if not sender_email or not sender_password:
        print("❌ Missing email credentials. Set EMAIL_ADDRESS and EMAIL_PASSWORD as environment variables.")
        return

    # Create email message
    msg = MIMEMultipart()
    msg["From"] = sender_email
    msg["To"] = receiver_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    try:
        server = smtplib.SMTP("smtp.gmail.com", 587)
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, receiver_email, msg.as_string())
        server.quit()
        print(f"✅ Email sent to {receiver_email}")
    except Exception as e:
        print(f"❌ Failed to send email: {e}")

# Example usage
if __name__ == "__main__":
    sendmail()
   
