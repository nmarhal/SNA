class CentralityScores:
    def __init__(
            self,
            in_degree: dict,
            out_degree: dict,
            eigenvector: dict,
            closeness: dict,
            betweenness: dict,
    ):
        self.in_degree = in_degree
        self.out_degree = out_degree
        self.eigenvector = eigenvector
        self.closeness = closeness
        self.betweenness = betweenness
