from __future__ import absolute_import, unicode_literals

import sys

import django
from django.apps import apps
from django.utils.translation import ugettext_lazy as _

from debug_toolbar.panels import Panel


class VersionsPanel(Panel):
    """
    Shows versions of Python, Django, and installed apps if possible.
    """
    @property
    def nav_subtitle(self):
        return 'Django %s' % django.get_version()

    title = _("Versions")

    template = 'debug_toolbar/panels/versions.html'

    def generate_stats(self, request, response):
        versions = [
            ('Python', '', '%d.%d.%d' % sys.version_info[:3]),
            ('Django', '', self.get_app_version(django)),
        ]
        versions += list(self.gen_app_versions())
        self.record_stats({
            'versions': sorted(versions, key=lambda v: v[0]),
            'paths': sys.path,
        })

    def gen_app_versions(self):
        for app_config in apps.get_app_configs():
            name = app_config.verbose_name
            app = app_config.module
            version = self.get_app_version(app)
            if version:
                yield app.__name__, name, version

    def get_app_version(self, app):
        if hasattr(app, 'get_version'):
            get_version = app.get_version
            if callable(get_version):
                version = get_version()
            else:
                version = get_version
        elif hasattr(app, 'VERSION'):
            version = app.VERSION
        elif hasattr(app, '__version__'):
            version = app.__version__
        else:
            return
        if isinstance(version, (list, tuple)):
            # We strip dots from the right because we do not want to show
            # trailing dots if there are empty elements in the list/tuple
            version = '.'.join(str(o) for o in version).rstrip('.')
        return version
