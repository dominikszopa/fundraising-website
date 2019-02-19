from django.apps import AppConfig


class TeamFundraisingConfig(AppConfig):
    name = 'team_fundraising'

    def ready(self):
        from paypal.standard.ipn.signals import valid_ipn_received
        from .paypal import process_paypal
        valid_ipn_received.connect(process_paypal)
