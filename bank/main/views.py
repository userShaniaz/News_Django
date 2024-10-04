from django.db.models import Q
from datetime import date, timedelta
from django.utils import timezone
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout, update_session_auth_hash 
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib import messages 
from django.contrib.auth import get_user
from django.urls import reverse_lazy
from django.http import Http404
from .forms import SignUpForm, CustomUserCreationForm, CreditForm, BankCardForm
from .models import CustomUser, Kupon, Transaction, Credit, BankCard
import random

from django.views import View
from django.views.generic import TemplateView, ListView, FormView, UpdateView
from django.contrib.auth.views import LoginView, LogoutView


from django.views import View

class HomeView(TemplateView):
    template_name = 'main/home.html'



class CustomLogoutView(LogoutView):
    next_page = reverse_lazy('home')

    def dispatch(self, request, *args, **kwargs):
        logout(request)
        messages.success(request, 'Вы вышли из системы.')
        return super().dispatch(request, *args, **kwargs)



class RegisterUserView(FormView):
    template_name = 'main/register.html'
    form_class = CustomUserCreationForm

    def form_valid(self, form):
        user = form.save()
        username = form.cleaned_data['username']
        password = form.cleaned_data['password1']
        user = authenticate(self.request, username=username, password=password)
        if user is not None:
            login(self.request, user)
            messages.success(self.request, 'Вы успешно зарегистрировались.')
            return redirect('kabinet', id=user.id)
        else:
            messages.error(self.request, 'Ошибка при регистрации.')
            return redirect('register')



class CustomLoginView(LoginView):
    template_name = 'main/login.html'

    def form_valid(self, form):
        user = form.get_user()
        login(self.request, user)
        messages.success(self.request, 'Вы успешно вошли в систему.')
        return redirect('kabinet', id=user.id)

    def form_invalid(self, form):
        messages.error(self.request, 'Ошибка при входе в систему.')
        return super().form_invalid(form)



class KabinetView(View):
    template_name = 'main/kabinet.html'

    def get(self, request, id):
        u = get_object_or_404(CustomUser, id=id)
        cards = BankCard.objects.filter(user=u)
        return render(request, self.template_name, {'user': u, 'cards': cards})

    def post(self, request, id):
        u = get_object_or_404(CustomUser, id=id)
        name = request.POST.get('name')
        money = request.POST.get('money')
        kupon_number = request.POST.get('kupon')
        credit_amount = request.POST.get('credit_amount')
        repay_credit_id = request.POST.get('repay_credit_id')
        add_card_number = request.POST.get('add_card_number')
        card_type = request.POST.get('card_type')
        expiry_date = request.POST.get('expiry_date')

        if name and money:
            try:
                money = int(money)
                if CustomUser.objects.filter(name=name).exists() and u.wallet >= money and money >= 0:
                    recipient = CustomUser.objects.get(name=name)
                    u.transaction(money, recipient)
                    success_message = f"Перевод {money} успешно выполнен."
                    return render(request, self.template_name, {'user': u, 'success': success_message})
                else:
                    error_message = "Недостаточно средств или пользователь не найден."
                    return render(request, self.template_name, {'user': u, 'error': error_message})
            except ValueError:
                error_message = "Сумма перевода должна быть числом."
                return render(request, self.template_name, {'user': u, 'error': error_message})

        elif kupon_number:
            try:
                kupon = Kupon.objects.get(number=kupon_number, active=True)
                u.wallet += kupon.amount
                u.save()
                kupon.active = False
                kupon.save()
                success_message = f"Купон на сумму {kupon.amount} успешно активирован."
                return render(request, self.template_name, {'user': u, 'success': success_message})
            except Kupon.DoesNotExist:
                error_message = "Купон не найден или уже был использован."
                return render(request, self.template_name, {'user': u, 'error': error_message})

        elif credit_amount:
            try:
                credit_amount = int(credit_amount)
                interest_rate = 5
                duration = 12
                monthly_payment = calculate_monthly_payment(credit_amount, interest_rate, duration)
                next_payment_date = timezone.now().date() + timedelta(days=30)

                if credit_amount > 0:
                    Credit.objects.create(
                        user=u,
                        amount=credit_amount,
                        interest_rate=interest_rate,
                        duration=duration,
                        monthly_payment=monthly_payment,
                        next_payment_date=next_payment_date,
                        date_due=next_payment_date + timedelta(days=30 * duration)
                    )
                    u.wallet += credit_amount
                    u.save()
                    success_message = f"Кредит на сумму {credit_amount} успешно получен."
                    return render(request, self.template_name, {'user': u, 'success': success_message})
                else:
                    error_message = "Сумма кредита должна быть положительной."
                    return render(request, self.template_name, {'user': u, 'error': error_message})
            except ValueError:
                error_message = "Сумма кредита должна быть числом."
                return render(request, self.template_name, {'user': u, 'error': error_message})

        elif repay_credit_id:
            try:
                credit = Credit.objects.get(id=repay_credit_id, user=u, is_paid=False)
                total_amount = credit.calculate_total_amount()
                if u.wallet >= total_amount:
                    u.wallet -= total_amount
                    u.save()
                    credit.is_paid = True
                    credit.save()
                    success_message = f"Кредит на сумму {credit.amount} успешно погашен."
                    return render(request, self.template_name, {'user': u, 'success': success_message})
                else:
                    error_message = "Недостаточно средств для погашения кредита."
                    return render(request, self.template_name, {'user': u, 'error': error_message})
            except Credit.DoesNotExist:
                error_message = "Кредит не найден или уже погашен."
                return render(request, self.template_name, {'user': u, 'error': error_message})

        elif add_card_number and card_type and expiry_date:
            try:
                BankCard.objects.create(
                    user=u,
                    card_type=card_type,
                    card_number=add_card_number,
                    expiry_date=expiry_date
                )
                success_message = "Банковская карта успешно добавлена."
                return render(request, self.template_name, {'user': u, 'success': success_message})
            except Exception as e:
                error_message = f"Ошибка при добавлении карты: {str(e)}"
                return render(request, self.template_name, {'user': u, 'error': error_message})

        cards = BankCard.objects.filter(user=u)
        return render(request, self.template_name, {'user': u, 'cards': cards})



