class UnimplementedError(Exception):
    """Exception raised for unimplemented method call."""

    def __init__(self):
        super().__init__('Unimplemented code!')
