import bcrypt
import random
import string
import smtplib
from email.mime.text import MIMEText
from sqlalchemy.orm import Session
from models import User

# Temporary storage for recovery codes
recovery_codes = {}

def hash_password(password: str) -> str:
    """Hash a password using bcrypt."""
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

def verify_password(stored_password: str, provided_password: str) -> bool:
    """Verify a stored password against the provided password."""
    return bcrypt.checkpw(provided_password.encode('utf-8'), stored_password.encode('utf-8'))

def register_user(db: Session, username: str, password: str, email: str) -> User:
    """Register a new user with a hashed password."""
    hashed_password = hash_password(password)
    new_user = User(username=username, password_hash=hashed_password, email=email)
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user

def login_user(db: Session, username: str, password: str) -> User:
    """Authenticate a user by verifying username and password."""
    user = db.query(User).filter(User.username == username).first()
    if user and verify_password(user.password_hash, password):
        return user
    return None

def delete_user(db: Session, username: str) -> bool:
    """Delete a user account by username."""
    user = db.query(User).filter(User.username == username).first()
    if user:
        db.delete(user)
        db.commit()
        return True
    return False

def generate_recovery_code(length=6) -> str:
    """Generate a random recovery code consisting of uppercase letters and digits."""
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

def send_recovery_email(email: str, recovery_code: str):
    """Send a recovery email with the recovery code."""
    msg = MIMEText(f'Your recovery code is: {recovery_code}')
    msg['Subject'] = 'Password Recovery Code'
    msg['From'] = 'your_email@gmail.com'  # Replace with your email
    msg['To'] = email

    # Use Gmail's SMTP server to send the email
    try:
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade to a secure connection
            server.login('your_email@gmail.com', 'your_app_password')  # Use your email and app password
            server.send_message(msg)
            print("Recovery email sent successfully.")
    except smtplib.SMTPException as e:
        print(f"Error sending email: {e}")

def recover_password(db: Session, username: str) -> bool:
    """Recover user password by sending a recovery code and updating the password."""
    user = db.query(User).filter(User.username == username).first()
    if user:
        recovery_code = generate_recovery_code()
        send_recovery_email(user.email, recovery_code)

        # Store the recovery code temporarily for validation
        recovery_codes[username] = recovery_code

        # Prompt user to input the recovery code
        user_input_code = input("Enter the recovery code sent to your email: ")

        # Verify the recovery code
        if user_input_code == recovery_codes.get(username):
            new_password = input("Enter your new password: ")
            user.password_hash = hash_password(new_password)  # Hash the new password
            db.commit()  # Save the new password hash
            print('Your password has been reset successfully.')
            del recovery_codes[username]  # Clear the recovery code after use
            return True
        else:
            print('Error: Invalid recovery code.')
    else:
        print('Error: User not found.')
    return False
