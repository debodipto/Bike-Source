from django.contrib.auth.models import User
from django.db import models
from django.db.models import Avg
from django.urls import reverse


class Category(models.Model):
    name = models.CharField(max_length=350)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Categories"

    def __str__(self):
        return self.name


class BikeBuyAndSell(models.Model):
    STATUS = (
        ("Pending", "Pending"),
        ("Approved", "Approved"),
    )
    CONDITION_CHOICES = (
        ("Used", "Used"),
        ("Certified Used", "Certified Used"),
        ("Like New", "Like New"),
    )

    name = models.CharField(max_length=300)
    brand = models.CharField(max_length=100, blank=True, default="")
    model_year = models.PositiveIntegerField(null=True, blank=True)
    mileage = models.PositiveIntegerField(null=True, blank=True, help_text="Mileage in kilometers")
    engine_capacity = models.CharField(max_length=50, blank=True, default="")
    location = models.CharField(max_length=120, blank=True, default="")
    price = models.IntegerField()
    description = models.TextField()
    quantity = models.IntegerField(null=True, blank=True, default=1)
    condition = models.CharField(max_length=30, choices=CONDITION_CHOICES, default="Used")
    is_featured = models.BooleanField(default=False)
    is_negotiable = models.BooleanField(default=False)
    is_available = models.BooleanField(default=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, null=True, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.name

    def get_first_image(self):
        return self.images.first()

    def get_absolute_url(self):
        return reverse("product_detail", args=[self.pk])

    @property
    def average_rating(self):
        return self.reviews.filter(is_approved=True).aggregate(score=Avg("rating"))["score"] or 0

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()


class BikeBuyAndSellImage(models.Model):
    bike_buy_and_sell = models.ForeignKey(BikeBuyAndSell, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="bike_buy_and_sell_images/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["created_at"]

    def __str__(self):
        return f"Image for {self.bike_buy_and_sell.name}"


class Orders(models.Model):
    STATUS = (
        ("Pending", "Pending"),
        ("Order Confirmed", "Order Confirmed"),
        ("Out for Delivery", "Out for Delivery"),
        ("Delivered", "Delivered"),
    )
    PAYMENT_METHODS = (
        ("Cash on Delivery", "Cash on Delivery"),
        ("Bank Transfer", "Bank Transfer"),
        ("Mobile Banking", "Mobile Banking"),
    )

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    email = models.CharField(max_length=50, null=True)
    address = models.CharField(max_length=500, null=True)
    mobile = models.CharField(max_length=20, null=True)
    total_price = models.CharField("Total Price", max_length=20, null=True)
    payment_method = models.CharField(max_length=50, choices=PAYMENT_METHODS, default="Cash on Delivery")
    notes = models.CharField(max_length=300, blank=True, default="")
    order_date = models.DateField(auto_now_add=True, null=True)
    status = models.CharField(max_length=50, null=True, choices=STATUS, default="Pending")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.id}"


class OrderItem(models.Model):
    order = models.ForeignKey(Orders, on_delete=models.CASCADE, related_name="items")
    bike_buy_and_sell = models.ForeignKey(BikeBuyAndSell, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        ordering = ["created_at"]

    def get_cost(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.bike_buy_and_sell.name} x {self.quantity}"


class Banner(models.Model):
    title = models.CharField(max_length=120, blank=True, default="")
    subtitle = models.CharField(max_length=255, blank=True, default="")
    banner_image = models.ImageField(upload_to="banners/")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return self.title or f"Banner {self.pk}"


class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="wishlist_items")
    bike = models.ForeignKey(BikeBuyAndSell, on_delete=models.CASCADE, related_name="wishlisted_by")
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("user", "bike")

    def __str__(self):
        return f"{self.user.username} -> {self.bike.name}"


class Review(models.Model):
    bike = models.ForeignKey(BikeBuyAndSell, on_delete=models.CASCADE, related_name="reviews")
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField(default=5)
    comment = models.TextField()
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        unique_together = ("bike", "user")

    def __str__(self):
        return f"{self.bike.name} review by {self.user.username}"


class FinancingApplication(models.Model):
    EMPLOYMENT_CHOICES = (
        ("Salaried", "Salaried"),
        ("Business", "Business"),
        ("Freelancer", "Freelancer"),
        ("Student", "Student"),
    )

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    city = models.CharField(max_length=100)
    monthly_income = models.PositiveIntegerField()
    down_payment = models.PositiveIntegerField()
    employment_type = models.CharField(max_length=30, choices=EMPLOYMENT_CHOICES)
    preferred_bike = models.ForeignKey(BikeBuyAndSell, on_delete=models.SET_NULL, null=True, blank=True)
    notes = models.TextField(blank=True, default="")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Finance: {self.full_name}"


class TradeInRequest(models.Model):
    CONDITION_CHOICES = (
        ("Excellent", "Excellent"),
        ("Good", "Good"),
        ("Average", "Average"),
        ("Needs Work", "Needs Work"),
    )

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    bike_brand = models.CharField(max_length=100)
    bike_model = models.CharField(max_length=100)
    model_year = models.PositiveIntegerField()
    expected_price = models.PositiveIntegerField()
    condition = models.CharField(max_length=20, choices=CONDITION_CHOICES)
    details = models.TextField(blank=True, default="")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Trade-in: {self.bike_brand} {self.bike_model}"


class ServiceCenter(models.Model):
    name = models.CharField(max_length=120)
    city = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    opening_hours = models.CharField(max_length=120, default="10:00 AM - 7:00 PM")
    is_authorized = models.BooleanField(default=True)

    class Meta:
        ordering = ["city", "name"]

    def __str__(self):
        return f"{self.name} ({self.city})"


class InspectionBooking(models.Model):
    SLOT_CHOICES = (
        ("10:00 AM", "10:00 AM"),
        ("12:00 PM", "12:00 PM"),
        ("3:00 PM", "3:00 PM"),
        ("5:00 PM", "5:00 PM"),
    )

    full_name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    bike = models.ForeignKey(BikeBuyAndSell, on_delete=models.CASCADE, related_name="inspection_bookings")
    preferred_date = models.DateField()
    preferred_slot = models.CharField(max_length=20, choices=SLOT_CHOICES)
    notes = models.TextField(blank=True, default="")
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Inspection for {self.bike.name} by {self.full_name}"


class ContactMessage(models.Model):
    name = models.CharField(max_length=120)
    email = models.EmailField()
    phone = models.CharField(max_length=20, blank=True, default="")
    subject = models.CharField(max_length=150)
    message = models.TextField()
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.subject} - {self.name}"
