import unittest
import requests
import gapy.error_handling as error_handling

class TestError(unittest.TestCase):
    
    def test_verbose_error(self):
        # Define dummy function that creates an error that creates a message
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



