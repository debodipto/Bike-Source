from .cart import Cart


def cart(request):
    return {'cart': Cart(request)}


def compare_items(request):
    return {"compare_ids": request.session.get("compare_bikes", [])}
