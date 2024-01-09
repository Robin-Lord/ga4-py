import unittest
import requests
import gapy.add_tracker as add_tracker
import gapy.error_handling as error_handling

@add_tracker.analytics_hit_decorator
def simple_function_to_track():
    """
    simple_function_to_track 
    
    A simple function which we've added the tracking decorator to.

    Note we haven't had to add *any* special arguments to this function.
    """

    print("Running simple function")

@add_tracker.analytics_hit_decorator
def simple_function_to_show_custom_error():
    """
    simple_function_to_track 
    
    A simple function which we've added the tracking decorator to.

    Note we haven't had to add *any* special arguments to this function.

    But we have defined a custom error which will automatically include a
    message in our analytics hit.
    """
    
    raise error_handling.AnalyticsException("Error message", "Special analytics message for tracker")


class TestTracking(unittest.TestCase):
    
    def test_tracking_function(self):

        tracking_args_dict = {
            "testing_mode": True, # Make sure to either remove this, or to set this to False when you want to actually send hits
            "page_location": "any_location_you_want", 
            "page_location": "any title you want", 
            "page_location": "any title you want", 
        }


        simple_function_to_track(ga4py_args_remove = tracking_args_dict)
    
    def test_tracking_function_with_error(self):

        tracking_args_dict = {
            "testing_mode": True, # Make sure to either remove this, or to set this to False when you want to actually send hits
            "page_location": "any_location_you_want", 
            "page_location": "any title you want", 
            "page_location": "any title you want", 
        }

        # The function will raise an error, but first the tracking library will record that error
        simple_function_to_show_custom_error(ga4py_args_remove = tracking_args_dict)
        self.assertRaises(error_handling.AnalyticsException)
        
        
