import pygame
from ip_scanner import IPscanner
from monitor import IPscannerMonitor



# 파이게임 설정
pygame.init()

screen = pygame.display.set_mode((500, 500), pygame.RESIZABLE)
clk = pygame.Clock()
fps = 60
dt = 10
on = True

# 기본 설정
threadCount = 24
ipPerThread = 64

divisionUnit = 256^3 # 파일 하나당 주소 몇게 저장할지를 설정
resultPath = 'result'

# 헥톡ㅌ탄 설정
ipScanner = IPscanner(0, 0x0_0001_0000, threadCount, ipPerThread)
ipScannerMonitor = IPscannerMonitor(screen, ipScanner)


while on:
    dt = clk.tick(fps)
    ipScanner.update()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            on = False

            ipScanner.stopAllThread()

            isExit = input("결과를 저장하시겠습니까? (Y/n) :")
            if isExit == 'Y' or isExit == 'y':
                ipScanner.saveResult(resultPath, divisionUnit)

        ipScannerMonitor.event(event)
    
    ipScannerMonitor.update(dt)

    if ipScanner.isDone: on = False

    ipScannerMonitor.draw()

    pygame.display.flip()

pygame.quit()

ipScanner.saveResult('result', 256^2)