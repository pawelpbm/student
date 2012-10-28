# -*- coding: utf-8 -*-
from django.contrib.admin.widgets import AdminDateWidget
from misc import expiration_days_to_date, date_to_expiration_days

class ExpireWidget(AdminDateWidget):
    """Widget for displaying account expiration date"""
    def render(self, name, value, attrs=None):
        """Function that is called when we want to display widget"""
        if isinstance(value, (int, long)):
            value = expiration_days_to_date(value)
        return super(ExpireWidget, self).render(name, value, attrs)

    def value_from_datadict(self, data, files, name):
        """Function that is called when we want to save data"""
        return date_to_expiration_days(data['shadow_expire'])
