# ga4-py
A library which sends tracking pings to GA4 so we can track tool usage.

This is mainy for teams who are producing Python based tools, particularly for internal teams, and want a quick way to be able to add usage/error tracking to those tools without lots of setup of the package, and without having to make changes to deeper code.

This can be implemented almost completely by setting some environment variables and adding a single decorator to your topmost function.

This library is designed with an aggressive focus on *not* taking down existing code with errors. Any tracking errors *can* be sent to a chosen API
endpoint but they will not raise errors in your main code. This is a design choice which could mean you miss times when tracking isn't working (but 
that's what the error API address field is for).

Tracking Based on [gtagmp](https://github.com/adswerve/GA4-Measurement-Protocol-Python)

## Steps:
1. Add tracking_decorator as a decorator to the function you want to track 
    Recommendation is add the decorator to your highest-level function so you
    catch all the starts, ends, and errors, but don't flood your analytics with messages.
    This will also allow you to use a custom exception to send an error message to 
    analytics without it potentially causing unforeseen error handling problems further down.
2. Add a GA client secret to your env variables with the name GA4_CLI_SEC [see GTAGMP for more details](https://github.com/adswerve/GA4-Measurement-Protocol-Python)
3. Add a measurement_id to your env variables with the name GA4_MID [see GTAGMP for more details](https://github.com/adswerve/GA4-Measurement-Protocol-Python)
4. Run your code

### When you've added this decorator, your function will:
- Send a tracking ping when your function starts
- Send a tracking ping if/when your function successfully completes
- Send a tracking ping if/when your function fails
    (Then it will raise the error directly to avoid interfering with your debugging)

## Recommended:
- As a bare minimum, the decorator will include a "stage" parameter in the GA4 hit to
    show whether it is recording a hit for the start, or end of your code running, or
    if it's recording an error. It's recommended that you add stage as a known parameter
    in GA4. For [more information check the GA4 documentation.](https://developers.google.com/analytics/devguides/collection/ga4/event-parameters)

## Optional:
- If you want to send additional information as part of your tracking hit (i.e. tool name etc.)
    then add a *named argument* to the function you are tracking when you call it.
    You can add the arguments in two ways
    - If you use the name ga4py_args_remove the decorator will use the dictionary and then remove
        it before your function is called so you don't have to change how your function works to 
        add the optional parameters.
    - If you use the name ga4py_args the decorator will use the dictioanry but *not* remove it from
        your function arguments before calling your function

- If you want to be alerted if your tracking function fails for some reason (because it deliberately won't cause the main code to fail). Include the GA4_ERROR_API_ENDPOINT environment variable. The decorator will automatically send a POST request to that url using the requests library. The message will include JSON with a summary of the issue and more detail. You could use that endpoint to send an alert to your chosen monitoring address.

- If you want certain error messages to be sent to GA when we record errors, update your function so that it raises an ga4py.error_class.AnalyticsException (class defined in this library) the analytics_message you specify in that error will be passed to your analytics hit as the "error_message" parameter.

- If you want to mark a hit as a "testing" hit (recommended so you can separate actual 
user traffic from your team testing the script) you can set an env variable with the name GA4_ANALYTICS_TEST and the value of "TRUE". The decorator will automatically pick that up
and include it in tracking hits. 

- You can pass whatever custom parameters you want to the function but if you want to use type checking and are only using the basic expected arguments you can use the class in ga4py/custom_arguments

### Parameters you could include in your arguments

The below are some suggested paramters you could include in your
analytics hits. Some of these parameters are already pre-defined in 
GA4 and will appear automatically in your reports when they are sent.

Other parameters are *not* default GA4 parameters and you may have to add them.
For [more information check the GA4 documentation.](https://developers.google.com/analytics/devguides/collection/ga4/event-parameters)

```{
"page_location" (string): this will automatically be separated out and sent to GA4, if you *don't* set this the hit will still fire but the script will silently send an error to your chosen API to alert you that your tracking isn't categorising things.

"skip_stage" (list): normally the decorator will automatically send one tracking hit with a stage of "start" before your function runs, one with the stage of "end" when your function completes, and one with the stage of "error". If you include a "skip_stage" item in this dictionary then the decorator will automatically skip sending that stage of hit. This is useful if, for example, you have function that runs repeatedly (say a Streamlit app) and you only want to trigger the start function once when it loads and the end function once when it completes. To skip the start stage include {skip_stage: ["start"]} 

"stage" (string): normally the decorator will automatically send a "start" stage hit at the start, and "end" stage hit at the end. If you want to send a *different* stage value with the tracking hit you can pass a stage parameter. This will mean that a tracking hit is *only* sent before your function runs, and instead of having "start" as the stage the stage name will be whatever you pass. I.e. {stage: "upload"} will send a tracking hit before your function runs with the stage value of "upload"

"logging_level" (string): normally the decorator won't automatically print out descriptions of what it is doing and why. If you want it to print out the reasons for errors then pass {logging_level: "error"} if you want it to log all updates then pass {logging_level: "all"}


"page_title" (string): the name of the page title that should show up in GA4, if not set it'll just be the page location but with any underscores or hyphens replaced with a space

"event_name" (string): the name of the event in GA4, if not set this will default to "pageview"

"testing_mode" (bool): a flag which will tell the code *not* to send a hit to GA4 but instead print out the details

Any other parameters you choose to include!
}
```


## Examples

For example usage, look in /tests.

