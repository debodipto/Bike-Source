from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.db.models import Count, Q
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from .cart import Cart
from .forms import (
    BikeListingForm,
    CartAddProductForm,
    CheckoutForm,
    ContactMessageForm,
    FinancingApplicationForm,
    InspectionBookingForm,
    LoginForm,
    ProfileUpdateForm,
    ReviewForm,
    SignUpForm,
    TradeInRequestForm,
)
from .models import (
    Banner,
    BikeBuyAndSell,
    BikeBuyAndSellImage,
    Category,
    InspectionBooking,
    OrderItem,
    Orders,
    Review,
    ServiceCenter,
    Wishlist,
)

COMPARE_SESSION_KEY = "compare_bikes"


def build_market_context(queryset, request):
    search = request.GET.get("query", "").strip()
    category_id = request.GET.get("category", "").strip()
    city = request.GET.get("city", "").strip()
    condition = request.GET.get("condition", "").strip()
    max_price = request.GET.get("max_price", "").strip()

    if search:
        queryset = queryset.filter(
            Q(name__icontains=search)
            | Q(brand__icontains=search)
            | Q(description__icontains=search)
            | Q(location__icontains=search)
        )
    if category_id:
        queryset = queryset.filter(category_id=category_id)
    if city:
        queryset = queryset.filter(location__icontains=city)
    if condition:
        queryset = queryset.filter(condition=condition)
    if max_price:
        queryset = queryset.filter(price__lte=max_price)

    return {
        "bike_buy_and_sell": queryset,
        "categories": Category.objects.all(),
        "selected_category": category_id,
        "selected_city": city,
        "selected_condition": condition,
        "selected_max_price": max_price,
        "query": search,
        "conditions": BikeBuyAndSell.CONDITION_CHOICES,
    }


def home_stats():
    approved_bikes = BikeBuyAndSell.objects.filter(status="Approved")
    return {
        "live_listings": approved_bikes.count(),
        "featured_bikes": approved_bikes.filter(is_featured=True).count(),
        "happy_riders": Orders.objects.count(),
        "seller_count": approved_bikes.values("user").distinct().count(),
    }


@login_required(login_url="/login/")
def logout_view(request):
    logout(request)
    return render(request, "logout.html")


def about_view(request):
    return render(
        request,
        "about_us.html",
        {
            "stats": home_stats(),
            "service_centers": ServiceCenter.objects.all()[:3],
        },
    )


def contact_view(request):
    form = ContactMessageForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your message has been sent. Our team will contact you soon.")
        return redirect("contact")
    return render(request, "contact_us.html", {"form": form})


def index(request):
    approved = BikeBuyAndSell.objects.filter(status="Approved", is_available=True).select_related("category", "user")
    featured = approved.filter(is_featured=True)[:6]
    latest = approved[:8]
    context = {
        "featured_bikes": featured,
        "latest_bikes": latest,
        "banners": Banner.objects.all()[:5],
        "categories": Category.objects.annotate(total_bikes=Count("bikebuyandsell")),
        "service_centers": ServiceCenter.objects.all()[:3],
        "top_rated_bikes": approved[:4],
        "stats": home_stats(),
    }
    return render(request, "index.html", context)


def user_login(request):
    form = LoginForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        username = form.cleaned_data.get("username")
        password = form.cleaned_data.get("password")
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, "Welcome back to Bike Source.")
            return redirect("dashboard" if request.user.is_authenticated else "index")
        messages.error(request, "Login failed. Please check your username and password.")
    return render(request, "login.html", {"form": form})


class SignUpView(CreateView):
    form_class = SignUpForm
    success_url = reverse_lazy("login")
    template_name = "registration.html"

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, "Account created successfully. You can sign in now.")
        return response


@login_required(login_url="/login/")
def change_password(request):
    if request.method == "POST":
        form = PasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, "Your password was updated successfully.")
            return redirect("profile")
        messages.error(request, "Please correct the highlighted fields.")
    else:
        form = PasswordChangeForm(request.user)
    return render(request, "change_password.html", {"form": form})


