class RemagicException(ValueError):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    # ENHANCE: Expand this later
