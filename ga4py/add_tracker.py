import os
from functools import wraps # Properly show docstrings for decorated functions
import ga4py.error_handling as error_handling 
from typing import Tuple, List, Dict, AnyStr

try:
    from ga4mp import GtagMP
except Exception as e:
    print("Failed to import ga4mp - tracking will likely fail")


def analytics_hit_decorator(func):
    """
    Decorator to add tracking to a function.

    When added to a function, will add a traking ping when the function 
    starts, and one when it ends. 

    function parameters:
        - ga4py_args_remove (dictionary - optional): [default None] arguments to
                                                pass to GA4, this parameter will
                                                be removed before calling the 
                                                decorated function. For some examples
                                                or options you could include in your
                                                dictionary, look at the readme file for this library.

        - ga4py_args (dictionary - optional): [default None] arguments to
                                                pass to GA4, this parameter will
                                                *not* be removed before calling
                                                the decorated function. For some examples
                                                or options you could include in your
                                                dictionary, look at the readme file for this library.


    

    environment parameters to set:
        - GA4_CLI_SEC (environment variable): GA4 API client secret, see here for more: https://github.com/adswerve/GA4-Measurement-Protocol-Python

        - GA4_MID (environment variable): GA4 measurement id, see here for more: https://github.com/adswerve/GA4-Measurement-Protocol-Python

        - GA4_ERROR_API_ENDPOINT (environment variable - optional): A url to send an error message to if the analytics fails 
                                                                    (if you don't set this env variable leave blank then the analytics will just 
                                                                    fail silently to avoid disrupting the crucial thread)

        - GA4_ANALYTICS_TEST (environment variable - optional): A flag for if you are testing the code, this won't stop analytics hits from being
                                                                    sent, but will automatically include a parameter in the GA4  hit so you can 
                                                                    filter out testing events (the parameter name will be "testing" and the value will be
                                                                    "TRUE")
    """

    @wraps(func) # Make sure docstring comes through properly
    def wrapper(*args, **kwargs):

        arg_params = {}

        if kwargs != None:
            # If user has included ga4py_args_remove then add to our arg
            # dict while removing from the arguments passed
            arg_params.update(kwargs.pop("ga4py_args_remove", {}))

            # Add other parameters but don't remove them from what is
            # being passed to the function
            arg_params.update(kwargs.get("ga4py_args", {}))

        # Check if this is a testing hit
        testing_flag = os.getenv("GA4_ANALYTICS_TEST", "FALSE")
        if testing_flag == "TRUE":
            arg_params["testing"] = testing_flag

        
        # Pull out key information from the dictionary
        page_title = arg_params.pop("page_title", "")
        page_location = arg_params.pop("page_location", None)
        event_name = arg_params.pop("event_name", "pageview")
        testing_mode = arg_params.pop("testing_mode", False)

        try:
            # Send "starting function" hit
            send_hit(
                parameter_dictionary = arg_params,
                page_title = page_title,
                page_location = page_location,
                event_name = event_name,
                stage = "start",
                gtag_tracker = None,
                testing_mode = testing_mode,
            )

            
            # Run function as normal
            returned_value = func(*args, **kwargs)

            # Send success hit now that function is done
            send_hit(
                parameter_dictionary = arg_params,
                page_title = page_title,
                page_location = page_location,
                event_name = event_name,
                stage = "end",
                gtag_tracker = None,
                testing_mode = testing_mode,
            )

            return returned_value
        
        except error_handling.AnalyticsException as e:
            # If function hits an error and user has defined a specific message
            # to send to analytics, use that
            arg_params["error_message"] = e.analytics_message
            send_hit(
                parameter_dictionary = arg_params,
                page_title = page_title,
                page_location = page_location,
                event_name = event_name,
                stage = "error",
                gtag_tracker = None,
                testing_mode = testing_mode,
            )

        
        except Exception as e:
            # Send standard error hit with no specialised message to include
            send_hit(
                parameter_dictionary = arg_params,
                page_title = page_title,
                page_location = page_location,
                event_name = event_name,
                stage = "error",
                gtag_tracker = None,
                testing_mode = testing_mode,
            )


            # If there's an error we still raise it, we
            # just send an error message to our tracking first
            raise e
    

    return wrapper






