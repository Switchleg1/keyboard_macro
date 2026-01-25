class SettingType():
    def __init__(self, default_value, print_string, indent=0):
        super().__init__()

        self.value          = default_value
        self.print_string   = print_string
        self.indent         = indent


    def print(self):
        print(" " * self.indent + f"{self.print_string}: {self.value}")


    def print_value(self, value):
        print(" " * self.indent + f"{self.print_string}: {value}")