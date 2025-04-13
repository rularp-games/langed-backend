from keycloak import KeycloakAdmin, KeycloakOpenID
from django.conf import settings
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from django.http import HttpResponse
from executor.models import Person

# Инициализируем KeycloakAdmin и KeycloakOpenID
keycloak_openid = KeycloakOpenID(server_url=settings.KEYCLOAK_CONFIG['SERVER_URL'],
                                  client_id=settings.KEYCLOAK_CONFIG['CLIENT_ID'],
                                  client_secret_key=settings.KEYCLOAK_CONFIG['CLIENT_SECRET'],
                                  realm_name=settings.KEYCLOAK_CONFIG['REALM'])

def keycloak_login(request):
    # Переходим на страницу аутентификации Keycloak
    auth_url = keycloak_openid.auth_url(redirect_uri=f"https://{settings.SITE_URL}/auth/callback/")
    return redirect(auth_url)

def keycloak_callback(request):
    # Обрабатываем коллбек от Keycloak
    code = request.GET.get('code')
    
    # Получаем токены
    token = keycloak_openid.token(code=code, 
                                  redirect_uri=f'https://{settings.SITE_URL}/auth/callback/', 
                                  grant_type='authorization_code')
    
    if 'access_token' in token:
        # Здесь вы можете использовать access_token для получения информации о пользователе
        user_info = keycloak_openid.userinfo(token['access_token'])
        
        # Проверяем, существует ли пользователь в вашей базе данных
        user, created = User.objects.get_or_create(username=user_info['preferred_username'], defaults={
            'email': user_info.get('email', ''),
            'first_name': user_info['given_name'],
            'last_name': user_info['family_name']
        })

        if 'vk' in user_info['groups']:
            Person.objects.get_or_create(vk_url=f"https://vk.com/{user_info['preferred_username']}",
                                        defaults={
                                            'user_id': user.id,
                                            'first_name': user_info['given_name'],
                                            'last_name': user_info['family_name'],
                                        })
        
        # Логиним пользователя в Django
        login(request, user)

        return redirect(f"https://{settings.SITE_URL}/")
    
    return HttpResponse("Ошибка аутентификации.")

def keycloak_logout(request):
    # Выход из системы
    logout(request)
    return redirect(f"https://{settings.SITE_URL}/")