from django.db import models
from xml.etree import ElementTree as ET


class KBOrderManager(models.Manager):
    def update_from_response_xml(self, payload: str):
        root = ET.fromstring(payload)
        order_id = root.find("./Message/OrderID").text
        session_id = root.find("./Message/SessionID").text
        status = root.find("./Message/OrderStatus").text
        (
            self.get_queryset()
            .filter(order_id=order_id, session_id=session_id)
            .update(status=status)
        )
