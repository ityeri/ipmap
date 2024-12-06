import pygame

from blackboard.main import *
from blackboard.main import camera

from thread_thread import Thread
from iptools import *
from ip_scanner import IPscanner


class ThreadMonitor(shape):
    def __init__(self, thread: Thread, threadNum: int, pos: tuple[int, int], 
                 mainColor: tuple[int, int, int], 
                 progressColor: tuple[int, int, int],
                 gridColor: tuple[int, int, int],
                 size: tuple[float, float] = (1, 1)) -> None:
        
        self.thread: Thread = thread
        self.threadNum: int = threadNum

        self.unitPos: tuple[int, int] = pos
        self.actualPos: tuple[float,  float] = (
            pos[0] * size[0], pos[1] * size[1]
        )

        self.mainColor: tuple[int, int, int] = mainColor
        self.progressColor: tuple[int, int, int] = progressColor
        self.gridColor: tuple[int, int, int] = gridColor

        self.size: tuple[float, float] = size


    def draw(self, surface: pygame.Surface, viewCamera: camera) -> None:

        try: progress = self.thread.getProgress()[0]
        except: progress = 0

        mainColor  = (
            self.mainColor[0] * progress,
            self.mainColor[1] * progress,
            self.mainColor[2] * progress
        )

        screenPos = boardToScreen(self.actualPos[0], self.actualPos[1], viewCamera)
        
        rectWidth = self.size[0] * viewCamera.zoom * viewCamera.surfaceRadius +1
        rectHeight = self.size[1] * viewCamera.zoom * viewCamera.surfaceRadius +1

        rect = (
            *screenPos, rectWidth, rectHeight
        )

        pygame.draw.rect(surface, mainColor , rect)

        displayProgress = int(progress * rectWidth)

        # 원래 선 그리는건데 속도를 위해 사각형으로
        pygame.draw.rect(surface, self.progressColor, 
                         (*screenPos, displayProgress, rectHeight*0.2))

        pygame.draw.rect(surface, self.gridColor, rect, 1)


class IPscannerMonitor(blackboard):
    def __init__(self, 
                 surface: pygame.Surface, 
                 nuclear: IPscanner,
                 zoomInterval: float = 1.1, 
                 zoomBlending: float = 100, 
                 direction: str = 'ru') -> None:
        
        super().__init__(surface, zoomInterval, zoomBlending, direction)

        self.nuclear: IPscanner = nuclear
        # self.font: pygame.Font = pygame.font.Font('mainFont.ttf', 200)
        
        width = int(self.nuclear.threadCount ** 0.5)
        x = 0
        y = 0

        mainColor = (0, 255, 0)
        progressColor = (0, 255, 255)
        gridColor = (127, 127, 127)

        for i, thread in enumerate(self.nuclear.threads):
            self.addShape(
                ThreadMonitor(
                    thread= thread,
                    threadNum= i,
                    pos= (x, y),
                    mainColor= mainColor,
                    progressColor= progressColor,
                    gridColor= gridColor
                )
            )

            x += 1
            if x >= width:
                x = 0
                y -= 1