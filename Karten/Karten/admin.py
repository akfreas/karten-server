from django.contrib import admin
from Karten.models import *
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import ReadOnlyPasswordHashField

from django import forms

class KartenStackAdmin(admin.ModelAdmin):

    list_display = ('owner', 'name', 'creation_date')

admin.site.register(KartenStack, KartenStackAdmin)

class UserCreationForm(forms.ModelForm):
    """ Form for creating new users, including a repeated password."""

    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Password Confirmation', widget=forms.PasswordInput)

    class Meta:
        model = KartenUser
        fields = ('email',)

    def clean_password2(self):

        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise forms.ValidationError("Passwords don't match")
        return password2

    def save(self, commit=True):

        user = super(UserCreationForm, self).save(commit=False)
        user.set_password(self.cleaned_data["password1"])
        if commit:
            user.save()
        return user

class UserChangeForm(forms.ModelForm):

    password = ReadOnlyPasswordHashField()
    
    
    class Meta:
        model = KartenUser

class KartenUserAdmin(UserAdmin):

    list_display = ('username', 'first_name', 'last_name', 'external_service', 'is_admin')
    exclude = ('user_permissions', 'is_superuser', 'is_staff', 'groups')

    form = UserChangeForm
    add_form = UserCreationForm

    list_filter = ('is_admin',)
    fieldsets = (
            (None, {'fields' : ('first_name', 'last_name', 'email', 'friends', 'profile_pic_url')}),
            ('Permissions info', {'fields' : ('is_admin',)}),
            ('Important dates', {'fields' : ('last_login',)}),
        )

    add_fieldsets = (
            (None, {
                'classes' : ('wide',),
                'fields' : ('username', 'first_name',
                    'last_name', 'email',
                    'password1', 
                    'password2',)}
            ),
    )
    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ()

admin.site.register(KartenUser, KartenUserAdmin)

class KartenCouchServerAdmin(admin.ModelAdmin):
    list_display = ('host', 'protocol', 'port')
admin.site.register(KartenCouchServer, KartenCouchServerAdmin)
