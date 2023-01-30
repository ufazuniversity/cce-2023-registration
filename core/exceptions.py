class OrderException(Exception):
    def __init__(self, message: str = "Order could not be processed."):
        self.message = message
        super().__init__(self.message)
