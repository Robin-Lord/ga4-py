"""
Functions for custom error handling, including a decorator that lets our send_hit function
fail gracefully without taking down main code, and a custom AnalyticsException class which 
users can use to pass a custom analytics message to GA4.
"""


import os
import requests #type: ignore
from typing import AnyStr, List, Tuple, Dict
import json

class AnalyticsException(Exception):
    def __init__(self, message, analytics_message):
        super().__init__(message)
        self.analytics_message = analytics_message


def handle_analytics_errors(func):
    """
    Decorator to make sure that our analytics hits don't break the script.

    While it's important that we record usage data - that's not the MOST
    important thing - we don't want to derail usage of the script just
    because this isn't working


    parameters:
        - func (function with arguments)

    """

    def ret_fun(*args, **kwargs):
        """
        Function which does error handling (module checks and in-measurement errors)
        then runs the measurement function we want to run.

        It tries to extract the name of the function that called this one so
        we can debug but if that doesn't work it sends the error anyway just
        in case.


        parameters:
        - *args (passed to function and error logging)
        - **kwargs (passed to function and error logging)
        """

        # Get logging level
        logging_level = kwargs.get("logging_level", "any")

        # First see if we can extract the calling function
        try:
            import inspect # Build in, should be present

            # Get the name of the function that called this one
            calling_function = inspect.stack()[1].function
        except:
            # If that fails then just say we couldn't extract
            calling_function = (
                "[error occurred in a calling function we couldn't get the name of]"
            )

        # First check that modules are installed
        try:
            from ga4mp import GtagMP # type: ignore
            from ga4mp.store import DictStore # type: ignore

        except Exception as E:
            # If we get an error then the modules aren't installed
            send_tracking_error_alert(
                error=E, 
                function=calling_function, 
                parameters=[args, kwargs],
                logging_level=logging_level)

            # If the modules aren't installed then running the function
            # will throw an error (which will error more crucial code)
            # so instead we just run an error print function
            # that can handle whatever and return

            if logging_level in ["error", "any"]:
                error = "Modules not installed"
                print_error_function(error)
            return

        # If the modules ARE installed - try running our passed function
        try:
            returned_value = func(*args, **kwargs)
            return returned_value

        except Exception as e:
            # If we hit an error we don't want it to derail our core code

            if logging_level in ["error", "any"]:
                print_error_function(e)

            send_tracking_error_alert(
                error=e, 
                function=calling_function, 
                parameters=[args, kwargs],
                logging_level=logging_level)

    return ret_fun





def send_tracking_error_alert(
        error: AnyStr, 
        function: AnyStr, 
        parameters: List[Dict],
        logging_level: str = "any"
        )->requests.Response: 
    """
    
    A function to send errors to our tool monitoring API when our tracking
    fails. (Importantly, this does not hit the error API when the main code
    fails, it's just a way to know if the measurement tracking is hitting issues).

    Parameters:

    - error (string): What has caused the problem
    - function (string): The function that was not tracked successfully
    - parameters (list of dicts): The parameters we tried to send to GA4
    - logging_level (str - optional): [default = "any"] how much we should print

    Returns:
    - response (requests.Response object)

    """

    # Retrieve the API endpoint to send the error message to
    api_endpoint = os.getenv("GA4_ERROR_API_ENDPOINT", "")

    if api_endpoint == "":
        # If the endpoint url isn't set, just return
        if logging_level in ["error", "any"]:
            print("No analytics error endpoint set - skipping")
        return


    # Construct subject line and body (body can use html markup)
    subject = f"Error in tracking function: {function!r} "

    param="<br>" + "<br>".join([str(param) for param in parameters])

    body = f"""
  
  Error: {error!r}
  <br><br><hr> <br><br>
  Function parameters: {param!r}
  
  """
    

    # Construct json to send
    data = {"subject": subject, "body": body}

    data_json = json.dumps(data)

    # Send json to endpoint
    r = requests.post(api_endpoint, data=data_json)

    return r


def print_error_function(
        error: AnyStr):
    """Function to tell user why analytics isn't running
    Likely won't care!


    parameters:
    - error (string)

    returns:
    - None
    """
    print(f"Skipping analytics: {error!r}")

    return