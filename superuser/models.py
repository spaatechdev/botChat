from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager
from django.utils.timezone import now


class User(AbstractUser):
    email = models.EmailField(
        verbose_name='email address',
        max_length=100,
        unique=True,
        error_messages={'unique': 'A user with that email already exists.'},
        help_text='Required. 100 characters or fewer. Letters, digits and @/./_ only.',
    )
    pswd_token = models.CharField(max_length=255, blank=True, null=True)
    phone = models.CharField(max_length=15, blank=True, null=True)

    USERNAME_FIELD = 'email'
    # removes email from REQUIRED_FIELDS
    REQUIRED_FIELDS = ['first_name', 'last_name', 'phone']

    manager = UserManager()

    def __str__(self):
        return self.first_name
    
    class Meta:
        managed = True
        db_table = 'users'
        verbose_name_plural = 'users'

    def has_perm(self, perm, obj=None):
        "Does the user have a specific permission?"
        # Simplest possible answer: Yes, always
        return True

    def has_module_perms(self, app_label):
        "Does the user have permissions to view the app `app_label`?"
        # Simplest possible answer: Yes, always
        return True

    @property
    def is_staff(self):
        "Is the user a member of staff?"
        # Simplest possible answer: All admins are staff
        return self.is_superuser
    
class QuestionAnswers(models.Model):
    question = models.TextField(blank=True, null=True)
    response = models.TextField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.CASCADE, blank=True, null=True)
    category = models.TextField(blank=True, null=True)
    order = models.IntegerField(blank=True, null=True)

    def __str__(self):
        return self.question

    class Meta:
        managed = True
        db_table = 'question_answers'
        verbose_name_plural = 'question_answers'