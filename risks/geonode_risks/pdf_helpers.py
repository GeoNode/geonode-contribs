# -*- coding: utf-8 -*-
#########################################################################
#
# Copyright (C) 2019 OSGeo
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. If not, see <http://www.gnu.org/licenses/>.
#
#########################################################################

import logging
import subprocess
from StringIO import StringIO

from django.conf import settings

from geonode.utils import run_subprocess

log = logging.getLogger(__name__)


def generate_pdf_weasyprint_api(urls, pdf):
    from weasyprint import HTML
    h = HTML(urls[0])
    h.write_pdf(pdf)
    return pdf


def generate_pdf_wkhtml2pdf(urls, pdf):
    converter_path = settings.RISKS['PDF_GENERATOR']['BIN']
    converter_opts = settings.RISKS['PDF_GENERATOR']['ARGS']
    args = [converter_path] + converter_opts + urls + [ pdf]
    log.info('running pdf converter with args: %s', args)

    ret, stdout, stderr = run_subprocess(*args, shell=True, close_fds=True)
    if ret:
        raise ValueError("Error when running subprocess {}:\n {}\n{}".format(args, stdout, stderr))

    return pdf

def generate_pdf(urls, pdf, pdf_gen_name=None, **kwargs):
    pdf_gen_name = pdf_gen_name or settings.RISKS['PDF_GENERATOR']['NAME']
    pdf_gen = globals()['generate_pdf_{}'.format(pdf_gen_name)]

    return pdf_gen(urls, pdf)

