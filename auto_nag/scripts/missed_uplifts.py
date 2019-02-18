# This Source Code Form is subject to the terms of the Mozilla Public
# License, v. 2.0. If a copy of the MPL was not distributed with this file,
# You can obtain one at http://mozilla.org/MPL/2.0/.

from auto_nag.bzcleaner import BzCleaner
from auto_nag.common import get_current_versions
from auto_nag import utils


class MissedUplifts(BzCleaner):
    def __init__(self):
        super(MissedUplifts, self).__init__()

    def description(self):
        return 'Bugs fixed in nightly but still affect other supported channels'

    def name(self):
        return 'missed-uplifts'

    def template(self):
        return 'missed_uplifts.html'

    def subject(self):
        return self.description()

    def ignore_date(self):
        return True

    def ignore_bug_summary(self):
        return False

    def columns(self):
        return ['id', 'summary', 'affected']

    def handle_bug(self, bug, data):
        bugid = str(bug['id'])
        beta = bug[self.status_beta]
        release = bug[self.status_release]
        esr = bug[self.status_esr]
        affected = []
        if beta == 'affected':
            affected.append(self.beta)
        if release == 'affected':
            affected.append(self.release)
        if esr == 'affected':
            affected.append(self.esr)

        data[bugid] = {'affected': affected}

        return bug

    def get_bz_params(self, date):
        versions = get_current_versions()
        self.beta = versions['beta']
        self.release = versions['release']
        self.esr = versions['esr']
        self.status_central = utils.get_flag(versions['central'], 'status', 'central')
        self.status_beta = utils.get_flag(self.beta, 'status', 'beta')
        self.status_release = utils.get_flag(self.release, 'status', 'release')
        self.status_esr = utils.get_flag(self.esr, 'status', 'esr')
        fields = [self.status_beta, self.status_release, self.status_esr]
        params = {
            'include_fields': fields,
            'resolution': ['---', 'FIXED'],
            'f1': self.status_central,
            'o1': 'anyexact',
            'v1': ','.join(['fixed', 'verified']),
            'j2': 'OR',
            'f2': 'OP',
            # affected in beta
            'f3': self.status_beta,
            'o3': 'anyexact',
            'v3': 'affected',
            # affected in release
            'f4': self.status_release,
            'o4': 'anyexact',
            'v4': 'affected',
            'f5': 'CP',
        }

        return params


if __name__ == '__main__':
    MissedUplifts().run()