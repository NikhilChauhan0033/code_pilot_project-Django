# Import Django's built-in models module for defining database models
from django.db import models
# Import Django's built-in User model for authentication
from django.contrib.auth.models import User


# Model to store instructor details
class Instructor(models.Model):
    # Name of instructor
    name = models.CharField(max_length=100)
    # Profession/job title of instructor
    profession = models.CharField(max_length=200)
    # Detailed about section for instructor
    about = models.TextField()
    # Unique email for instructor
    email = models.EmailField(unique=True)
    # Phone number of instructor
    phone_no = models.CharField(max_length=15)
    # Average rating of instructor (float)
    rating = models.FloatField()
    # Profile image uploaded to 'instructors/' folder, optional
    profile_image = models.ImageField(upload_to='instructors/', null=True, blank=True)

    # String representation of instructor in admin panel or shell
    def __str__(self):
        return self.name


# Model to store course details
class Course(models.Model):
    # Choices for main course categories
    CATEGORY_CHOICES = [
        ('full_stack', 'Full Stack Development'),
        ('mobile_app', 'Mobile App Development'),
        ('data_science', 'Data Science'),
        ('data_analytics', 'Data Analytics'),
        ('software_testing', 'Software Testing'),
        ('digital_marketing', 'Digital Marketing'),
        ('ux_ui', 'UX/UI Design'),
        ('cyber_security', 'Cyber Security'),
    ]

    # Choices for subcategories under main categories
    SUBCATEGORY_CHOICES = [
        # Full Stack
        ('mern_stack', 'MERN Stack'),
        ('python_stack', 'Python Stack'),
        ('java_stack', 'Java Stack'),
        ('dotnet_stack', 'DotNet Stack'),

        # Mobile App
        ('android', 'Android'),
        ('ios', 'iOS'),
        ('flutter_app', 'Flutter App'),
        ('flutter_app_development', 'Flutter App Development'),

        # Data Science
        ('data_science_training', 'Data Science Training'),
        ('machine_learning_training', 'Machine Learning Training'),

        # Data Analytics
        ('data_analytics_training', 'Data Analytics Training'),
        ('business_analytics_training', 'Business Analytics Training'),

        # Software Testing
        ('software_testing_training', 'Software Testing Training'),
        ('selenium_automation_training', 'Selenium Automation Training'),
        ('manual_testing_training', 'Manual Testing Training'),

        # Digital Marketing
        ('digital_marketing_training', 'Digital Marketing Training'),

        # UX/UI Design
        ('ux_ui_training', 'UX-UI Training'),

        # Cyber Security
        ('ethical_hacking_training', 'Ethical Hacking Training'),
    ]

    # Course name/title
    course_name = models.CharField(max_length=200)
    # Short description (summary)
    short_description = models.TextField()
    # Detailed description
    long_description = models.TextField()
    # Category choice (from CATEGORY_CHOICES)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    # Subcategory choice, optional
    subcategory = models.CharField(max_length=50, choices=SUBCATEGORY_CHOICES, blank=True, null=True)
    # What students will learn
    learning_outcomes = models.TextField()
    # Price of the course
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Instructor assigned to course, optional
    instructor = models.ForeignKey(Instructor, on_delete=models.CASCADE, related_name='courses', null=True, blank=True)
    # Duration of course (e.g., "4 weeks")
    duration = models.CharField(max_length=50)
    # Number of students enrolled
    students_enrolled = models.PositiveIntegerField()
    # Language of instruction
    language = models.CharField(max_length=50)
    # Certification info
    certification = models.CharField(max_length=100)
    # Rating of course
    rating = models.FloatField()
    # Optional promo video uploaded
    promo_video = models.FileField(upload_to='course_videos/', blank=True, null=True)
    # Technologies/topics covered
    technologies_covered = models.TextField()
    # Old price for discount comparison
    old_price = models.DecimalField(max_digits=10, decimal_places=2)
    # Discount percentage
    discount_percent = models.PositiveIntegerField()
    # Badge (e.g., Bestseller, New), optional
    badge = models.CharField(max_length=50, blank=True, null=True)
    # Difficulty level (Beginner/Intermediate/Advanced), optional
    level = models.CharField(max_length=50, blank=True, null=True)
    # Number of lessons in the course
    lessons_count = models.PositiveIntegerField(default=0)

    # String representation for admin panel
    def __str__(self):
        return f"{self.course_name} ({self.get_category_display()})"


# Cart model to store courses added by a user
class Cart(models.Model):
    # Link to User, if user deleted → cascade delete
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Link to Course, if course deleted → cascade delete
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Timestamp when added to cart, auto-filled
    added_at = models.DateTimeField(auto_now_add=True)

    # String representation for admin panel
    def __str__(self):
        return f"{self.user.username} - {self.course.course_name}"


# Checkout model to store purchase details
class Checkout(models.Model):
    # Payment method choices
    PAYMENT_CHOICES = (
        ('upi', 'UPI'),
        ('paytm', 'Paytm'),
        ('phonepe', 'PhonePe'),
        ('card', 'Credit/Debit Card'),
    )

    # Link to User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Link to Course
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    # Price paid
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Payment method used
    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default='upi')
    # Timestamp when checkout created
    created_at = models.DateTimeField(auto_now_add=True)

    # String representation for admin panel
    def __str__(self):
        return f"{self.user.username} - {self.course.course_name} - {self.payment_method}"


# Favorite courses of a user
class Favorite(models.Model):
    # Link to User
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # Link to Course
    course = models.ForeignKey('Course', on_delete=models.CASCADE)

    class Meta:
        # Ensure no duplicates (user cannot favorite same course twice)
        unique_together = ('user', 'course')


# Contact messages submitted by users
class ContactMessage(models.Model):
    # Name of sender
    name = models.CharField(max_length=100)
    # Email of sender
    email = models.EmailField()
    # Subject (optional)
    subject = models.CharField(max_length=200, blank=True)
    # Message content
    message = models.TextField()
    # Timestamp when message created
    created_at = models.DateTimeField(auto_now_add=True)

    # String representation for admin panel
    def __str__(self):
        return f"Message from {self.name}"


# Email subscribers for newsletter or updates
class Subscriber(models.Model):
    # Subscriber email (unique)
    email = models.EmailField(unique=True)
    # Timestamp when subscribed
    subscribed_at = models.DateTimeField(auto_now_add=True)

    # String representation
    def __str__(self):
        return self.email
