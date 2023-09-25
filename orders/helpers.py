from orders.models import OrderNotes


def get_notes(id_note):
    return OrderNotes.objects.filter(
        order__id=int(id_note)).order_by("-created_at")
