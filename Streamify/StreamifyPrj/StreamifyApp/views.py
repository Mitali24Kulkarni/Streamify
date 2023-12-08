from django.shortcuts import render, redirect
from django.views import View
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import logout
from django.http import HttpResponseRedirect
from django.utils import timezone
from . forms import ProfileForm, SubscriptionForm
from . models import Profile, Movie, Subscription
import razorpay

class Home(View):
    def get(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return render(request, 'index.html')
        elif not request.user.has_active_subscription():
            return redirect('StreamifyApp:subscribe')
        return redirect('StreamifyApp:profile-list')


method_decorator(login_required, name='dispatch')
class ProfileList(View):
    def get(self, request, *args, **kwargs):
        profiles = request.user.profiles.all()
        context = {
            'profiles' : profiles
        }
        return render(request, 'profilelist.html', context)
     
method_decorator(login_required, name='dispatch')
class ProfileCreate(View):
    def get(self, request, *args, **kwargs):

        form = ProfileForm()
        context = {'form': form}
        return render(request, 'profilecreate.html', context)


    def post(self, request, *args, **kwargs):
        form  = ProfileForm(request.POST or None)
        if form.is_valid():
            profile = Profile.objects.create(**form.cleaned_data)
            if profile:
                request.user.profiles.add(profile)
                return redirect('StreamifyApp:profile-list')
        context = {
            'profiles' : profiles
        }
        return render(request, 'profilelist.html', context)    

method_decorator(login_required, name='dispatch')
class MovieList(View):
    def get(self, request, profile_id,  *args, **kwargs):
        try:
            profile = Profile. objects.get(uuid=profile_id)
            movies =  Movie.objects.filter(age_limit = profile.age_limit)
            subscription = Subscription.objects.filter(user=request.user, is_active=True).first()
            if subscription is None:
                return redirect('StreamifyApp:subscribe')
            if profile not in request.user.profiles.all():
                return redirect('StreamifyApp:profile-list')
            context = {
                'movies' : movies
            }            
            return render(request, 'movielist.html', context)
        except Profile.DoesNotExist:
            return redirect('StreamifyApp:profile-list')

method_decorator(login_required, name='dispatch')
class MovieDetail(View):
    def get(self, request, movie_id,  *args, **kwargs):
        try:
            movie =  Movie.objects.get(uuid = movie_id)

            context = {
                'movie' : movie
            }            
            return render(request, 'moviedetail.html', context)
        except Movie.DoesNotExist:
            return redirect('StreamifyApp:profile-list')

method_decorator(login_required, name='dispatch')
class PlayMovie(View):
    def get(self, request, movie_id,  *args, **kwargs):
        try:
            movie =  Movie.objects.get(uuid = movie_id)
            movie =  movie.video.values()

            context = {
                'movie' : list(movie)
            }            
            return render(request, 'playmovie.html', context)
        except Movie.DoesNotExist:
            return redirect('StreamifyApp:profile-list')

class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect('/')

method_decorator(login_required, name='dispatch')
class Subscribe(View):
    def get(self, request, *args, **kwargs):
        form = SubscriptionForm()
        context = {'form': form}
        return render(request, 'subscribe.html', context)

    def post(self, request, *args, **kwargs):
        form = SubscriptionForm(request.POST)
        if form.is_valid():
            selected_plan = request.POST.get('plan')

            # Validate the selected plan
            if selected_plan not in ['BASIC', 'STANDARD', 'PREMIUM']:
                raise ValueError('Invalid subscription plan')

            # Calculate the amount based on the selected plan
            if selected_plan == 'BASIC':
                amount = 10000  # 1 Month Subscription
            elif selected_plan == 'STANDARD':
                amount = 60000  # 6 Months Subscription
            elif selected_plan == 'PREMIUM':
                amount = 120000  # 12 Months Subscription
            else:
                raise ValueError('Invalid subscription plan')

            
            subscription = form.save(commit=False)
            subscription.user = request.user
            subscription.save()

            # Save the amount to the subscription object
            subscription.amount = amount
            subscription.save()

            # Create a Razorpay order
            razorpay_client = razorpay.Client(auth=RAZORPAY_KEY_ID, key=RAZORPAY_KEY_SECRET)

            order_data = {
                "amount": subscription.amount,
                "currency": "INR",
                "receipt": "receipt_123456",
                "payment_capture": True,
            }

            new_order = razorpay_client.orders.create(order_data)

            # Save the order ID in the subscription object
            subscription.order_id = new_order['id']
            subscription.save()

            # Redirect to Razorpay payment page
            payment_gateway_url = new_order['url']
            return redirect(payment_gateway_url)

        context = {'form': form, 'amount': amount}
        return render(request, 'subscribe.html', context)

method_decorator(login_required, name='dispatch')
class PaymentSuccess(View):
  def get(self, request, *args, **kwargs):
    # Get the order ID and subscription ID from the request
    order_id = request.GET.get('order_id')
    subscription_id = request.GET.get('subscription_id')

    # Try to get the subscription object associated with the subscription ID
    try:
        subscription = Subscription.objects.get(pk=subscription_id)
    except Subscription.DoesNotExist:
        # If the subscription object doesn't exist, create a new one
        subscription = Subscription.objects.create(user=request.user, subscription_type='BASIC')

    # Check if the subscription object matches the order ID
    if subscription.order_id != order_id:
        # If the order ID doesn't match, raise an error
        raise ValueError('Invalid subscription ID or order ID')

    # Update the subscription object with the order ID
    subscription.order_id = order_id

    # Set the `is_active` flag to `True`
    subscription.is_active = True

    # Update the `end_date` field
    subscription.end_date = subscription.get_subscription_end_date()

    # Save the subscription object again
    subscription.save()

    return render(request, 'paymentsuccess.html')

