from django import forms
from .models import Credit, BankCard
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.utils.safestring import mark_safe

class CreditForm(forms.ModelForm):
    amount = forms.IntegerField(
        min_value=1000,
        label='Сумма кредита',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите сумму кредита'}),
    )
    interest_rate = forms.FloatField(
        min_value=0,
        max_value=100,
        step_size=0.1,
        label='Процентная ставка',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите процентную ставку'}),
    )
    term_months = forms.IntegerField(
        min_value=1,
        max_value=360,
        label='Срок кредита (в месяцах)',
        widget=forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Введите срок кредита в месяцах'}),
    )

    class Meta:
        model = Credit
        fields = ['amount', 'interest_rate', 'term_months']


class BankCardForm(forms.ModelForm):
    class Meta:
        model = BankCard
        fields = ['card_type', 'card_number', 'expiry_date']


class CustomUserCreationForm(UserChangeForm):
	
	password = forms.CharField(label="", widget=forms.TextInput(attrs={'type':'hidden'}))
	class Meta:
		model = User
		fields = ('username', 'first_name', 'last_name', 'email','password',)
		  



class SignUpForm(UserCreationForm):
    email = forms.EmailField(
        label="",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Email Address'})
    )
    first_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'First Name'})
    )
    last_name = forms.CharField(
        label="",
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Last Name'})
    )

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2',)

    def __init__(self, *args, **kwargs):
        super(SignUpForm, self).__init__(*args, **kwargs)

        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'User Name'
        })
        self.fields['username'].label = ''
        self.fields['username'].help_text = mark_safe('<span class="form-text text-muted"><small>Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.</small></span>')

        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Password'
        })
        self.fields['password1'].label = ''
        self.fields['password1'].help_text = mark_safe('<ul class="form-text text-muted small"><li>Your password can\'t be too similar to your other personal information.</li><li>Your password must contain at least 8 characters.</li><li>Your password can\'t be a commonly used password.</li><li>Your password can\'t be entirely numeric.</li></ul>')

        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm Password'
        })
        self.fields['password2'].label = ''
        self.fields['password2'].help_text = mark_safe('<span class="form-text text-muted"><small>Enter the same password as before, for verification.</small></span>')
