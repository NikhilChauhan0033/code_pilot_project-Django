# Import render → used to load and display HTML templates with context data.
# Import redirect → sends the user to another URL without rendering a template.
# Import get_object_or_404 → fetches an object or returns a 404 page if not found.
from django.shortcuts import render, redirect, get_object_or_404

# Import Django's built-in User model → handles users, passwords, auth system.
from django.contrib.auth.models import User

# authenticate → checks whether username & password are correct.
# login as auth_login → logs the user in and creates a session.
# logout as auth_logout → logs the user out and destroys the session.
from django.contrib.auth import authenticate, login as auth_login, logout as auth_logout

# login_required decorator → restricts views to logged-in users only.
from django.contrib.auth.decorators import login_required

# messages → allows you to show success/error/info messages to users.
from django.contrib import messages

# update_session_auth_hash → keeps user logged in after password update.
from django.contrib.auth import update_session_auth_hash

# Import all models used in this file (Course, Cart, Checkout, Favorite, etc.)
from .models import Course, Instructor, Cart, Checkout, Favorite, ContactMessage, Subscriber

# JsonResponse → used when returning JSON data (usually for AJAX requests).
from django.http import JsonResponse

# render_to_string → loads a template and returns it as pure HTML string.
from django.template.loader import render_to_string

# Q object → allows OR/AND complex queries in Django filters (used in search).
from django.db.models import Q

# A secret key for verifying admin users.
# Hardcoded here, but in real applications you should use environment variables.
ADMIN_SECRET_KEY = 'superadmin123'


# This decorator checks if the user is logged in before allowing access to a view.
# If not authenticated:
#     → It shows a warning message
#     → It redirects the user to the home (index) page.
# Decorator uses *args and **kwargs to support all types of view parameters.
def login_required_redirect(view_func):
    def wrapper(request, *args, **kwargs):
        
        # If the user is NOT logged in
        if not request.user.is_authenticated:
            
            # Show warning message
            messages.warning(request, "Please login or register to access this page.")
            
            # Redirect to homepage
            return redirect('index')
        
        # If user is authenticated, continue to the original view
        return view_func(request, *args, **kwargs)
    
    # Return the modified wrapped function
    return wrapper


# Handles registration page processing.
def register(request):

    # If the user is already logged in → redirect to homepage
    if request.user.is_authenticated:
        return redirect('index')

    # If a form is submitted (POST request)
    if request.method == "POST":

        # Retrieve form inputs and remove extra spaces
        username = request.POST['username'].strip()
        email = request.POST['email'].strip()
        password = request.POST['password']
        confirm_password = request.POST['confirm_password']

        # If any field is empty → show error and reload page
        if not username or not email or not password or not confirm_password:
            messages.error(request, "All fields are required.")
            return redirect('index')

        # request.session → stores temporary data for the user (like modal state)
        # If passwords do not match
        if password != confirm_password:
            messages.error(request, "Passwords do not match.")
            request.session['open_modal'] = 'register'  # reopen register modal
            return redirect('index')

        # Check if username already exists
        if User.objects.filter(username=username).exists():
            messages.error(request, "Username already exists.")
            request.session['open_modal'] = 'register'
            return redirect('index')

        # Check if email already exists
        if User.objects.filter(email=email).exists():
            messages.error(request, "Email already registered.")
            request.session['open_modal'] = 'register'
            return redirect('index')

        # Create the new user
        User.objects.create_user(username=username, email=email, password=password)

        # Success message and open login modal
        messages.success(request, "Registration successful. Please log in.")
        request.session['open_modal'] = 'login'
        return redirect('index')

    # If request is GET → show index page
    return render(request, 'index.html')



def login(request):

    # If user is already logged in → send to homepage
    if request.user.is_authenticated:
        return redirect('index')

    # If form is submitted
    if request.method == "POST":

        # identifier can be username OR email
        identifier = request.POST['identifier'].strip()
        password = request.POST['password']

        # First check if identifier matches username
        # If not found, check email
        user = (
            User.objects.filter(username=identifier).first() or
            User.objects.filter(email=identifier).first()
        )

        print(user)

        # If user exists → try authentication
        if user:
            user = authenticate(username=user.username, password=password)

            # If password correct
            if user:
                auth_login(request, user)   # Log the user in
                messages.success(request, f"Welcome, {user.username}!")

                # If superuser (admin) → ask for admin verification
                if user.is_superuser:
                    request.session['admin_verified'] = False
                    messages.info(request, "Please verify your admin key.")
                    return redirect('verify-admin')

                # Normal user → login completely
                else:
                    request.session['admin_verified'] = True
                    request.session['open_modal'] = None
                    return redirect('index')

            else:
                # Wrong password
                messages.error(request, "Incorrect password.")
                request.session['open_modal'] = 'login'
        else:
            # No user found with username/email
            messages.error(request, "User not found.")
            request.session['open_modal'] = 'login'

        return redirect('index')

    # GET request → show index page
    return render(request, 'index.html')


