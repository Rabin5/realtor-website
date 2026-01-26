from django import forms
from .models import ContactInquiry, Listing, Contact, Review

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactInquiry
        fields = ['listing','name','email','phone','message']
        widgets = {'listing': forms.HiddenInput()}

class ListingSearchForm(forms.Form):
    q = forms.CharField(required=False, label='Search')
    min_price = forms.DecimalField(required=False, decimal_places=2)
    max_price = forms.DecimalField(required=False, decimal_places=2)
    beds = forms.IntegerField(required=False)
    city = forms.CharField(required=False)

# class ContactForm1(forms.ModelForm):

#     class Meta:
#         model = Contact
#         fields = ['name', 'email', 'phone', 'message']

#     def clean_phone(self):
#         phone = self.cleaned_data.get('phone', '').strip()
#         # optional: simple digits-only normalization or validation
#         return phone

# from django import forms

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class':'form-control', 'placeholder':'Full Name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class':'form-control', 'placeholder':'Email Address'
    }))
 
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class':'form-control', 'placeholder':'Message', 'rows':4
    }))




# class BuyerQuestionnaireForm(forms.Form):
#     PROPERTY_CHOICES = [('house', 'House'), ('apartment', 'Apartment'), ('townhome', 'Townhome')]
#     BUDGET_CHOICES = [('100-200', '$100k–$200k'), ('200-400', '$200k–$400k'), ('400+', '$400k+')]
#     LOCATION_CHOICES = [('killeen', 'Killeen'), ('heights', 'Harker Heights'), ('temple', 'Temple')]
#     BEDROOM_CHOICES = [('1-2', '1–2'), ('3-4', '3–4'), ('5+', '5+')]

#     property_type = forms.ChoiceField(choices=PROPERTY_CHOICES, widget=forms.RadioSelect)
#     budget = forms.ChoiceField(choices=BUDGET_CHOICES, widget=forms.RadioSelect)
#     location = forms.ChoiceField(choices=LOCATION_CHOICES, widget=forms.RadioSelect)
#     bedrooms = forms.ChoiceField(choices=BEDROOM_CHOICES, widget=forms.RadioSelect)



class Step1Form(forms.Form):
    PROPERTY_CHOICES = [
        ('house', 'House'),
        ('apartment', 'Apartment'),
        ('townhome', 'Townhome')
    ]
    property_type = forms.ChoiceField(
        choices=PROPERTY_CHOICES, widget=forms.RadioSelect, label="What type of property are you looking for?"
    )

class Step2Form(forms.Form):
    BUDGET_CHOICES = [
        ('100-200', '$100k–$200k'),
        ('200-400', '$200k–$400k'),
        ('400+', '$400k+')
    ]
    budget = forms.ChoiceField(
        choices=BUDGET_CHOICES, widget=forms.RadioSelect, label="What is your budget range?"
    )

class Step3Form(forms.Form):
    LOCATION_CHOICES = [
        ('killeen', 'Killeen'),
        ('heights', 'Harker Heights'),
        ('temple', 'Temple')
    ]
    location = forms.ChoiceField(
        choices=LOCATION_CHOICES, widget=forms.RadioSelect, label="Preferred location?"
    )

class Step4Form(forms.Form):
    BEDROOM_CHOICES = [
        ('1-2', '1–2'),
        ('3-4', '3–4'),
        ('5+', '5+')
    ]
    bedrooms = forms.ChoiceField(
        choices=BEDROOM_CHOICES, widget=forms.RadioSelect, label="How many bedrooms do you need?"
    )



# listings/forms.py


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['name', 'email', 'rating', 'comment', 'category', 'location', 'property_related']
        
    def save(self, commit=True):
        print("=== DEBUG: ReviewForm.save() called ===")
        print(f"Form data: {self.cleaned_data}")
        
        # Call parent save
        review = super().save(commit=False)
        
        print(f"Review object created: {review}")
        print(f"Review will be saved with commit={commit}")
        
        if commit:
            review.save()
            print(f"Review saved! ID: {review.id}")
        
        return review
    class Meta:
        model = Review
        fields = ['name', 'email', 'rating', 'category', 'comment', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Full Name *',
                'required': True,
                'id': 'reviewName'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address (Optional)',
                'id': 'reviewEmail'
            }),
            'rating': forms.HiddenInput(attrs={
                'id': 'reviewRating'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control',
                'id': 'reviewCategory'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience with Raja... *',
                'rows': 6,
                'required': True,
                'id': 'reviewComment'
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State (Optional)',
                'id': 'reviewLocation'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Set initial values for required fields
        self.fields['rating'].initial = 5
        self.fields['category'].initial = 'general'
        
    def clean(self):
        cleaned_data = super().clean()
        # Debug: Print cleaned data
        print("Form cleaned data:", cleaned_data)
        return cleaned_data
    class Meta:
        model = Review
        fields = ['name', 'email', 'rating', 'category', 'comment', 'location']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name',
                'required': True
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email (Optional)'
            }),
            'comment': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Share your experience...',
                'rows': 6,
                'required': True
            }),
            'location': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'City, State (Optional)'
            }),
            'category': forms.Select(attrs={
                'class': 'form-control'
            }),
        }
    
    rating = forms.IntegerField(
        widget=forms.HiddenInput(),
        initial=5
    )
    
    def clean_rating(self):
        rating = self.cleaned_data['rating']
        if rating < 1 or rating > 5:
            raise forms.ValidationError("Rating must be between 1 and 5")
        return rating
    
        def save(self, commit=True):
            print("=== DEBUG: ReviewForm.save() called ===")
            print(f"Form data: {self.cleaned_data}")
            
            # Call parent save
            review = super().save(commit=False)
            
            print(f"Review object created: {review}")
            print(f"Review will be saved with commit={commit}")
            
            if commit:
                review.save()
                print(f"Review saved! ID: {review.id}")
            
            return review