import logging
import smtplib
import ssl
from email.header import Header
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from infrastructure.database.models import User
from infrastructure.database.models.awards import Awards
from infrastructure.database.models.executes import Execute
from tgbot.config import load_config
from tgbot.services.logger import setup_logging

config = load_config(".env")

setup_logging()
logger = logging.getLogger(__name__)


# TODO Добавить логирование отправки Email
async def send_email(to_addrs: list[str], subject: str, body: str, html: bool = True):
    """
    Отправка email

    Args:
        to_addrs: Список адресов для отправки письма
        subject: Заголовок письма
        body: Тело письма
        html: Использовать ли HTML для форматирования
    """
    context = ssl.create_default_context()

    msg = MIMEMultipart()
    msg["From"] = config.email.user
    msg["To"] = ", ".join(to_addrs)  # Join list into comma-separated string
    msg["Subject"] = Header(subject, "utf-8")

    content_type = "html" if html else "plain"
    msg.attach(MIMEText(body, content_type, "utf-8"))

    try:
        with smtplib.SMTP_SSL(
            host=config.email.host, port=config.email.port, context=context
        ) as server:
            server.login(user=config.email.user, password=config.email.password)
            server.sendmail(
                from_addr=config.email.user, to_addrs=to_addrs, msg=msg.as_string()
            )
            logger.info("[Email] Письмо успешно отправлено")
    except smtplib.SMTPException as e:
        logger.error(f"[Email] Ошибка отправки письма: {e}")


async def new_award_email(execute: Execute, award: Awards, user: User, boss: User):
    # Заголовок письма
    email_subject = "Использование награды"

    # Контент письма
    email_content = f"""Добрый день<br>
<b>{user.FIO}</b> просит активировать награду <b>{award.Name}</b><br>
Описание: <b>{award.Description}</b><br>"""
    if execute.Comment:
        email_content += f"""<br>Комментарий: <b>{execute.Comment}</b>"""

    # Список адресов для отправки письма
    to_addrs: list[str] = []

    match execute.Executing % 7:
        case 3:
            if user.Division == "НЦК":
                interaction = execute.Executing % 7
            else:
                interaction = "НТП1" if "первой" in user.Position else "НТП2"
        case 4:
            interaction = "Администратор"
        case 5:
            interaction = "ГОК"
        case 6:
            interaction = "МИП"
        case _:
            interaction = "Неизвестно"

    # TODO добавить проверку на направление специалиста вместо конфига
    if interaction in ["НЦК", "НТП1", "НТП2"]:
        match config.tg_bot.division:
            case "NCK":
                to_addrs.append(config.email.nck_email_addr)
            case "NTP":
                to_addrs.append(config.email.ntp_email_addr)

    if user.Email != "Не указан email":
        to_addrs.append(user.Email)

    # TODO Включить отправку уведомления РГ
    # if boss.Email != "Не указан email":
    # to_addrs.append(boss.Email)

    # Отправка письма
    logger.info(
        "[Email] Собран список адресов для отправки уведомления о новой награде:"
        + str(to_addrs)
    )
    await send_email(
        to_addrs=to_addrs, subject=email_subject, body=email_content, html=True
    )
