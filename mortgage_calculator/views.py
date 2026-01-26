
# mortgage_calculator/views.py
from decimal import Decimal
from django.http import JsonResponse
from django.shortcuts import render
from django.views.decorators.http import require_POST

from .services import monthly_payment

def widget(request):
    """
    Render a reusable mortgage calculator widget page.
    You can also embed its template into other pages.
    """
    return render(request, "mortgage_calculator/widget.html")

@require_POST
def calc_api(request):
    try:
        principal = Decimal(request.POST.get("principal", "0"))
        rate = Decimal(request.POST.get("rate", "0"))
        years = int(request.POST.get("years", "0"))

        m = monthly_payment(principal, rate, years)

        return JsonResponse({
            "monthly_payment": str(m.quantize(Decimal("0.01"))),
        })
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=400)
