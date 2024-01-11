"""

File to show the allowed custom arguments and create a class for a dictionary so we can
still use typing for those custom arguments.

"""


from typing import TypedDict, Optional

class MeasurementArguments(TypedDict, total=False):
    page_location: Optional[str]
    skip_stage: Optional[list]
    stage: Optional[str]
    logging_level: Optional[str]
    page_title: Optional[str]
    event_name: Optional[str]
    testing_mode: Optional[bool]

# Example usage
my_dict: MeasurementArguments = {
    'page_location': "my_page",
    'skip_stage': ['end'],
    "logging_level": "all",
    "testing_mode": True
}

