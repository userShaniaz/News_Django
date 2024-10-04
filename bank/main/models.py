from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.contrib.auth.models import AbstractUser


class CustomUser(AbstractUser):
    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    wallet = models.IntegerField(default=0)

    def __str__(self):
        return self.username


class Transaction(models.Model):
    class Meta:
        verbose_name = 'Транзакция'
        verbose_name_plural = 'Транзакции'

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='transactions')
    amount = models.PositiveIntegerField()
    value = models.CharField(max_length=1)
    recipient = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='recipient')
    time = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.value == '+':
            return f"{self.value, self.amount} от {self.recipient}, время: {self.time}"
        else:
            return f"{self.value, self.amount} для {self.recipient}, время: {self.time}"


class TransactionService:
    @staticmethod
    def create_transaction(sender, amount, recipient_name):
        recipient = CustomUser.objects.get(username=recipient_name)
        if amount >= 0 and amount:
            sender.wallet -= amount
            sender.save()
            Transaction.objects.create(user=sender, amount=amount, value='-', recipient=recipient)

            recipient.wallet += amount
            recipient.save()
            Transaction.objects.create(user=recipient, amount=amount, value='+', recipient=sender)


class Kupon(models.Model):
    class Meta:
        verbose_name = 'Купон'
        verbose_name_plural = "Купоны"

    number = models.IntegerField(unique=True)
    active = models.BooleanField(default=True)
    amount = models.PositiveIntegerField()



class Credit(models.Model):
    class Meta:
        verbose_name = 'Кредит'
        verbose_name_plural = "Кредиты"

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    date_due = models.DateField()
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    interest_rate = models.DecimalField(max_digits=5, decimal_places=2)
    duration = models.IntegerField()
    monthly_payment = models.DecimalField(max_digits=12, decimal_places=2)
    next_payment_date = models.DateField()
    is_paid = models.BooleanField(default=False)

    def calculate_total_amount(self):
        if self.interest_rate == 0:
            return self.amount
        
        r = self.interest_rate / 100 / 12
        n = self.duration
        total_amount = self.amount * (r * (1 + r) ** n) / ((1 + r) ** n - 1) * n
        return total_amount

    def __str__(self):
        return f"Кредит на сумму {self.amount} с процентной ставкой {self.interest_rate}%"
    

class BankCard(models.Model):
    class Meta:
        verbose_name = 'Банковская карта'
        verbose_name_plural = "Банковские карты"


    CARD_TYPES_CHOICES = [
        ('DEBIT', 'Дебетова'),
        ('CREDIT', 'Кредитная'),
        ('VISA', 'Виза'),
        ('MASTERCARD', 'Мастеркард'),
        ('GOLD', 'Золотая'),
        ('PLATINUM', 'Платиновая')
    ]

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    card_number = models.CharField(max_length=16, unique=True)
    card_type = models.CharField(max_length=20, choices=CARD_TYPES_CHOICES)
    expiry_date = models.DateField()
    cvv = models.CharField(max_length=3)