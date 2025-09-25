from django.shortcuts import render, redirect
from django.views import View
from django.http import HttpResponse,HttpResponseBadRequest
from django.db.models import Q
from .models import Airport, Route
from .forms import AirportForm, AirportRouteForm


class HomeView(View):
    # This method handles GET requests to the view.
    # Its purpose is to display the initial page with an empty form and a list of existing airports.
    def get(self, request):
        airports = Airport.objects.all()  # Fetches all existing Airport objects from the database.
        airpotform = AirportForm()  # Creates a new, empty instance of the AirportForm.
        return render(request, 'AddAirport.html', {'airports': airports, 'airpotform': airpotform})
    
    # This method handles POST requests, which occur when the user submits the form.
    def post(self, request):
        airpotform = AirportForm(request.POST)  # Binds the submitted form data to the AirportForm.
        
        # is_valid() checks if the form data is correct and meets validation rules (e.g., required fields).
        if airpotform.is_valid():
            # commit=False tells Django not to save the object to the database yet.
            # This is done to allow manual modification of the object before saving.
            airpotform.save(commit=False)
            
            # Retrieves 'code' and 'name' from the submitted POST data.
            # Converts the retrieved values to uppercase for case-insensitive checking.
            air, name = request.POST.get('code'), request.POST.get('name') 
            airf, namf = air.upper(), name.upper()
            
            # This line checks if an airport with the same name OR code already exists in the database.
            # Q objects allow for complex lookups (like OR conditions) within a query.
            # The .exists() method is an efficient way to check for the existence of an object without retrieving it.
            if Airport.objects.filter(Q(name=namf) | Q(code=airf)).exists():
                return HttpResponse("Airport code already exists")  # If a match is found, returns an error message.
            else:
                # If no existing airport matches, a new one is created with the uppercase values.
                Airport.objects.create(code=airf, name=namf)
                
                # Redirects the user to the 'home' URL, triggering a new GET request.
                # This refreshes the page and displays the newly added airport in the table.
                return redirect('home')
        else:
            # If the form data is invalid, this block is executed.
            airports = Airport.objects.all()  # Fetches the list of airports again to display the table.
            
            # Rerenders the same page, but this time, the form object 'airpotform' contains the validation errors,
            # which will be displayed to the user by Django's template rendering.
            return render(request, 'AddAirport.html', {'airports': airports, 'airpotform': airpotform})
        
class RoutView(View):
    # The 'get' method handles GET requests to display the form and existing routes.
    def get(self, request):
        # Create an instance of the form to be rendered on the page.
        airportrouteform = AirportRouteForm()
        # Retrieve all existing route objects from the database.
        routes = Route.objects.all().order_by('direction')
        # Render the 'AddAirportRoute.html' template, passing the form and routes to the context.
        return render(request, 'AddAirportRoute.html', {'airportrouteform': airportrouteform, 'routes': routes})
    
    # The 'post' method handles POST requests when the form is submitted.
    def post(self, request):
        # Create a form instance and populate it with data from the POST request.
        airportrouteform = AirportRouteForm(request.POST)
        
        # Check if the 'start_airport' and 'end_airport' fields have the same value.
        if request.POST.get('start_airport') == request.POST.get('end_airport'):
            # If they are the same, return an HTTP response with an error message.
            return HttpResponse("Start and end airports cannot be the same.")
        else:
            # If the airports are different, proceed with form validation.
            if airportrouteform.is_valid():
                # If the form data is valid, save it to the database.
                airportrouteform.save()
                # Redirect the user to the 'route' URL to prevent form resubmission on page refresh.
                return redirect('route')
            else:
                # If the form data is not valid, re-render the page with the form and its errors.
                # Retrieve the routes again to pass them to the template context.
                routes = Route.objects.all().order_by('direction')
                # Render the template again, passing the form with errors and the list of routes.
                return render(request, 'AddAirportRoute.html', {'airportrouteform': airportrouteform, 'routes': routes})

from django.shortcuts import render
from django.views import View
from django.http import HttpResponseBadRequest, HttpResponse
from .models import Route, Airport