# Decorator to make sure only authenticated users can access this view
# If user is not logged in, redirect them to 'index' page
@login_required_redirect
def verify_admin_key(request):
    # Check if the form is submitted via POST method
    if request.method == 'POST':
        # Get the 'key' input from the submitted form and remove spaces
        key = request.POST.get('key', '').strip()
        # Compare the submitted key with the hardcoded admin secret key
        if key == ADMIN_SECRET_KEY:
            # Store admin verification status in session
            request.session['admin_verified'] = True
            # Show success message to user
            messages.success(request, "Admin verified successfully.")
            # Redirect to home page after successful verification
            return redirect('index')  # or wherever you want
        else:
            # Show error message if key is invalid
            messages.error(request, "Invalid admin key.")
            # Redirect back to verify-admin page to try again
            return redirect('verify-admin')

    # Render the admin verification HTML page if GET request
    return render(request, 'verify_admin.html')


# Logs out the currently logged-in user
def logout(request):
    # Django built-in logout function clears session and logs out user
    auth_logout(request)
    # Display a message to confirm logout
    messages.success(request, "You have been logged out.")
    # Redirect user to homepage after logout
    return redirect('index')


# View for user's profile page (update profile info)
@login_required_redirect
def profile(request):
    # Prevent superuser/admin from updating profile
    if request.user.is_superuser:
        messages.error(request, "Admins are not allowed to update their profile.")
        return redirect('index')

    # Handle form submission when user updates profile
    if request.method == 'POST':
        # Get new username and remove spaces
        new_username = request.POST['username'].strip()
        # Get new email and remove spaces
        new_email = request.POST['email'].strip()
        # Get old password (optional, used for changing password)
        old_password = request.POST.get('old_password', '').strip()
        # Get new password (optional)
        new_password = request.POST.get('new_password', '').strip()
        # Get confirm password field (optional)
        confirm_password = request.POST.get('confirm_password', '').strip()

        # Ensure username and email are not empty
        if not new_username or not new_email:
            messages.error(request, "Username and Email are required.")
            return redirect('profile')

        # Check if new username is already taken by other users
        if User.objects.exclude(id=request.user.id).filter(username=new_username).exists():
            messages.error(request, "Username is already taken.")
            return redirect('profile')
        # Check if new email is already used by other users
        if User.objects.exclude(id=request.user.id).filter(email=new_email).exists():
            messages.error(request, "Email is already used.")
            return redirect('profile')

        # Update the user's username
        request.user.username = new_username
        # Update the user's email
        request.user.email = new_email

        # Handle password change if user provided a new password
        if new_password:
            # Require old password to confirm identity
            if not old_password:
                messages.error(request, "Please enter your old password to set a new one.")
                return redirect('profile')

            # Check if old password is correct
            if not request.user.check_password(old_password):
                messages.error(request, "Old password is incorrect.")
                return redirect('profile')

            # Ensure new password and confirm password match
            if new_password != confirm_password:
                messages.error(request, "New passwords do not match.")
                return redirect('profile')

            # Set new password
            request.user.set_password(new_password)
            # Keep user logged in after password change
            update_session_auth_hash(request, request.user)

        # Save the updated user information to the database
        request.user.save()
        # Show success message
        messages.success(request, "Profile updated successfully.")
        # Redirect back to profile page
        return redirect('profile')

    # Render profile page if request is GET
    return render(request, 'profile.html')


# Home page view to show courses and instructors
def index(request): #we also use this [{% for course in courses|slice:":4" %} in templates for show only 4 courses]
    # Fetch first 4 courses from database
    courses = Course.objects.all()[:4]  # fetch all courses 
    # Fetch first 4 instructors from database
    instructors = Instructor.objects.all()[:4]  # fetch all instructors
    # Render index.html and pass courses and instructors
    return render(request, 'index.html', {'courses': courses, 'instructors': instructors})


# Show details of a single course
def course_detail(request, course_id):
    # Get the course object by ID or return 404 if not found
    course = get_object_or_404(Course, id=course_id)
    # Render course detail page and pass the course object
    return render(request, 'course_detail.html', {'course': course})


# Show details of a single instructor
def instructor_detail(request, instructor_id):
    # Get the instructor object by ID or return 404 if not found
    instructor = get_object_or_404(Instructor, id=instructor_id)
    # Render instructor detail page and pass the instructor object
    return render(request, 'instructor_detail.html', {'instructor': instructor})


