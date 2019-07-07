from time import gmtime, strftime


class Error:
    # Creates/writes to an error file when crucial files aren't found.
    @staticmethod
    def log(error):
        sys_time = strftime("%d/%m/%Y %H:%M:%S", gmtime())
        e = open("..\\error.txt", "w+")
        e.write("(%s) ERROR: %s" % (sys_time, error))
        e.close()
        exit(1)
