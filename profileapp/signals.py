from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User, Group
from .models import Profile, Relationship, Review, productNotifications

@receiver(post_save, sender=User)
def profile_create(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)

@receiver(post_save, sender=Review)
def review_created(sender, instance, created, **kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    profile= Profile.objects.get(user=receiver_.id)

    if created:
        five= Review.objects.filter(value__exact=5, receiver=receiver_.id).count()
        four= Review.objects.filter(value__exact=4, receiver=receiver_.id).count()
        three= Review.objects.filter(value__exact=3, receiver=receiver_.id).count()
        two= Review.objects.filter(value__exact=2, receiver=receiver_.id).count()
        one= Review.objects.filter(value__exact=1, receiver=receiver_.id).count()
        total=five+four+three+two+one
        rating_collected= ((5*five)+(4*four)+(3*three)+(2*two)+(1*one))
        rating=0
        if total<1 and rating_collected<1:
            rating=0
        else:
            rating=rating_collected//total

        sender_profile=Profile.objects.get(user=sender_.id)
        pics_=sender_profile.pics
        instance.pics=pics_
        instance.save(update_fields=["pics"])

        instance.sender_name=sender_.user.username
        instance.save(update_fields=["sender_name"])
                

       

        

        # updating the ratings value with "profile"
        profile.ratings_value=rating
        profile.save(update_fields=["ratings_value"])

@receiver(post_save, sender=Relationship)
def followers(sender, instance, created, **kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    if instance.status=="accept":
        receiver_.followers.add(sender_.user)
        sender_.following.add(receiver_.user)
        sender_.save()

@receiver(post_save, sender=Relationship)
def unfollow(sender, instance, created, **kwargs):
    sender_ = instance.sender
    receiver_ = instance.receiver
    if instance.status=="delete":
        receiver_.followers.remove(sender_.user)
        sender_.save()
        
@receiver(post_save, sender=productNotifications)
def addNotifications(sender, instance, created, **kwargs):
    if created:
        sender_ = instance.id
        receiver_ = instance.receiver
        for i in instance.receiver:
            if i.isdigit():
                profile= Profile.objects.get(user=int(i))
                profile.notification.add(instance)
                profile.save()

@receiver(post_save, sender=Group)
def blockuser(sender, instance, created, **kwargs):
    sender_profile=Profile.objects.get(user=sender_.id)
    pics_=sender_profile.pics
    instance.pics=pics_
    instance.save(update_fields=["pics"])