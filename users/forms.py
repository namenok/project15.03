from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from .models import Profile


class FormControlMixin:
    """Міксін для додавання класу 'form-control' у всі текстові поля."""

    def add_form_control_class(self):
        for _, field in self.fields.items():
            widget = field.widget
            # Якщо це текстове поле (TextInput, PasswordInput, EmailInput тощо)
            if hasattr(widget, "attrs"):
                # Додаємо або оновлюємо клас
                existing_classes = widget.attrs.get("class", "")
                classes = existing_classes.split()
                if "form-control" not in classes:
                    classes.append("form-control")
                widget.attrs["class"] = " ".join(classes)


class RegisterForm(FormControlMixin, UserCreationForm):
    first_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "First Name"}),
    )
    last_name = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Last Name"}),
    )
    username = forms.CharField(
        max_length=100,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Username"}),
    )
    email = forms.EmailField(
        required=True, widget=forms.TextInput(attrs={"placeholder": "Email"})
    )
    password1 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Password",
                "data-toggle": "password",
                "id": "password",
            }
        ),
    )
    password2 = forms.CharField(
        max_length=50,
        required=True,
        widget=forms.PasswordInput(
            attrs={
                "placeholder": "Confirm Password",
                "data-toggle": "password",
                "id": "password",
            }
        ),
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_form_control_class()

    def clean_email(self):
        """Кастомна валідація email: перевірка унікальності."""
        email = self.cleaned_data.get("email")
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Цей email вже використовується.")
        return email


class UpdateUserForm(FormControlMixin, forms.ModelForm):
    username = forms.CharField(max_length=100, required=True)
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.add_form_control_class()

    def clean_email(self):
        """Перевірка унікальності email при оновленні."""
        email = self.cleaned_data.get("email")
        qs = User.objects.filter(email=email).exclude(pk=self.instance.pk)
        if qs.exists():
            raise forms.ValidationError(
                "Цей email вже використовується іншим користувачем."
            )
        return email


class UpdateProfileForm(FormControlMixin, forms.ModelForm):
    avatar = forms.ImageField(
        widget=forms.FileInput(attrs={"class": "form-control-file"})
    )
    bio = forms.CharField(widget=forms.Textarea(attrs={"rows": 5}))

    class Meta:
        model = Profile
        fields = ["avatar", "bio"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Додаємо form-control для текстового поля bio
        self.fields["bio"].widget.attrs["class"] = "form-control"
