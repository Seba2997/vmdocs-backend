import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

load_dotenv()

SMTP_SERVER = os.getenv("SMTP_SERVER", "smtp.gmail.com")
SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
SMTP_USER = os.getenv("SMTP_USER")
SMTP_PASSWORD = os.getenv("SMTP_PASSWORD", "").replace(" ", "")
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://localhost:5173")

def send_reset_password_email(email_to: str, token: str):
    """
    Envía un correo electrónico con el link de recuperación.
    """
    # Si no hay credenciales, imprimimos el link en consola para pruebas locales
    if not all([SMTP_USER, SMTP_PASSWORD]) or "tu-correo" in str(SMTP_USER):
        print("\n" + "="*60)
        print("🛠️  MODO DESARROLLO: Simulación de envío de correo")
        print(f"📧 Para: {email_to}")
        print(f"🔗 Link: {FRONTEND_URL}/reset-password?token={token}")
        print("="*60 + "\n")
        return True

    from datetime import datetime
    ahora = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    
    reset_link = f"{FRONTEND_URL}/reset-password?token={token}"
    
    # Agregar la hora al asunto fuerza a Gmail a crear un hilo nuevo cada vez, eliminando los 3 puntitos
    subject = f"Recuperación de Contraseña - VMDocs ({ahora})"
    
    # Template HTML con estilo profesional y un timestamp único para evitar que Gmail lo repliegue
    html_body = f"""<html><body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333; background-color: #f4f4f4; padding: 20px;"><div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 8px; overflow: hidden; box-shadow: 0 4px 10px rgba(0,0,0,0.1); border: 1px solid #e0e0e0;"><div style="background-color: #1a237e; padding: 25px; text-align: center;"><h1 style="color: #ffffff; margin: 0; font-size: 32px; font-weight: bold; letter-spacing: -1px;">VMDocs</h1></div><div style="padding: 40px;"><h2 style="color: #1a237e; margin-top: 0; font-size: 22px;">Recuperación de Contraseña</h2><p style="font-size: 16px;">Hola,</p><p style="font-size: 16px;">Usted ha solicitado restablecer su contraseña de acceso al sistema <strong>VMDocs</strong>. Para continuar, por favor haga clic en el siguiente botón:</p><div style="text-align: center; margin: 35px 0;"><a href="{reset_link}" style="background-color: #1a237e; color: #ffffff; padding: 14px 30px; text-decoration: none; border-radius: 6px; font-weight: bold; display: inline-block; font-size: 16px; box-shadow: 0 2px 5px rgba(0,0,0,0.2);">Restablecer Contraseña</a></div><p style="font-size: 14px; color: #666; background-color: #f9f9f9; padding: 15px; border-radius: 5px; border-left: 4px solid #1a237e;">Este enlace tiene una validez de <strong>5 minutos</strong> y es de un solo uso. Si usted no realizó esta solicitud, puede ignorar este correo de forma segura.</p><hr style="border: 0; border-top: 1px solid #eee; margin: 30px 0;"><p style="font-size: 12px; color: #999; text-align: center;">Este es un correo automático generado por el sistema VMDocs.<br>Por favor, no responda a este mensaje.<br><br><span style="color:#cccccc;">Ref: {ahora}</span></p></div></div></body></html>"""

    message = MIMEMultipart()
    message["From"] = SMTP_USER
    message["To"] = email_to
    message["Subject"] = subject
    message.attach(MIMEText(html_body, "html"))


    try:
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SMTP_USER, SMTP_PASSWORD)
            server.send_message(message)
        return True
    except Exception as e:
        print(f"❌ Error enviando email: {e}")
        return False
