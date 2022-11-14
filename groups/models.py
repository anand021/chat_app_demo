from django.db import models
from user.models import AppUser, MyBaseModel


class ChatGroups(MyBaseModel):
    name = models.CharField(max_length=100,
                            blank=True, null=True)

    members = models.ManyToManyField(AppUser,
                                  blank=True)
    
    is_deleted = models.BooleanField(default=False)


    class Meta:
        verbose_name = "Group"
        verbose_name_plural = "Groups"

    def __str__(self):
        return self.name


class Messages(MyBaseModel):
    message = models.CharField(max_length=400,
                            blank=False, null=False)

    sender = models.ForeignKey(AppUser, on_delete = models.PROTECT,
                                  blank=False, null=False)
    
    likes_count = models.IntegerField(default=0)

    is_deleted = models.BooleanField(default=False)

    chat_group = models.ForeignKey(ChatGroups, on_delete = models.PROTECT,
                                  blank=False, null=False)


    class Meta:
        verbose_name = "Message"
        verbose_name_plural = "Messages"

    def __str__(self):
        return self.message
    

class MessageLikes(MyBaseModel):
    message = models.ForeignKey(Messages, on_delete = models.CASCADE,
                                  blank=False, null=False)

    liked_by = models.ForeignKey(AppUser, on_delete = models.CASCADE,
                                  blank=False, null=False)
