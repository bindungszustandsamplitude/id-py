# utility class
class Util:

    # useful for value extractions
    @staticmethod
    def sandwich(text: str, before: str, after: str):
        return text.split(before)[1].split(after)[0]

# class end