from django.core.exceptions import ValidationError


def username_validation(value):
    if value.lower() == 'me':
        raise ValidationError(
            '"me" запрещено использовать как логин пользователя'
        )
    return value
