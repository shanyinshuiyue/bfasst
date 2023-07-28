"""Job class for a job function and dependency list"""

import uuid

from bfasst.tool import BfasstException


class Job:
    """Class for a job function and dependency list"""

    def __init__(self, function, design_rel_path, dependencies=None):
        """Holds a pointer to a tool's 'run' method,
        the relative path of the design to which the job belongs,
        a list of integer dependencies, generated by the uuid library,
        and the uuid in int form itself.
        """
        self.function = function
        self.design_rel_path = design_rel_path
        self.dependencies = dependencies
        self.__set_uuid()

    def __set_uuid(self):
        """Set the UUID for this job. The UUID is used to track dependencies
        between jobs and to identify jobs
        while eliminating concerns about pickling across processes in multiprocessing."""
        self.uuid = uuid.uuid4().int

    def invert(self):
        """This can be called in the case where we want to invert the job's exception handling"""
        return Job(self.inverter, self.design_rel_path, self.dependencies)

    def inverter(self):
        try:
            self.function()
        except BfasstException:
            return
        except AssertionError:
            return

        raise BfasstException(f"Job succeeded but was expected to fail")

    def __eq__(self, other):
        return self.uuid == other.uuid
