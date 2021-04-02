from termcolor import colored

class APITest:
    def __init__(self, endpoint, request_type, expected, params = None):
        self.endpoint = endpoint
        self.request_type = request_type
        self.params = params
        self.expected = expected


def run_api_test(test: APITest):
    pass

def assert_eq(got, expected):
    if got == expected:
        print(colored("PASSED", 'green'), ":", expected)
    else:
        print(colored("FAILED", 'red'), ": Expected:", expected, "\nReceived:", got)


def run_tests():

    print("Running API tests")