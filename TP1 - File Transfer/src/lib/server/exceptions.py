class ServerParamsFailException(Exception):
    def __str__(self):
        return "Error: some param/s was not included."
    pass