class Nhroute(View):
    # This method handles GET requests to display the initial form.
    def get(self, request):
        # Get a distinct list of airport IDs that are used as a starting point in any route.
        start_airport_ids = Route.objects.values_list('start_airport', flat=True).distinct()
        
        # Fetch the Airport objects corresponding to these IDs.
        Airp = Airport.objects.filter(id__in=start_airport_ids)
        
        # Render the 'nthnode.html' template, passing the list of starting airports to the template.
        return render(request, 'nthnode.html', {'Airp': Airp})

    # This method handles POST requests when the user submits the form to find the Nth node.
    def post(self, request):
        # Retrieve the selected starting airport ID, the number of nodes to traverse (n_value), and the direction (left/right) from the form data.
        start_airport_id = request.POST.get('start_airport')
        n_value_str = request.POST.get('n_value')
        direction = request.POST.get('direction')
        
        # Validate that all required form data is present.
        if not start_airport_id or not n_value_str or not direction:
            return HttpResponseBadRequest("Invalid form data.")

        try:
            # Convert n_value to an integer and retrieve the starting Airport object.
            n_value = int(n_value_str)
            current_airport = Airport.objects.get(id=start_airport_id)
        except (ValueError, Airport.DoesNotExist):
            # Handle cases where n_value is not a valid number or the start airport does not exist.
            return HttpResponse("Invalid start airport or n-value.")
        
        # Initialize a list to store the path of the route.
        route_path = [current_airport]
        
        # Loop 'n_value' times to find each subsequent node.
        for i in range(n_value):
            try:
                # Find the next route from the current airport in the specified direction.
                next_route = Route.objects.filter(start_airport=current_airport, direction=direction).first()
                if next_route is None:
                    # If no route is found, handle the error gracefully.
                    # Re-fetch the list of starting airports for the template.
                    Airp = Airport.objects.filter(id__in=Route.objects.values_list('start_airport', flat=True).distinct())

                    # Create an error message and render the template with the partial path and the error.
                    error_msg = f"Search halted. Route could not be found after {i} nodes."
                    return render(request, 'nthnode.html', {
                        'err': error_msg,
                        'routsi': {f'Node {j}': ap for j, ap in enumerate(route_path)},
                        'Airp': Airp
                    })
                
                # Update the current airport to be the end airport of the found route.
                current_airport = next_route.end_airport
                
                # Append the new airport to the route path list.
                route_path.append(current_airport)
            except Route.DoesNotExist:
                # If a route is not found at any step, handle the error gracefully.
                # Re-fetch the list of starting airports for the template.
                Airp = Airport.objects.filter(id__in=Route.objects.values_list('start_airport', flat=True).distinct())
                
                # Create an error message and render the template with the partial path and the error.
                error_msg = f"Search halted. Route could not be found after {i} nodes."
                return render(request, 'nthnode.html', {
                    'err': error_msg,
                    'routsi': {f'Node {j}': ap for j, ap in enumerate(route_path)},
                    'Airp': Airp
                })
        
        # Get the final airport from the completed route path.
        final_node = route_path[-1]
        
        # Re-fetch the list of starting airports for the template, as in the get() method.
        Airp = Airport.objects.filter(id__in=Route.objects.values_list('start_airport', flat=True).distinct())
        
        # Convert the route path list into a dictionary for easier display in the template.
        routsi_dict = {f'Node {i}': ap for i, ap in enumerate(route_path)}

        # Render the template with the final airport, the full route path, and the list of starting airports.
        return render(request, 'nthnode.html', {
            'fin': final_node,
            'routsi': routsi_dict,
            'Airp': Airp
        })



def longest_route_view(request):
    # Find the single Route object with the maximum duration_minutes
    longest_route = Route.objects.order_by('-duration_minutes').first()

    # Create a context dictionary to pass the data to the template
    context = {
        'longest_route': longest_route
    }

    # Render the template, passing the context
    return render(request, 'LongestRoute.html', context)



class DistanceBtwnAiports(View):

    def get(self, request):
        """
        Handles GET requests to display the form for selecting two airports.
        """
        # Fetch all airports from the database to populate the dropdown menus.
        airports = Airport.objects.all()

        # Render the template with the list of airports.
        return render(request, 'DistanceBtwnAiports.html', {'airports': airports})

    def post(self, request):
        """
        Handles POST requests to find the shortest route between two selected airports.
        """
        # Get the IDs of the selected start and end airports from the form.
        start_airport_id = request.POST.get('start_airport')
        end_airport_id = request.POST.get('end_airport')
        airports = Airport.objects.all()


        # Validate that both airport IDs are present.
        if start_airport_id==None or end_airport_id==None or start_airport_id==end_airport_id:
            return HttpResponse("Please select both a start and an end airport.")
        
        if Route.objects.filter(start_airport = start_airport_id, end_airport = end_airport_id).exists():
                return HttpResponse("A route from this airport to itself already exists.")

        try:
            routes = Route.objects.filter(Q(start_airport=start_airport_id) | Q(end_airport=end_airport_id))
            starting = routes.first().start_airport
            nextrout = routes.first().end_airport
            dist = routes.first().distance_km
            duration = routes.first().duration_minutes
            shotrest = []
            fr =True
            while fr:

                if nextrout == end_airport_id:
                    fr = False
                    return render(request, 'DistanceBtwnAiports.html', {'shotrest':shotrest, 'airports': airports})
                else:
                    starting = nextrout
                    nextrout = routes.first().end_airport
                    dist = routes.first().distance_km
                    duration = routes.first().duration_minutes
                    shotrest.append({"starting":starting, "nextrout":nextrout, "dist":dist, "duration":duration})
        except:
            return HttpResponse("No route found between the selected airports.")
        print(shotrest)
        return render(request, 'DistanceBtwnAiports.html', {'airports': airports, 'start_airport_id': start_airport_id, 'end_airport_id': end_airport_id})

