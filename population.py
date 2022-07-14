import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

import django

django.setup()

from django.core.management import call_command
import csv
from django.contrib.auth import get_user_model
from django.contrib.auth.models import Group


User = get_user_model()

with open("/home/pamungkas/Project/rest-service/data/rpl3.csv") as f:
    group_student, created = Group.objects.get_or_create(name="student")
    csv_reader = csv.reader(f)
    count = 0
    print("________SISWA_________")
    print("Membuat akun untuk murid")
    for row in csv_reader:
        nis = row[0]
        name = row[1]
        print(nis, name)
        if count == 0:
            print("skipp")
        else:
            user = User.objects.create(
                username=nis,
                first_name=name,
            )
            user.set_password((lambda x: "password" if x == "" else x)(nis))
            user.groups.add(group_student)
            user.save()
            print(f"Success membuat akun untuk {row[0]}")
        count += 1

with open("/home/pamungkas/Project/rest-service/data/guru.csv") as f:
    group_teacher, created = Group.objects.get_or_create(name="teacher")
    csv_reader = csv.reader(f)
    count = 0
    print("________GURU_________")
    print("Membuat akun untuk guru")
    for row in csv_reader:
        nis = row[0]
        name = row[1]
        print(nis, name)
        if count == 0:
            print("skipp")
        else:
            user = User.objects.create(
                username=nis,
                first_name=name,
            )
            user.set_password((lambda x: "password" if x == "" else x)(nis))
            user.groups.add(group_teacher)
            user.save()
            print(f"Success membuat akun untuk {row[0]}")
        count += 1
