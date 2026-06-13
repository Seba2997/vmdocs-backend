import pytest
from unittest.mock import patch, MagicMock
from app.services.email_service import send_reset_password_email

@patch('app.services.email_service.SMTP_USER', '')
@patch('app.services.email_service.SMTP_PASSWORD', '')
def test_send_reset_password_email_dev_mode(capsys):
    # Act
    resultado = send_reset_password_email("test@example.com", "fake-token")
    captured = capsys.readouterr()

    # Assert
    assert resultado is True
    assert "MODO DESARROLLO" in captured.out
    assert "fake-token" in captured.out

@patch('app.services.email_service.SMTP_USER', 'user@example.com')
@patch('app.services.email_service.SMTP_PASSWORD', 'secret')
@patch('smtplib.SMTP')
def test_send_reset_password_email_success(mock_smtp):
    # Arrange
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Act
    resultado = send_reset_password_email("test@example.com", "fake-token")

    # Assert
    assert resultado is True
    mock_server.starttls.assert_called_once()
    mock_server.login.assert_called_once_with('user@example.com', 'secret')
    mock_server.send_message.assert_called_once()

@patch('app.services.email_service.SMTP_USER', 'user@example.com')
@patch('app.services.email_service.SMTP_PASSWORD', 'secret')
@patch('smtplib.SMTP')
def test_send_reset_password_email_failure(mock_smtp):
    # Arrange
    mock_smtp.side_effect = Exception("Connection Error")

    # Act
    resultado = send_reset_password_email("test@example.com", "fake-token")

    # Assert
    assert resultado is False

@patch('app.services.email_service.SMTP_USER', 'user@example.com')
@patch('app.services.email_service.SMTP_PASSWORD', 'secret')
@patch('smtplib.SMTP')
def test_send_reset_password_email_correct_subject_and_body(mock_smtp):
    # Arrange
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Act
    send_reset_password_email("test@example.com", "fake-token")

    # Assert
    # Obtener el mensaje enviado
    sent_message = mock_server.send_message.call_args[0][0]
    
    assert sent_message["To"] == "test@example.com"
    assert sent_message["From"] == "user@example.com"
    assert "Recuperación de Contraseña - VMDocs" in sent_message["Subject"]
    
    html_content = sent_message.get_payload(0).get_payload(decode=True).decode('utf-8')
    assert "fake-token" in html_content

@patch('app.services.email_service.SMTP_USER', 'user@example.com')
@patch('app.services.email_service.SMTP_PASSWORD', 'secret')
@patch('app.services.email_service.SMTP_SERVER', 'smtp.custom.com')
@patch('app.services.email_service.SMTP_PORT', 465)
@patch('smtplib.SMTP')
def test_send_reset_password_email_called_with_correct_server_port(mock_smtp):
    # Arrange
    mock_server = MagicMock()
    mock_smtp.return_value.__enter__.return_value = mock_server

    # Act
    send_reset_password_email("test@example.com", "fake-token")

    # Assert
    mock_smtp.assert_called_once_with('smtp.custom.com', 465)