@login_required(login_url="/login/")
def profile(request):
    user = request.user
    listings = BikeBuyAndSell.objects.filter(user=user)
    orders = Orders.objects.filter(user=user)
    context = {
        "profile": user,
        "listings": listings[:5],
        "orders": orders[:5],
        "wishlist_count": Wishlist.objects.filter(user=user).count(),
    }
    return render(request, "profile.html", context)


@login_required(login_url="/login/")
def dashboard(request):
    user = request.user
    user_listings = BikeBuyAndSell.objects.filter(user=user)
    context = {
        "approved_listings": user_listings.filter(status="Approved").count(),
        "pending_listings": user_listings.filter(status="Pending").count(),
        "orders": Orders.objects.filter(user=user)[:5],
        "wishlist_items": Wishlist.objects.filter(user=user).select_related("bike")[:4],
        "recent_listings": user_listings[:4],
        "inspection_bookings": InspectionBooking.objects.filter(email=user.email)[:4],
    }
    return render(request, "dashboard.html", context)


@login_required(login_url="/login/")
def update_profile(request):
    initial = {
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
    }
    form = ProfileUpdateForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        request.user.first_name = form.cleaned_data["first_name"]
        request.user.last_name = form.cleaned_data["last_name"]
        request.user.email = form.cleaned_data["email"]
        request.user.save()
        messages.success(request, "Your profile has been updated.")
        return redirect("profile")

    return render(request, "update_profile.html", {"form": form, "user": request.user})


@login_required(login_url="/login/")
def booking_list(request):
    booking_queryset = Orders.objects.filter(user=request.user).order_by("-id")
    return render(request, "booking_list.html", {"booking_list": booking_queryset})


def buy_list(request):
    queryset = BikeBuyAndSell.objects.filter(status="Approved", is_available=True).select_related("category", "user")
    context = build_market_context(queryset, request)
    context["page_title"] = "Browse Pre-Owned Bikes"
    return render(request, "buy_list.html", context)


@login_required(login_url="/login/")
def sell_views(request):
    form = BikeListingForm(request.POST or None, request.FILES or None)
    if request.method == "POST" and form.is_valid():
        listing = form.save(commit=False)
        listing.user = request.user
        listing.status = "Pending"
        listing.save()

        for image in request.FILES.getlist("image"):
            BikeBuyAndSellImage.objects.create(bike_buy_and_sell=listing, image=image)

        messages.success(
            request,
            "Your bike listing has been submitted for approval. We will review it shortly.",
        )
        return redirect("sell_list")

    return render(request, "sell.html", {"form": form})


@login_required(login_url="/login/")
def sell_list(request):
    user = request.user
    obj = BikeBuyAndSell.objects.filter(user=user).select_related("category")
    context = {
        "bike_buy_and_sell": obj,
    }
    return render(request, "sell_list.html", context)