class HistoryRangeView(View):
    template_name = 'main/history_range.html'

    def post(self, request, id):
        start = request.POST.get('start')
        end = request.POST.get('end')
        user = get_object_or_404(CustomUser, id=id)
        transactions = Transaction.objects.filter(user__id=user.id, time__range=(start, end))
        return render(request, self.template_name, {'transactions': transactions})

    def get(self, request, id):
        return render(request, self.template_name)



class ShowAllUsersView(View):
    template_name = 'main/show_all_users.html'

    def get(self, request, id):
        u = get_object_or_404(CustomUser, id=id)
        users = CustomUser.objects.filter(~Q(id=u.id))
        return render(request, self.template_name, {'users': users, 'cur_u': u})

    def post(self, request, id):
        u = get_object_or_404(CustomUser, id=id)
        name = request.POST.get('name')
        money = request.POST.get('money')
        try:
            money = int(money)
            recipient = CustomUser.objects.get(name=name)
            if u.wallet >= money and money >= 0:
                u.transaction(money, recipient)
        except (ValueError, CustomUser.DoesNotExist):
            pass
        return redirect('kabinet', id=u.id)



class CreateCreditView(FormView):
    template_name = 'main/create_credit.html'
    form_class = CreditForm

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        interest_rate = form.cleaned_data['interest_rate']
        term_months = form.cleaned_data['term_months']

        if interest_rate > 0:
            monthly_rate = interest_rate / 100 / 12
            monthly_payment = amount * (monthly_rate * (1 + monthly_rate) ** term_months) / ((1 + monthly_rate) ** term_months - 1)
        else:
            monthly_payment = amount / term_months

        credit = form.save(commit=False)
        credit.user = self.request.user
        credit.monthly_payment = monthly_payment
        credit.remaining_amount = amount
        credit.save()
        return redirect('credit_detail', id=credit.id)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['monthly_payment'] = None
        return context



class GetCreditView(FormView):
    template_name = 'main/get_credit.html'
    form_class = CreditForm
    success_url = reverse_lazy('get_credit')

    def form_valid(self, form):
        amount = form.cleaned_data['amount']
        interest_rate = form.cleaned_data['interest_rate']
        duration = form.cleaned_data['duration']

        monthly_payment = calculate_monthly_payment(amount, interest_rate / 100, duration)
        next_payment_date = calculate_next_payment_date(duration)

        Credit.objects.create(
            amount=amount,
            interest_rate=interest_rate,
            duration=duration,
            monthly_payment=monthly_payment,
            next_payment_date=next_payment_date
        )
        return super().form_valid(form)



def calculate_monthly_payment(amount, annual_rate, duration):
    r = annual_rate / 12
    n = duration
    if r == 0:
        return amount / n
    return amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1)



def calculate_next_payment_date(duration):
    today = timezone.now().date()
    return today + timedelta(days=30 * duration)



class CardListView(ListView):
    model = BankCard
    template_name = 'main/card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return BankCard.objects.filter(user=self.request.user)



def generate_card_number():
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])



def generate_cvv():
    return ''.join([str(random.randint(0, 9)) for _ in range(3)])



class AddCardView(FormView):
    template_name = 'main/add_card.html'
    form_class = BankCardForm

    def form_valid(self, form):
        card_type = form.cleaned_data['card_type']
        user = self.request.user

        card_number = generate_card_number()
        cvv = generate_cvv()
        expiry_date = date.today() + timedelta(days=4*365)

        BankCard.objects.create(
            user=user,
            card_type=card_type,
            card_number=card_number,
            cvv=cvv,
            expiry_date=expiry_date
        )
        return redirect('kabinet', id=user.id)



class EditCardView(UpdateView):
    model = BankCard
    form_class = BankCardForm
    template_name = 'main/edit_card.html'
    success_url = reverse_lazy('card_list')

    def get_object(self, queryset=None):
        card = super().get_object(queryset)
        if card.user != self.request.user:
            raise Http404()
        return card



class RemoveCardView(View):
    def post(self, request, card_id):
        user = self.request.user
        card = get_object_or_404(BankCard, id=card_id, user=user)
        card.delete()
        return redirect('kabinet', id=user.id)

    def get(self, request, card_id):
        return redirect('kabinet', id=self.request.user.id)