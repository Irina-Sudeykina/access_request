def user_groups(request):
    """
    Контекстный процессор, добавляющий переменные о группах пользователя.
    """
    # Проверяем, что пользователь аутентифицирован
    if request.user.is_authenticated:
        # Проверяем принадлежность к группе Admins или суперпользователя
        is_admin = request.user.groups.filter(name="Admins").exists() or request.user.is_superuser
    else:
        # Если пользователь не залогинен, переменная False
        is_admin = False

    # Возвращаем словарь. Ключ станет именем переменной в шаблоне.
    return {
        'is_admin': is_admin
    }
