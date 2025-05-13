from email.message import EmailMessage
from pathlib import Path
from typing import BinaryIO

import aiofiles
from src.config import settings
from src.schemas import EmailBaseModel, EmailRecieve
from src.storage import StorageService

from jinja2 import Template


async def get_prepared_email_template(
    message: EmailBaseModel,
) -> EmailMessage:
    try:
        # Get HTML template
        filepath: str | Path = settings.storage.local_storage_template_path
        # file_content: BinaryIO = await storage.get_file(filepath)
        async with aiofiles.open(filepath, "rb") as f:
            html_template = (await f.read()).decode("utf-8")

        #  Jinja2
        template = Template(html_template)
        html_content = template.render(
            header_text="This is a test email",
            message_body=message.message_body,
        )

        msg = EmailMessage()
        msg["Subject"] = message.subject
        msg["From"] = message.from_email
        msg["To"] = message.to_email

        msg.set_content(
            "Please view this email in an HTML-capable email client.", subtype="plain"
        )
        msg.add_alternative(html_content, subtype="html")

        return msg

    except Exception as e:
        raise ValueError(f"Error preparing email template: {str(e)}")
