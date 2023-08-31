from django import forms

from .models import Recipe


class RecipeAdminForm(forms.ModelForm):
    class Meta:
        model = Recipe
        fields = "__all__"
        widgets = {
            "tags": forms.CheckboxSelectMultiple(),
        }
        help_texts = {
            "tags": "Выберите теги для рецепта",
        }
