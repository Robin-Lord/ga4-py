import unittest
import requests
import ga4py.add_tracker as add_tracker
import ga4py.error_handling as error_handling
from ga4py.custom_arguments import MeasurementArguments

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
        print("Basic function tracking")
        tracking_args_dict: MeasurementArguments = {
            "testing_mode": True, # Make sure to either remove this, or to set this to False when you want to actually send hits
            "page_location": "any_location_you_want", 
            "page_title": "any title you want", 
            "logging_level": "all"
        }


        simple_function_to_track(ga4py_args_remove = tracking_args_dict)
    
    def test_tracking_function_with_error(self):
        print("Testing error handling")
        tracking_args_dict: MeasurementArguments = {
            "testing_mode": True, # Make sure to either remove this, or to set this to False when you want to actually send hits
            "page_location": "any_location_you_want", 
            "page_title": "any title you want", 
            "logging_level": "all"
        }

        # The function will raise an error, but first the tracking library will record that error
        with self.assertRaises(error_handling.AnalyticsException):
            simple_function_to_show_custom_error(ga4py_args_remove = tracking_args_dict)

        

    
    def test_skipping_stage(self):
        print("Testing stage skip and logging")
        tracking_args_dict: MeasurementArguments = {
            "testing_mode": True, # Make sure to either remove this, or to set this to False when you want to actually send hits
            "page_location": "any_location_you_want", 
            "page_title": "any title you want", 
            "skip_stage": ["start"],
            "logging_level": "all"
        }


        simple_function_to_track(ga4py_args_remove = tracking_args_dict)
        

        
        
