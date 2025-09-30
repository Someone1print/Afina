from django.db import models

class Income(models.Model):
    id = models.AutoField(primary_key=True)  # Django и так автоматически добавляет id, но можно явно указать
    incomename = models.CharField(max_length=255)  # название/сумма дохода

    def __str__(self):
        return f"{self.id} - {self.incomename}"
