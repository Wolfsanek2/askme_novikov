from django import forms
from app import models

class LoginForm(forms.Form):
    username = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)

class SignupForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=30)
    first_name = forms.CharField(max_length=30)
    password = forms.CharField(max_length=30)
    confirm_password = forms.CharField(max_length=30)

    class Meta:
        model = models.Profile
        fields = ["avatar"]

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if models.User.objects.filter(username=username).exists():
            self.add_error("username", "This login is already exist")
        return self.cleaned_data.get("username")
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if models.User.objects.filter(email=email).exists():
            self.add_error("email", "This email is already exist")
        return self.cleaned_data.get("email")
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if models.User.objects.filter(first_name=first_name).exists():
            self.add_error("first_name", "This nickname is already exist")
        return self.cleaned_data.get("first_name")

    def clean_confirm_password(self):
        if self.cleaned_data.get("password") != self.cleaned_data.get("confirm_password"):
            self.add_error("confirm_password", "Passwords do not match")
            self.add_error("password", "Passwords do not match")
        return self.cleaned_data.get("confirm_password")
    
    def save(self, commit=True):
        user = models.User.objects.create_user(
            username=self.cleaned_data.get("username"),
            email=self.cleaned_data.get("email"),
            first_name=self.cleaned_data.get("first_name"),
        )
        user.set_password(self.cleaned_data.get("password"))
        user.save()
        profile = models.Profile(
            user=user,
            avatar=self.cleaned_data.get("avatar", None)
        )
        profile.save()
        return profile
    
class SettingsForm(forms.ModelForm):
    username = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=30)
    first_name = forms.CharField(max_length=30)

    class Meta:
        model = models.Profile
        fields = ["avatar"]

    def __init__(self, *args, **kwargs):
        self.user_id = kwargs.pop('user_id', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get("username")
        if models.User.objects.filter(username=username).exclude(id=self.user_id).exists():
            self.add_error("username", "This login is already exist")
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get("email")
        if models.User.objects.filter(email=email).exclude(id=self.user_id).exists():
            self.add_error("email", "This email is already exist")
        return email
    
    def clean_first_name(self):
        first_name = self.cleaned_data.get("first_name")
        if models.User.objects.filter(first_name=first_name).exclude(id=self.user_id).exists():
            self.add_error("first_name", "This nickname is already exist")
        return first_name

    def save(self, commit=True):
        profile = models.Profile.objects.filter(user__id=self.user_id).first()
        profile.user.username = self.cleaned_data.get("username")
        profile.user.email = self.cleaned_data.get("email")
        profile.user.first_name = self.cleaned_data.get("first_name")
        profile.user.save()
        profile.avatar = self.cleaned_data.get("avatar")
        profile.save()
        return profile

class QuestionForm(forms.ModelForm):
    tags = forms.CharField(max_length=100, required=False)

    class Meta:
        model = models.Question
        fields = ["title", "text"]

    def clean_tags(self):
        tags = self.cleaned_data.get("tags", None)
        if tags:
            tags = tags.split()
            if len(tags) > 3:
                raise forms.ValidationError("Please, enter up to 3 tags")
            cleaned_tags = []
            for string in tags:
                string = string.replace(",", "")
                cleaned_tags.append(string)
            return cleaned_tags
        else:
            return tags
    
    def save(self, user_id):
        profile = models.Profile.objects.filter(user__id=user_id).first()
        question = models.Question(
            title=self.cleaned_data.get("title"),
            text=self.cleaned_data.get("text"),
            author=profile,
        )
        question.save()
        tags = self.cleaned_data.get("tags")
        if tags:
            for tag_name in tags:
                tag = models.Tag.objects.filter(name=tag_name).first()
                if not(tag):
                    tag = models.Tag(name=tag_name)
                    tag.save()
                question.tags.add(tag)
        question.save()
        return question

class AnswerForm(forms.ModelForm):
    class Meta:
        model = models.Answer
        fields = ["text"]

    def save(self, user_id, question_id):
        profile = models.Profile.objects.filter(user__id=user_id).first()
        question = models.Question.objects.filter(id=question_id).first()
        answer = models.Answer(
            text=self.cleaned_data.get("text"),
            author=profile,
            question=question,
        )
        answer.save()
        return answer