# Add a course to the user's cart
@login_required_redirect
def add_to_cart(request, course_id):
    # Get the course object by ID
    course = get_object_or_404(Course, id=course_id)
    # Get existing cart item or create a new one
    cart_item, created = Cart.objects.get_or_create(user=request.user, course=course)
    # created=True → new item added, created=False → item already in cart

    # Handle AJAX request for updating cart without page reload
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
        # Count how many items are in user's cart
        count = Cart.objects.filter(user=request.user).count() 
        # Return JSON response with cart status and count
        return JsonResponse({'status': 'success', 'added': created, 'count': count})

    # If not AJAX, redirect to course detail page
    return redirect('course_detail', course_id=course.id)


# View the user's cart page
@login_required_redirect
def view_cart(request):
    # Get all cart items for the logged-in user
    cart_items = Cart.objects.filter(user=request.user)
    # Calculate total price by summing the price of each course in the cart
    total = sum(item.course.price for item in cart_items)
    # Render cart.html template and pass cart items and total price
    return render(request, 'cart.html', {'cart_items': cart_items, 'total': total})


# Remove a specific item from the cart
@login_required_redirect
def remove_from_cart(request, item_id):
    # Only allow POST requests sent via AJAX
    if request.method == "POST" and request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the specific cart item for the user or return 404 if not found
        item = get_object_or_404(Cart, id=item_id, user=request.user)
        # Delete the cart item
        item.delete()
        # Count remaining items in cart
        count = Cart.objects.filter(user=request.user).count()
        # Calculate new total price after deletion
        total = sum(i.course.price for i in Cart.objects.filter(user=request.user))
        # Return JSON response with updated cart count and total
        return JsonResponse({'status': 'success', 'count': count,'total': total})
    
    # Redirect back to previous page if not an AJAX POST request
    return redirect(request.META.get('HTTP_REFERER', 'view_cart'))


# Checkout page for purchasing courses
@login_required_redirect
def checkout(request):
    # Get all cart items for the logged-in user
    cart_items = Cart.objects.filter(user=request.user)
    # Check if a single course ID is provided in query parameters
    course_id = request.GET.get('course_id')
    single_course = None

    # If cart is empty but course_id is provided, get that single course
    if not cart_items and course_id:
        single_course = get_object_or_404(Course, id=course_id)

    # Handle form submission for checkout
    if request.method == 'POST':
        # Get selected payment method
        payment_method = request.POST.get('payment_method')

        # Show error if payment method is not selected
        if not payment_method:
            messages.error(request, "Please select a payment method.")
            return redirect('checkout')

        # If user has multiple items in cart
        if cart_items:
            # Create checkout entry for each cart item
            for item in cart_items:
                Checkout.objects.create(
                    user=request.user,
                    course=item.course,
                    price=item.course.price,
                    payment_method=payment_method
                )
            # Remove all items from cart after checkout
            cart_items.delete()
        # If single course was selected directly
        elif single_course:
            Checkout.objects.create(
                user=request.user,
                course=single_course,
                price=single_course.price,
                payment_method=payment_method
            )

        # Show success message after checkout
        messages.success(request, "Checkout successful!")
        # Redirect to checkout history page
        return redirect('checkout_history')

    # Calculate total price: sum of cart or single course
    total = sum(item.course.price for item in cart_items) if cart_items else (single_course.price if single_course else 0)

    # Render checkout page and pass cart/single course info and total
    return render(request, 'checkout.html', {
        'cart_items': cart_items,
        'single_course': single_course,
        'total': total
    })


# View user's checkout/purchase history
@login_required_redirect
def checkout_history(request):
    # Get all checkout entries for logged-in user, newest first
    checkout_items = Checkout.objects.filter(user=request.user).order_by('-created_at')
    # Render checkout history template and pass checkout items
    return render(request, 'checkout_history.html', {'checkout_items': checkout_items})


# Add or remove a course from user's favorites
@login_required_redirect
def toggle_favorite(request, course_id):
    # Only handle AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get the course object
        course = get_object_or_404(Course, id=course_id)
        # Get existing favorite or create a new one
        fav, created = Favorite.objects.get_or_create(user=request.user, course=course)

        # If favorite already exists, remove it
        if not created:
            fav.delete()
            return JsonResponse({'status': 'removed'})
        # If new favorite added
        return JsonResponse({'status': 'added'})


# View all favorite courses of the user
@login_required_redirect
def view_favorites(request):
    # Get all favorite entries for logged-in user
    favorites = Favorite.objects.filter(user=request.user)
    # Render favorites page and pass favorite courses
    return render(request, 'favorites.html', {'favorites': favorites})


