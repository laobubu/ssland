from __future__ import print_function, absolute_import
from web.models import Quota

class QuotaSupervisor():
    def handle_periodic(self):
        quotas = Quota.objects.filter(enabled=True, account__enabled=True)
        for quota in quotas:
            quota.update_from_alias()
            if not quota.is_really_enabled: continue
            if quota.is_exceeded():
                quota.trig()

    def add_to_loop(self,loop):
        loop.add_periodic(self.handle_periodic)
