class Progress:
    def __init__(self, maxCount: int) -> None:
        self.count: int = 0
        self.maxCount: int = maxCount
    
    @property
    def countRatio(self) -> float:
        return self.count / self.maxCount
    
    @property
    def isDone(self) -> bool:
        return self.count == self.maxCount