# Remove a course from favorites
@login_required_redirect
def remove_from_favorites(request, course_id):
    # Only allow AJAX requests
    if request.headers.get('x-requested-with') == 'XMLHttpRequest':
        # Get favorite entry if exists
        fav = Favorite.objects.filter(user=request.user, course_id=course_id).first()
        if fav:
            # Delete favorite entry
            fav.delete()
            return JsonResponse({'status': 'success'})
        # If favorite not found
        return JsonResponse({'status': 'not_found'})
    # Redirect to favorites page if not AJAX
    return redirect('view_favorites')


# About Us page
def about_us(request):
    # Simply render the about_us.html template
    return render(request,'about_us.html')


# Contact form page (user can send a message)
# @login_required_redirect (optional: allow only logged-in users)
def contact_us(request):
    # Handle form submission
    if request.method == 'POST':
        # Get form fields
        name = request.POST.get('name')
        email = request.POST.get('email')
        subject = request.POST.get('subject')
        message = request.POST.get('message')

        # Ensure required fields are filled
        if name and email and message:
            # Save message to database
            ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message
            )
            # Show success message
            messages.success(request, "✅ Thank you! We will connect with you shortly.")
            # Redirect back to contact page
            return redirect('contact_us')
        else:
            # Show error if required fields are missing
            messages.error(request, "❌ Please fill all required fields.")

    # Render contact form template
    return render(request, 'contact_us.html')


# Load cart snippet dynamically for AJAX (used in header/cart icon)
@login_required_redirect
def load_cart_snippet(request):
    # Get all cart items for logged-in user
    cart_items = Cart.objects.filter(user=request.user)
    # Calculate total price of items in cart
    total = sum(item.course.price for item in cart_items)
    # Render HTML snippet for cart (partials/cart_snippet.html)
    html = render_to_string("partials/cart_snippet.html", {
        "cart_items": cart_items,  # Pass cart items to template
        "cart_total": total,       # Pass total price to template
    }, request=request)

    # Return HTML as JSON (used in AJAX to update cart icon dynamically)
    return JsonResponse({'html': html})


# Suggest course names while user types in search bar
def search_suggestions(request):
    # Get query parameter 'q' from GET request
    query = request.GET.get('q', '')
    if query:
        # Find courses where course_name contains query (case-insensitive)
        courses = Course.objects.filter(course_name__icontains=query)
        # Prepare a list of dictionaries with course id and name
        data = [{'id': c.id, 'name': c.course_name} for c in courses]
        # Return JSON response for frontend autocomplete
        return JsonResponse(data, safe=False)
    # Return empty list if no query
    return JsonResponse([], safe=False)


# Redirect user to course detail page after search
def search_course_redirect(request):
    # Get query parameter 'q' from GET request
    query = request.GET.get('q', '')
    if query:
        # Find first course that matches the search query
        course = Course.objects.filter(course_name__icontains=query).first()
        if course:
            # Redirect to the detail page of that course
            return redirect('course_detail', course_id=course.id)
    # Redirect to index page if no match found
    return redirect('index')


# Show all instructors page
def instructors(request):
    # Fetch all instructors from database
    all_instructors = Instructor.objects.all()
    # Render instructors page and pass all instructors
    return render(request,'instructors.html',{"all_instructors":all_instructors})


# Show all courses page
def courses(request):
    # Fetch all courses from database
    all_courses = Course.objects.all()
    # Render courses page and pass all courses
    return render(request,'courses.html',{"all_courses":all_courses})


# Subscribe user email to newsletter or mailing list
def subscribe_email(request):
    if request.method == 'POST':
        # Get email input from POST data
        email = request.POST.get('email')
        if email:
            # Check if email already exists in Subscriber model
            if not Subscriber.objects.filter(email=email).exists():
                # Create new subscriber entry
                Subscriber.objects.create(email=email)
                messages.success(request, "✅ Subscribed successfully!")
            else:
                # Inform user they are already subscribed
                messages.info(request, "ℹ️ You are already subscribed.")
        else:
            # Show error if email is empty or invalid
            messages.error(request, "❌ Please enter a valid email.")

        # Redirect back to previous page or homepage
        return redirect(request.META.get('HTTP_REFERER', '/'))
    

# Payment success page
def payment_success(request):
    # Render payment success template
    return render(request, 'payment_success.html')


# Payment failed page
def payment_failed(request):
    # Render payment failed template
    return render(request, 'payment_failed.html')


# Custom 404 error page
def custom_404_view(request, exception):
    # Render custom 404 page with HTTP status 404
    return render(request, '404.html', status=404)
