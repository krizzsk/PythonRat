def banner():
    return (Colour.green("""                                   
  _____       _   _                   _____         _______ 
 |  __ \     | | | |                 |  __ \     /\|__   __|
 | |__) |   _| |_| |__   ___  _ __   | |__) |   /  \  | |   
 |  ___/ | | | __| '_ \ / _ \| '_ \  |  _  /   / /\ \ | |   
 | |   | |_| | |_| | | | (_) | | | | | | \ \  / ____ \| |   
 |_|    \__, |\__|_| |_|\___/|_| |_| |_|  \_\/_/    \_\_|   
         __/ |                                              
        |___/                                                                           
    """) + "(" +
            Colour.blue("v1.0.0") + ")" +
            "\n")


class Colour():
    @staticmethod
    def red(str):
        return "\033[91m" + str + "\033[0m"

    @staticmethod
    def green(str):
        return "\033[92m" + str + "\033[0m"

    @staticmethod
    def yellow(str):
        return "\033[93m" + str + "\033[0m"

    @staticmethod
    def blue(str):
        return "\033[94m" + str + "\033[0m"