def initialise_tracking() -> GtagMP:
    """
    Function to create the tracker we'll continuously use to record activity

    This is called by send_hit()

    Parameters: None

    Returns:
    - gtag_tracker (tracker object)


    """

    storage_dict = {}

    # Get client secret and measurement id from environment variables
    api_secret = os.getenv("GA4_CLI_SEC")
    measurement_id = os.getenv("GA4_MID")

    # Create an instance of GA4 object using gtag
    gtag_tracker = GtagMP(
        api_secret = api_secret,
        client_id = "initial",
        measurement_id = measurement_id,
    )

    # Create a random client id
    # (for now - may come up with a better use for users in future)
    client_id = gtag_tracker.random_client_id()

    # Overwrite initialising client ID
    gtag_tracker.client_id = client_id

    return gtag_tracker

@error_handling.handle_analytics_errors
def send_hit(
    parameter_dictionary,
    page_title=None,
    page_location=None,
    event_name="pageview",
    stage="unknown",
    gtag_tracker=None,
    testing_mode=False,
):
    """
    Function to handle sending an analytics hit to GA4

    Parameters;

    - parameter_dictionary (dictionary -
    BE CAREFUL not to add a silly number to avoid flooding our analytics)

    - page_title (string - optional): [default = None] the page title to show in GA4

    - page_location (string - optional): [default = None] the page location to show in GA4

    - event_name (string - optional): [default = pageview] the event type to show in GA4

    - event_name (string - optional): [default = unknown] 
                                        used to categorise which point we're at in the script running)
                                        expected values are start, end, error but other values allowed

    - gtag_tracker (tracker object - optional): [default = None)
                                        object used to send hits to GA4

    """

    # Importing needed libraries should be handled by handle_errors 
    # decorator 

    #  Try to figure out the name of the function we're running
    function_name = ""
    try:
        import inspect

        function_name = inspect.stack()[2].function
    except:
        function_name = "unknown"

    # If the tracker hasn't been created before - create it
    if gtag_tracker == None:
        gtag_tracker = initialise_tracking()

    dict_to_send = {}

    # Check if we've added a silly number of parameters to the tracking hit
    if len(parameter_dictionary.keys()) > 10:
        # If we have - send an error
        error_handling.send_tracking_error_alert(
            "Too many parameters", function_name, parameter_dictionary
        )

        # And then just take a selection of parameters
        for key in parameter_dictionary.keys()[:10]:
            dict_to_send[key] = repr(parameter_dictionary[key])
            # Make sure is string so doesn't cause errors later

    else:
        dict_to_send = parameter_dictionary

    # Create a new event
    pageview_event = gtag_tracker.create_new_event(name=event_name)

    # Loop through all of our passed parameters and add them to our
    # pageview as analytics parameters (as long as they aren't really long)
    for key, value in parameter_dictionary.items():
        if len(repr(value)) > 30:
            value = repr(value)[:30]  # If it's more than 50 char then slice it down

        value = repr(value)

        pageview_event.set_event_param(name=key, value=value)

    # =======================
    # Handle page location and title

    # Check if we've got a page_title or location key set
    if page_location == None:
        error_handling.send_tracking_error_alert(
            "No page location set", function_name, parameter_dictionary
        )
        page_location = "unknown"

    if page_title == None:
        page_title = page_location.replace("_", " ").replace("-", " ")

    # Add default information which we know we want to include
    pageview_event.set_event_param(name="page_location", value=page_location)
    pageview_event.set_event_param(name="page_title", value=page_title)
    pageview_event.set_event_param(name="stage", value=stage)

    # End of handle page location and title
    # ^^^^^^^^^^^^^^^^^^^^^^^^

    if not testing_mode:
        # Then send the pageview event
        event_list = [pageview_event]  # It expects a list
        gtag_tracker.send(events=event_list)
    else:
        # If not testing mode then skip sending the hit but still
        # respond with what we were GOING to send so we can check
        print(f"""
              
Testing mode - no hit sent, tracking parameters:
              
param_dictionary: {parameter_dictionary}              
page_title: {page_title},
page_location: {page_location}
event_name: {event_name}
stage: {stage} 
              """)

    # Return the tracker
    return gtag_tracker
