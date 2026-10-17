"""Liveness du processus HTTP ; ne teste pas la disponibilité PostgreSQL."""
from django.http import JsonResponse


def health(_request):
    return JsonResponse({"status": "ok"})
