from random import choices
from django.db import models

class CustomUser(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=100)
    otp = models.CharField(max_length=6, blank=True, null=True)

    def __str__(self):
        return self.email


class Profile(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)

    profile_image = models.ImageField(upload_to="profiles/", blank=True, null=True)
    headline = models.CharField(max_length=200, blank=True)

    phone = models.CharField(max_length=20, blank=True)
    location = models.CharField(max_length=100, blank=True)

    linkedin = models.URLField(blank=True)
    github = models.URLField(blank=True)
    website = models.URLField(blank=True)

    skills = models.TextField(blank=True)

    experience_title = models.CharField(max_length=200, blank=True)
    experience_desc = models.TextField(blank=True)

    education_title = models.CharField(max_length=200, blank=True)
    education_desc = models.TextField(blank=True)

    resume = models.FileField(upload_to="resumes/", blank=True, null=True)

    def __str__(self):
        return self.user.email
from django.db import models

class Job(models.Model):
    title = models.CharField(max_length=200)
    company = models.CharField(max_length=200)
    location = models.CharField(max_length=100)
    job_type = models.CharField(
    max_length=50,
    choices=[
        ("Full Time", "Full Time"),
        ("Part Time", "Part Time"),
        ("Internship", "Internship"),
        ("Remote", "Remote"),
    ],
    default="Full Time"
                      )
    salary = models.CharField(max_length=100, blank=True)

    job_description = models.TextField(blank=True)
    required_skills = models.TextField(blank=True)
    responsibilities = models.TextField(blank=True)
    eligibility = models.TextField(blank=True)
    benefits = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = (
        ("Applied", "Applied"),
        ("Shortlisted", "Shortlisted"),
        ("Rejected", "Rejected"),
    )

    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    job = models.ForeignKey(Job, on_delete=models.CASCADE)
    resume = models.FileField(upload_to="leatest_resumes/", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="Applied"
    )
    applied_at = models.DateTimeField(auto_now_add=True)

    # class Meta:
    #     unique_together = ("user", "job")  # 🔒 prevents duplicate apply

    def __str__(self):
        return f"{self.user.name} → {self.job.title}"