def add_to_cart_view(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(BikeBuyAndSell, id=product_id, status="Approved")
    form = CartAddProductForm(request.POST)
    if form.is_valid():
        cd = form.cleaned_data
        quantity = cd["quantity"]
        if product.quantity is not None:
            quantity = min(quantity, product.quantity)
        cart.add(product=product, quantity=quantity, update_quantity=cd["update"])
        messages.success(request, f"{product.name} has been added to your cart.")
    return redirect("cart_detail")


def cart_detail(request):
    cart = Cart(request)
    for item in cart:
        item["update_quantity_form"] = CartAddProductForm(
            initial={"quantity": item["quantity"], "update": True}
        )
    return render(request, "cart_detail.html", {"cart": cart})


def cart_update(request, product_id):
    if request.method == "POST":
        cart = Cart(request)
        product = get_object_or_404(BikeBuyAndSell, id=product_id)
        form = CartAddProductForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            quantity = cd["quantity"]
            if product.quantity is not None:
                quantity = min(quantity, product.quantity)
            cart.update(product=product, quantity=quantity, update_quantity=cd["update"])
            messages.success(request, "Cart updated successfully.")
    return redirect("cart_detail")


def cart_remove(request, product_id):
    cart = Cart(request)
    product = get_object_or_404(BikeBuyAndSell, id=product_id)
    cart.remove(product)
    messages.info(request, f"{product.name} has been removed from your cart.")
    return redirect("cart_detail")


@login_required(login_url="/login/")
def order_create(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.info(request, "Your cart is empty.")
        return redirect("buy_list")

    if request.method == "POST":
        form = CheckoutForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            order = Orders.objects.create(
                user=request.user,
                email=cd["email"],
                mobile=cd["mobile"],
                address=cd["address"],
                total_price=cart.get_total_price(),
                payment_method=cd["payment_method"],
                notes=cd["notes"],
            )

            for item in cart:
                product = item["product"]
                if product.quantity is not None and item["quantity"] > product.quantity:
                    messages.error(
                        request,
                        f"Only {product.quantity} unit(s) of {product.name} are currently available.",
                    )
                    return redirect("cart_detail")
                OrderItem.objects.create(
                    order=order,
                    bike_buy_and_sell=product,
                    price=item["price"],
                    quantity=item["quantity"],
                )
                if product.quantity is not None:
                    product.quantity = max(product.quantity - item["quantity"], 0)
                    product.is_available = product.quantity > 0
                    product.save(update_fields=["quantity", "is_available"])
            cart.clear()
            return render(request, "order_created.html", {"order": order})
    else:
        form = CheckoutForm(
            initial={
                "email": request.user.email,
                "mobile": "",
                "address": "",
            }
        )
    return render(request, "checkout_create.html", {"form": form, "cart": cart})


def search_view(request):
    queryset = BikeBuyAndSell.objects.filter(status="Approved", is_available=True)
    context = build_market_context(queryset, request)
    context["page_title"] = "Search Results"
    return render(request, "buy_list.html", context)


@login_required(login_url="/login/")
def order_details(request, order_id):
    orders = get_object_or_404(Orders, user=request.user, id=order_id)
    products = OrderItem.objects.filter(order__id=order_id).select_related("bike_buy_and_sell")
    return render(request, "order_details.html", {"order": orders, "products": products})


def product_detail(request, id):
    product = get_object_or_404(BikeBuyAndSell, id=id, status="Approved")
    cart_product_form = CartAddProductForm()
    review_form = ReviewForm(request.POST or None)

    if request.method == "POST" and "submit_review" in request.POST:
        if not request.user.is_authenticated:
            messages.error(request, "Please log in to submit a review.")
            return redirect("login")
        if review_form.is_valid():
            Review.objects.update_or_create(
                bike=product,
                user=request.user,
                defaults={
                    "rating": review_form.cleaned_data["rating"],
                    "comment": review_form.cleaned_data["comment"],
                    "is_approved": True,
                },
            )
            messages.success(request, "Thanks for sharing your review.")
            return redirect("product_detail", id=product.id)

    related_products = (
        BikeBuyAndSell.objects.filter(status="Approved", category=product.category)
        .exclude(id=product.id)[:4]
    )
    in_wishlist = False
    if request.user.is_authenticated:
        in_wishlist = Wishlist.objects.filter(user=request.user, bike=product).exists()

    context = {
        "product": product,
        "cart_product_form": cart_product_form,
        "review_form": review_form,
        "reviews": product.reviews.filter(is_approved=True).select_related("user"),
        "related_products": related_products,
        "in_wishlist": in_wishlist,
    }
    return render(request, "detail.html", context)


def category_based_bike(request, category_id):
    queryset = BikeBuyAndSell.objects.filter(category__id=category_id, status="Approved", is_available=True)
    context = build_market_context(queryset, request)
    context["page_title"] = "Category Bikes"
    return render(request, "category_based_bike.html", context)


@login_required(login_url="/login/")
def wishlist_view(request):
    wishlist_items = Wishlist.objects.filter(user=request.user, is_approved=True).select_related("bike", "bike__category")
    return render(request, "wishlist.html", {"wishlist_items": wishlist_items})


@login_required(login_url="/login/")
def toggle_wishlist(request, bike_id):
    bike = get_object_or_404(BikeBuyAndSell, id=bike_id, status="Approved")
    wishlist_item, created = Wishlist.objects.get_or_create(
        user=request.user,
        bike=bike,
        defaults={"is_approved": True},
    )
    if created:
        messages.success(request, f"{bike.name} added to your wishlist.")
    else:
        wishlist_item.delete()
        messages.info(request, f"{bike.name} removed from your wishlist.")
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("wishlist")))


