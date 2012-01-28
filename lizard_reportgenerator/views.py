# (c) Nelen & Schuurmans.  GPL licensed, see LICENSE.txt.
from django.conf import settings
from lizard_area.models import Area
from lizard_reportgenerator.models import ReportTemplate
from lizard_reportgenerator.models import GeneratedReport
from lizard_security.models import DataSet

from django.shortcuts import render_to_response
from django.http import Http404
from django.template import RequestContext


def index(request, template='lizard_reportgenerator/index.html'):
    '''
        returns overview page of reports and historic pages


    '''

    #todo: make function less KRW specific

    aan_afvoergebied_id = request.GET.get('aan_afvoergebied', None)
    krw_gebied_id = request.GET.get('krw_gebied', None)

    aan_afvoergebied = None
    krw_gebied = None

    try:
        aan_afvoergebied = Area.objects.get(ident=aan_afvoergebied_id)
    except Area.DoesNotExist:
        pass

    try:
        krw_gebied = Area.objects.get(ident=krw_gebied_id)
    except Area.DoesNotExist:
        pass

    report_bloks = []

    report_bloks.append({
        'title': 'Algemeen',
        'algemeen': True,
        'report_templates': ReportTemplate.objects.filter(kind='algemeen'),
        'generated_reports': GeneratedReport.objects.filter(template__kind='algemeen')
    })

    report_bloks.append({
        'title': 'KRW waterlichaam',
        'algemeen': False,
        'selection_id': 'select_krw_waterlichaam',
        'area': krw_gebied,
        'report_templates': ReportTemplate.objects.filter(kind='krw'),
        'generated_reports': GeneratedReport.objects.filter(template__kind='krw', area = krw_gebied)
    })

    report_bloks.append({
        'title': 'Aan/afvoergebieden',
        'algemeen': False,
        'selection_id': 'select_aan_afvoergebied',
        'area': aan_afvoergebied,
        'report_templates': ReportTemplate.objects.filter(kind='aan_afvoer'),
        'generated_reports': GeneratedReport.objects.filter(template__kind='aan_afvoer', area = aan_afvoergebied)
    })

    report_templates = {}


    return render_to_response(
        template,
        locals(),
        context_instance=RequestContext(request))



def generate_report(request, format='pdf', report_id=None, area_id=None):
    '''
        function calls generation functions (specified in the configuration) and returns document
    '''

    report_template = ReportTemplate.objects.get(pk=report_id)
    report_module = __import__(report_template.generation_module, fromlist='something')
    #todo, improve interaction with return, saving achieve, etc
    report = getattr(report_module, report_template.generation_function)(request, format=format, report_id=report_id, area_id=area_id)

    return report

    ####
    #    response = HttpResponse(
    #        "Error, unknown format",
    #        content_type='application/txt'
    #    )
    #
    #    response['Content-Disposition'] = 'attachment; filename=error.txt'
    #
    #    return HttpResponse(response)
    ####
