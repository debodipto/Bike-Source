from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import DateInput

from .models import (
    BikeBuyAndSell,
    Category,
    ContactMessage,
    FinancingApplication,
    InspectionBooking,
    Review,
    TradeInRequest,
)


class LoginForm(forms.Form):
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Username"}))
    password = forms.CharField(widget=forms.PasswordInput(attrs={"placeholder": "Password"}))


class SignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        user.first_name = self.cleaned_data["first_name"]
        user.last_name = self.cleaned_data["last_name"]
        if commit:
            user.save()
        return user


class ProfileUpdateForm(forms.Form):
    first_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "First Name"}))
    last_name = forms.CharField(widget=forms.TextInput(attrs={"placeholder": "Last Name"}))
    email = forms.EmailField(widget=forms.TextInput(attrs={"placeholder": "Email"}))


PRODUCT_QUANTITY_CHOICES = [(i, str(i)) for i in range(1, 26)]


class CartAddProductForm(forms.Form):
    quantity = forms.TypedChoiceField(choices=PRODUCT_QUANTITY_CHOICES, coerce=int)
    update = forms.BooleanField(required=False, initial=False, widget=forms.HiddenInput)


class OrderCreateForm(forms.Form):
    email = forms.EmailField()
    mobile = forms.CharField(max_length=50)
    address = forms.CharField(max_length=500)
    payment_method = forms.ChoiceField(
        choices=(
            ("Cash on Delivery", "Cash on Delivery"),
            ("Bank Transfer", "Bank Transfer"),
            ("Mobile Banking", "Mobile Banking"),
        )
    )
    notes = forms.CharField(required=False)


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = (
        ("Cash on Delivery", "Cash on Delivery"),
        ("Bank Transfer", "Bank Transfer"),
        ("Mobile Banking", "Mobile Banking"),
    )

    email = forms.EmailField(widget=forms.EmailInput(attrs={"placeholder": "Email"}))
    mobile = forms.CharField(max_length=50, widget=forms.TextInput(attrs={"placeholder": "Phone number"}))
    address = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={"placeholder": "Delivery address", "rows": 4}),
    )
    payment_method = forms.ChoiceField(choices=PAYMENT_CHOICES)
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"placeholder": "Delivery notes (optional)", "rows": 3}),
    )


class MultipleFileInput(forms.ClearableFileInput):
    allow_multiple_selected = True


class BikeListingForm(forms.ModelForm):
    image = forms.FileField(
        widget=MultipleFileInput(),
        required=True,
    )

    class Meta:
        model = BikeBuyAndSell
        fields = [
            "name",
            "brand",
            "model_year",
            "mileage",
            "engine_capacity",
            "location",
            "price",
            "quantity",
            "condition",
            "category",
            "is_negotiable",
            "description",
        ]
        widgets = {
            "description": forms.Textarea(attrs={"rows": 5}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["category"].queryset = Category.objects.all()


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "comment"]
        widgets = {
            "rating": forms.Select(choices=[(i, f"{i} Star") for i in range(1, 6)]),
            "comment": forms.Textarea(attrs={"rows": 4, "placeholder": "Share your experience"}),
        }


class FinancingApplicationForm(forms.ModelForm):
    class Meta:
        model = FinancingApplication
        fields = [
            "full_name",
            "email",
            "phone",
            "city",
            "monthly_income",
            "down_payment",
            "employment_type",
            "preferred_bike",
            "notes",
        ]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 4, "placeholder": "Anything else we should know?"}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["preferred_bike"].queryset = BikeBuyAndSell.objects.filter(status="Approved", is_available=True)
        self.fields["preferred_bike"].required = False


class TradeInRequestForm(forms.ModelForm):
    class Meta:
        model = TradeInRequest
        fields = [
            "full_name",
            "email",
            "phone",
            "bike_brand",
            "bike_model",
            "model_year",
            "expected_price",
            "condition",
            "details",
        ]
        widgets = {
            "details": forms.Textarea(attrs={"rows": 4}),
        }


class InspectionBookingForm(forms.ModelForm):
    class Meta:
        model = InspectionBooking
        fields = ["full_name", "email", "phone", "bike", "preferred_date", "preferred_slot", "notes"]
        widgets = {
            "preferred_date": DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["bike"].queryset = BikeBuyAndSell.objects.filter(status="Approved", is_available=True)


class ContactMessageForm(forms.ModelForm):
    class Meta:
        model = ContactMessage
        fields = ["name", "email", "phone", "subject", "message"]
        widgets = {
            "message": forms.Textarea(attrs={"rows": 5}),
        }
