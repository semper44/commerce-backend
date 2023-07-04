from rest_framework import permissions
from django.contrib.auth.models import Group, User
from profileapp.models import Profile



class Sellerspermission(permissions.BasePermission):
    message= "sorry you have been blocked from using this service or you do not have the necessary permissions"
    # message2= "sorry you have been blocked from using this service"
    def has_permission(self, request, view):
        userProfile= Profile.objects.filter(user =  request.user, tags="seller")
        sellersgroup= User.objects.filter(id = request.user.id, groups__name= "bannedSellers")
        usersgroup= User.objects.filter(id = request.user.id, groups__name= "bannedUsers")
        try:
            if request.user.is_superuser or(request.user.is_authenticated and userProfile.exists() and (sellersgroup.exists() == False)):
                                return True
            # elif request.user.is_superuser or(request.user.is_authenticated and userProfile.exists() and (usersgroup.exists() == False)):
            #                 #     return True
        except:

                        return False       

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