def toggle_compare(request, bike_id):
    bike = get_object_or_404(BikeBuyAndSell, id=bike_id, status="Approved")
    compare_ids = request.session.get(COMPARE_SESSION_KEY, [])
    bike_id_str = str(bike.id)

    if bike_id_str in compare_ids:
        compare_ids.remove(bike_id_str)
        messages.info(request, f"{bike.name} removed from compare list.")
    else:
        if len(compare_ids) >= 3:
            messages.warning(request, "You can compare up to 3 bikes at a time.")
        else:
            compare_ids.append(bike_id_str)
            messages.success(request, f"{bike.name} added to compare list.")

    request.session[COMPARE_SESSION_KEY] = compare_ids
    return HttpResponseRedirect(request.META.get("HTTP_REFERER", reverse("compare")))


def compare_view(request):
    compare_ids = request.session.get(COMPARE_SESSION_KEY, [])
    bikes = list(BikeBuyAndSell.objects.filter(id__in=compare_ids, status="Approved"))
    bike_map = {str(bike.id): bike for bike in bikes}
    bikes = [bike_map[bike_id] for bike_id in compare_ids if bike_id in bike_map]
    compare_base = BikeBuyAndSell.objects.filter(status="Approved", is_available=True)[:6]
    return render(
        request,
        "compare.html",
        {
            "bikes": bikes,
            "compare_base": compare_base,
            "compare_ids": compare_ids,
        },
    )


def financing_view(request):
    form = FinancingApplicationForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your financing request has been submitted.")
        return redirect("financing")
    return render(request, "financing.html", {"form": form})


def trade_in_view(request):
    form = TradeInRequestForm(request.POST or None)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your trade-in request has been submitted.")
        return redirect("trade_in")
    return render(request, "trade_in.html", {"form": form})


def service_centers_view(request):
    centers = ServiceCenter.objects.all()
    fallback_centers = [
        {
            "name": "Bike Source Service Hub",
            "city": "Dhaka",
            "address": "Mirpur DOHS, Dhaka",
            "phone": "+880 1700-111111",
            "opening_hours": "10:00 AM - 8:00 PM",
            "is_authorized": True,
        },
        {
            "name": "Bike Source Chattogram Point",
            "city": "Chattogram",
            "address": "GEC Circle, Chattogram",
            "phone": "+880 1700-222222",
            "opening_hours": "10:00 AM - 7:00 PM",
            "is_authorized": True,
        },
        {
            "name": "Rider Care Workshop",
            "city": "Sylhet",
            "address": "Zindabazar, Sylhet",
            "phone": "+880 1700-333333",
            "opening_hours": "11:00 AM - 7:00 PM",
            "is_authorized": False,
        },
    ]
    return render(
        request,
        "service_centers.html",
        {"service_centers": centers if centers.exists() else fallback_centers},
    )


def inspection_view(request):
    initial = {}
    bike_id = request.GET.get("bike")
    if bike_id and bike_id.isdigit():
        initial["bike"] = bike_id

    form = InspectionBookingForm(request.POST or None, initial=initial)
    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(request, "Your inspection slot has been booked.")
        return redirect("inspection")
    return render(request, "inspection.html", {"form": form})
