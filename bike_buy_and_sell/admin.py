from django.contrib import admin

from .models import (
    Banner,
    BikeBuyAndSell,
    BikeBuyAndSellImage,
    Category,
    ContactMessage,
    FinancingApplication,
    InspectionBooking,
    OrderItem,
    Orders,
    Review,
    ServiceCenter,
    TradeInRequest,
    Wishlist,
)


@admin.action(description="Approve selected items")
def approve_selected(modeladmin, request, queryset):
    queryset.update(is_approved=True)


@admin.action(description="Mark selected items as pending")
def unapprove_selected(modeladmin, request, queryset):
    queryset.update(is_approved=False)


class BikeImageInline(admin.TabularInline):
    model = BikeBuyAndSellImage
    extra = 1


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ("bike_buy_and_sell", "price", "quantity")


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "created_at")
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(BikeBuyAndSell)
class BikeAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "brand",
        "price",
        "condition",
        "location",
        "category",
        "user",
        "status",
        "is_featured",
        "is_available",
    )
    search_fields = ("name", "brand", "location", "user__username", "category__name")
    list_filter = ("status", "condition", "is_featured", "is_available", "category")
    list_editable = ("status", "is_featured", "is_available")
    autocomplete_fields = ("category", "user")
    inlines = [BikeImageInline]


@admin.register(BikeBuyAndSellImage)
class BikeBuyAndSellImageAdmin(admin.ModelAdmin):
    list_display = ("id", "bike_buy_and_sell", "created_at")
    autocomplete_fields = ("bike_buy_and_sell",)


@admin.register(Orders)
class OrdersAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "user",
        "email",
        "mobile",
        "total_price",
        "payment_method",
        "status",
        "order_date",
    )
    search_fields = ("id", "user__username", "email", "mobile")
    list_filter = ("status", "payment_method", "order_date")
    list_editable = ("status",)
    autocomplete_fields = ("user",)
    inlines = [OrderItemInline]


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ("id", "order", "bike_buy_and_sell", "price", "quantity", "created_at")
    search_fields = ("order__id", "bike_buy_and_sell__name")
    autocomplete_fields = ("order", "bike_buy_and_sell")


@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "created_at")
    search_fields = ("title", "subtitle")


@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ("id", "user", "bike", "is_approved", "created_at")
    search_fields = ("user__username", "bike__name")
    autocomplete_fields = ("user", "bike")
    list_filter = ("is_approved",)
    list_editable = ("is_approved",)
    actions = (approve_selected, unapprove_selected)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("id", "bike", "user", "rating", "is_approved", "created_at")
    list_filter = ("rating", "is_approved")
    list_editable = ("is_approved",)
    search_fields = ("bike__name", "user__username", "comment")
    autocomplete_fields = ("bike", "user")


@admin.register(FinancingApplication)
class FinancingApplicationAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "phone", "city", "monthly_income", "is_approved", "created_at")
    search_fields = ("full_name", "phone", "city", "email")
    autocomplete_fields = ("preferred_bike",)
    list_filter = ("is_approved", "employment_type", "city")
    list_editable = ("is_approved",)
    actions = (approve_selected, unapprove_selected)


@admin.register(TradeInRequest)
class TradeInRequestAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "full_name",
        "bike_brand",
        "bike_model",
        "expected_price",
        "condition",
        "is_approved",
        "created_at",
    )
    search_fields = ("full_name", "bike_brand", "bike_model", "phone")
    list_filter = ("condition", "is_approved")
    list_editable = ("is_approved",)
    actions = (approve_selected, unapprove_selected)


@admin.register(ServiceCenter)
class ServiceCenterAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "city", "phone", "opening_hours", "is_authorized")
    search_fields = ("name", "city", "address")
    list_filter = ("city", "is_authorized")
    list_editable = ("is_authorized",)


@admin.register(InspectionBooking)
class InspectionBookingAdmin(admin.ModelAdmin):
    list_display = ("id", "full_name", "bike", "preferred_date", "preferred_slot", "is_approved", "created_at")
    search_fields = ("full_name", "phone", "email", "bike__name")
    list_filter = ("preferred_slot", "preferred_date", "is_approved")
    autocomplete_fields = ("bike",)
    list_editable = ("is_approved",)
    actions = (approve_selected, unapprove_selected)


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "subject", "email", "phone", "is_approved", "created_at")
    search_fields = ("name", "subject", "email", "message")
    list_filter = ("is_approved",)
    list_editable = ("is_approved",)
    actions = (approve_selected, unapprove_selected)


admin.site.site_header = "Bike Source Control Center"
admin.site.site_title = "Bike Source Admin"
admin.site.index_title = "Marketplace Operations Dashboard"
