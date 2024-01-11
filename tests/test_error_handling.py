import unittest
import requests #type: ignore
import ga4py.error_handling as error_handling
import ga4py.add_tracker as add_tracker
from ga4py.custom_arguments import MeasurementArguments

class TestError(unittest.TestCase):
    
    def test_verbose_error(self):
        """
        test_verbose_error 

        Test dummy function which uses the custom AnalyticsException error class
        to pass a custom error message to our Analytics
        """
        def my_function():
            if True:
                raise error_handling.AnalyticsException("Error occurred", "Custom analytics message")    

        error_success = False    
        try:
            my_function()

        except error_handling.AnalyticsException as e:
            self.assertEqual(e.analytics_message, "Custom analytics message")
            print(f"Analytics error message: {e.analytics_message}")
            error_success = True

        self.assertTrue(error_success)        
    def test_standard_error_handling(self):

        # Deliberately not setting page location to force error
        tracking_args_dict: MeasurementArguments = {
            "testing_mode": True, # Make sure to either remove this, or to set this to False when you want to actually send hits
            "logging_level": "all"
        }

        @add_tracker.analytics_hit_decorator
        def simple_function_to_show_error():
            print("Running simple function")


        # The function will raise an error, but first the tracking library will record that error
        simple_function_to_show_error(ga4py_args_remove = tracking_args_dict)



