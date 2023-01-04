
# commission number class, self validating
class CommissionNumber:

    def __init__(self, number: str):
        self.number = number.upper()
        self.validate()
        

    def validate(self):
        v = CommissionNumber.validate_condition
        v(len(self.number) == 6)
        v(self.number[:2].isalpha())
        v(self.number[2:].isnumeric())


    @staticmethod
    def validate_condition(cond: bool):
        if not cond:
            raise CommissionNumber.CommissionNumberError('malformed commission number')


    class CommissionNumberError(BaseException):
        pass

# class end