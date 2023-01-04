import random
from django.db import models
from datetime import datetime, timezone
from .logic.commissionnumber import CommissionNumber

# Token entity
class Token(models.Model):

    # pk
    id = models.AutoField(primary_key=True)

    # bearer token
    token = models.TextField()

    # creation date
    date = models.DateTimeField()

    # returns the youngest token
    @staticmethod
    def get_last():
        try:
            return Token.objects.order_by('date').last()
        except AttributeError:
            return None

# class end


# Quote class
class Quote(models.Model):
    # pk
    id = models.AutoField(primary_key=True)

    # quote
    quote = models.TextField()

    # returns a random quote
    @staticmethod
    def random_quote() -> str:
        objects = Quote.objects
        count = objects.count()
        rand_id = random.randint(1, count)
        return objects.filter(id=rand_id).get().quote

# class end


class Request(models.Model):
    # pk
    id = models.AutoField(primary_key=True)

    # request date
    date = models.DateTimeField()

    # commission number prefix
    prefix = models.CharField(max_length=2)

    # commission number suffix
    suffix = models.CharField(max_length=4)

    @staticmethod
    def persist(commission_number: CommissionNumber):
        request = Request()
        request.date = datetime.now().astimezone(timezone.utc)
        request.prefix = commission_number.number[:2]
        request.suffix = commission_number.number[2:]
        request.save()

# class end