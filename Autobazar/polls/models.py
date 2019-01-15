from django.db import models
import json
# Create your models here.

class User(models.Model):
    is_admin = models.BooleanField(default=True)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=50)
    phone = models.CharField(max_length=50)
    email = models.CharField(max_length=50)



class Car(models.Model):
    mark = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    images_paths = models.CharField(max_length=50, default=json.dumps([]))
    owner = models.ForeignKey(User, on_delete=models.CASCADE)
    manufacture_date = models.CharField(max_length=50)
    killometres = models.CharField(max_length=50)
    price = models.CharField(max_length=50)
    motorization = models.CharField(max_length=50)
    performance_kw = models.CharField(max_length=50)
    performance_hp = models.CharField(max_length=50)
    add_date = models.DateField(max_length=50)
    fuel_type = models.CharField(max_length=50)
    repair = models.CharField(max_length=500)
    defects = models.CharField(max_length=500)
    description = models.CharField(max_length=500)



    def set_image(self, image_path):
        images = json.loads(self.images_paths)
        images.append(image_path)
        self.images_paths = json.dumps(images)

    def get_images(self):
        return json.loads(self.images_paths)