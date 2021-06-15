from django.http import JsonResponse
from django.contrib.admin.views.decorators import staff_member_required

from .controller import sync_all, summary_to_json

@staff_member_required
def synchronize_all(request):
    full_summary = sync_all()
    summary_json = summary_to_json(full_summary)
    return JsonResponse(summary_json)
