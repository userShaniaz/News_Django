from django.contrib import admin
from django.urls import path
from . import views
from django.urls import path
from .views import (
    CustomLoginView, CustomLogoutView, RegisterUserView, KabinetView, 
    ShowAllUsersView, HistoryRangeView, GetCreditView, AddCardView, 
    RemoveCardView, HomeView
)

# urlpatterns = [
#     path('login/', CustomLoginView.as_view(), name='login'),
#     path('logout/', CustomLogoutView.as_view(), name='logout'),
#     path('register/', RegisterUserView.as_view(), name='register'),
#     path('home/', HomeView.as_view(), name='home'),
#     path('kabinet/<int:id>/', KabinetView.as_view(), name='kabinet'),
#     path('show_all_users/<int:id>/', ShowAllUsersView.as_view(), name='show_all_users'),
#     path('history_range/<int:id>/', HistoryRangeView.as_view(), name='history_range'),
#     path('credit/', GetCreditView.as_view(), name='get_credit'),
#     path('cards/add_card/', AddCardView.as_view(), name='add_card'),
#     path('cards/remove/<int:card_id>/', RemoveCardView.as_view(), name='remove_card'),
# ]


urlpatterns = [
    path('home/', views.HomeView.as_view(), name="home"),  # Главная страница
    path('', views.CustomLoginView.as_view(), name='login'),  # Вход
    path('logout/', views.CustomLogoutView.as_view(), name='logout'),  # Выход
    path('register/', views.RegisterUserView.as_view(), name='register'),  # Регистрация
    # path('admin/', admin.site.urls),  # Админка
    path('kabinet/<int:id>/', views.KabinetView.as_view(), name='kabinet'),  # Личный кабинет
    path('history_range/<int:id>/', views.HistoryRangeView.as_view(), name='history_range'),  # История транзакций
    path('show_all_users/<int:id>/', views.ShowAllUsersView.as_view(), name='show_all_users'),  # Показать всех пользователей
    path('credit/', views.GetCreditView.as_view(), name='get_credit'),  # Получить кредит
    path('cards/add_card/', views.AddCardView.as_view(), name='add_card'),  # Добавить карту
    path('cards/remove/<int:card_id>/', views.RemoveCardView.as_view(), name='remove_card'),  # Удалить карту
]