from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from django.utils.text import slugify


# Create your models here.

def upload_to(instance, filename):
    return 'profile/{filename}'.format(filename=filename)

TAGS_CHOICES=(
    ("no-seller", "no-seller"),
    ("seller", "seller"),
)

PRODUCT_SEEN_CHOICES=(
    ("seen", "seen"),
    ("unseen", "unseen"),
    )
class productNotifications(models.Model):
    senderName = models.TextField()
    senderId = models.IntegerField()
    receiver = models.TextField()
    seen = models.CharField(max_length=100, choices=PRODUCT_SEEN_CHOICES)
    text = models.CharField(max_length=100)
    time = models.TimeField(auto_now=False, auto_now_add=False)

    def __str__(self):
        return f"{self.text}-{self.receiver}"

FOLLOWING_CHOICES=(
    ("yes", "yes"),
    ("no", "no",)
)
BLOCKEDUSERS_CHOICES=(
    ("true", "true"),
    ("false", "false",)
)

class Profile(models.Model):
    user= models.OneToOneField(User, on_delete=models.CASCADE)
    pics = models.ImageField(null = True, blank =True, upload_to=upload_to, default='/profile/default.png')
    location = models.CharField(max_length=70,null = True, blank =True)
    ratings_value=models.IntegerField( null=True, blank=True)
    voucher= models.CharField(max_length=100,null = True, blank =True)
    tags=models.TextField(choices=TAGS_CHOICES, default="no-seller")
    blocked=models.TextField(choices=BLOCKEDUSERS_CHOICES, default="false")
    followers= models.ManyToManyField(User,related_name="followers", symmetrical=False, blank=True)
    following= models.ManyToManyField(User,related_name="following", symmetrical=False, blank=True)
    banckAccount=models.IntegerField(null=True, blank=True)
    accountNumber=models.IntegerField(null=True, blank=True)
    subaccount_percentage=models.IntegerField(null=True, blank=True)
    subaccountId=models.CharField(max_length=30, null=True, blank=True)
    phoneNumber=models.CharField(null=True, blank=True, max_length=50)
    country=models.CharField(max_length=30, null=True, blank=True)
    state=models.CharField(max_length=30, null=True, blank=True)
    email=models.CharField(max_length=30, null=True, blank=True)
    businessName=models.CharField(max_length=30, null=True, blank=True)
    notification= models.ManyToManyField(productNotifications, related_name="productnotification", blank=True)
    item= models.TextField(null=True, blank=True)
    name=models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.name:
            self.name= slugify(self.user)
        super(Profile, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.user}"

STATUS_CHOICES = (
    ("accept", "accept"),
    ("delete", "delete"),

)

class Relationship(models.Model):
    sender = models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "senders")
    receiver = models.ForeignKey(Profile, on_delete= models.CASCADE, related_name= 'receivers')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES)
    followers= models.IntegerField()

SEEN_CHOICES=(
    ("seen", "seen"),
    ("unseen", "unseen"),
    )

class Notifications(models.Model):
    sender = models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "notification_senders")
    senderName = models.TextField()
    receiver = models.ForeignKey(Profile, on_delete= models.CASCADE, related_name= 'notification_receivers')
    text = models.CharField(max_length=100)
    time = models.TimeField(auto_now=False, auto_now_add=False)
    seen=models.CharField(max_length=100, choices=SEEN_CHOICES)


    def __str__(self):
        return f"{self.text}-{self.receiver}"

class Review(models.Model):
    value=models.IntegerField()
    text=models.TextField(null=True, blank=True)
    sender = models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "sender_review")
    sender_name= models.CharField(max_length=50,null=True, blank=True,)
    receiver = models.ForeignKey(Profile, on_delete= models.CASCADE,  related_name= "receiver_review")
    pics= models.ImageField(null=True, blank=True,)
    def __str__(self):
        return f"{self.value}-{self.receiver}"
