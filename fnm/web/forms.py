from django import forms
from django.core.exceptions import ValidationError
from phonenumber_field.formfields import PhoneNumberField
from .models import Registration, Coupon

class RegistrationForm(forms.ModelForm):

    class Meta:
        model = Registration
        fields = [
            'first_name', 'last_name', 'email', 'phone', 'address', 'country',
            'bring_a_friend', 'friend_name',
            'special_diets', 'potluck', 'activity_idea', 'other_comments',
            'coupon_code',
            'checkbox1', 'checkbox2', 'checkbox3', 'checkbox4', 'checkbox5'
        ]
        widgets = {
            'address': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Your full address'}),
            'special_diets': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Any dietary restrictions or allergies?'}),
            'potluck': forms.Textarea(attrs={'rows': 2, 'placeholder': 'What dish do you plan to bring?'}),
            'activity_idea': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Anything you would like to organize?'}),
            'other_comments': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Any other comments or questions?'}),
            'friend_name': forms.TextInput(attrs={'placeholder': 'First name of your friend'}),
            'coupon_code': forms.TextInput(attrs={'placeholder': 'Optional discount code'})
        }

    def clean_coupon_code(self):
        code = self.cleaned_data.get('coupon_code')
        if code:
            try:
                coupon = Coupon.objects.get(code=code, is_active=True)  #pylint: disable=no-member
                if not coupon.is_valid():
                    raise ValidationError("This coupon has expired.")
            except Coupon.DoesNotExist:  #pylint: disable=no-member
                raise ValidationError("Invalid coupon code.")
        return code
    
    def clean(self):
        cleaned_data = super().clean()
        bring_a_friend = cleaned_data.get('bring_a_friend')
        friend_name = cleaned_data.get('friend_name')

        # Check if friend name is provided when bringing a friend
        if bring_a_friend and not friend_name:
            self.add_error('friend_name', "Please provide your friend's name.")

        # Check all required checkboxes
        if not cleaned_data.get('checkbox1'):
            self.add_error('checkbox1', "You must agree to this to participate in the event.")

        if not cleaned_data.get('checkbox2'):
            self.add_error('checkbox2', "Helping out is an essential part of the event format.")

        if not cleaned_data.get('checkbox3'):
            self.add_error('checkbox3', "Being respectful to all participants is required.")

        if not cleaned_data.get('checkbox4'):
            self.add_error('checkbox4', "You must acknowledge the photo policy.")

        # Only check checkbox5 if bringing a friend
        if bring_a_friend and not cleaned_data.get('checkbox5'):
            self.add_error('checkbox5', "You must agree to forward all information to your friend.")

        return cleaned_data
