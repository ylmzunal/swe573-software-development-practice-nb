from django.core.mail import send_mail

send_mail(
    'Test Email',
    'This is a test email from Eureka Nexus.',
    'betulnesibeswe@gmail.com',
    ['betulnesibe@gmail.com'],
    fail_silently=False,
)
