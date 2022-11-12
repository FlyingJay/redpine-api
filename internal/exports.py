import csv
from django.http import HttpResponse
from django.utils.encoding import smart_str


def export_csv(modelAdmin, request, queryset):
	response = HttpResponse(content_type='text/csv')
	response['Content-Disposition'] = 'attachment; filename='+modelAdmin.model.__name__+'.csv'
	writer = csv.writer(response, csv.excel)
	response.write(u'\ufeff'.encode('utf8')) # BOM (optional...Excel needs it to open UTF-8 file properly)

	fields = [
	    f.name for f in modelAdmin.model._meta.get_fields(include_parents=False)
		    if f.concrete and (
		        not f.is_relation
		        or f.one_to_one
		        or (f.many_to_one and f.related_model)
	    )
	]

	writer.writerow([smart_str(f) for f in fields])
	for obj in queryset:
		writer.writerow([smart_str(getattr(obj, f)) for f in fields])

	return response
export_csv.short_description = u"Export CSV"


def offer_sheet(campaign):

	return ''