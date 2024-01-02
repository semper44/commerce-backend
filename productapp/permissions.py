from rest_framework import permissions
from django.contrib.auth.models import Group, User
from profileapp.models import Profile

class SellersPermission(permissions.BasePermission):
    message = "Sorry, you have been blocked from using this service or do not have the necessary permissions."

    def has_permission(self, request, view):
        user = request.user

        if user.is_authenticated:
            sellers_group_exists = User.objects.filter(id=user.id, groups__name="bannedSellers").exists()
            users_group_exists = User.objects.filter(id=user.id, groups__name="bannedUsers").exists()

            try:
                blocked_profile = Profile.objects.get(user=user)

                if blocked_profile.blocked and (users_group_exists or sellers_group_exists):
                    return False
            except Profile.DoesNotExist:
                pass

        return True
    

# class BannedUser(permissions.BasePermission):

#     # edit_methods = ("PUT", "PATCH", "DELETE")
#     message= "sorry you have been blocked from using this service or you do not have the necessary permissions"
#     # message2= "sorry you have been blocked from using this service"
#     def has_permission(self, request, view):
#         # group= Group.objects.filter(name = "bannedSellers")
#         # userUser= User.objects.get(id =  request.user.id)
#         # userProfile= Profile.objects.filter(user =  request.user, tags="seller")
#         usergroup= User.objects.filter(id = request.user.id, groups__name= "bannedUsers")
#         #         print(usergroup.exists())
#         # print(userProfile.exists())
#         try:
#             if request.user.is_superuser or(request.user.is_authenticated and userProfile.exists() and (usergroup.exists() == False)):
#                 #                 return True
#         except:
#             #             return False       
        # return False