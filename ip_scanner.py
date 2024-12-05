import time
import json
import os

from progress import Progress
from thread import Thread, ThreadStatus, IpElement, IpStatus
from iptools import intToIP
from math import ceil



class IPscanner:
    def __init__(self, ipScope1: int, ipScope2: int,
                 threadCount: int, addPerThread: int,
                 data: dict[int, bool | None] | None=None) -> None:
        
        # self.ipStatus: dict[int, int] = dict.fromkeys(
        #     list(range(ipScope1, ipScope2)), ipStatus.WAIT)
        
        # self.ipResult: dict[int, bool | None] = dict.fromkeys(
        #     list(range(ipScope1, ipScope2)), None)
        
        self.ipAdds: dict[int, IpElement] = {ipAdd: IpElement(ipAdd) for ipAdd in range(ipScope1, ipScope2)}

        # 미리 입력된 데이터를 ipResult 에 적용
        if data != None:
            for ip, result in data.items():
                # 미리 입력받은 데이터의 ip 주소가 
                # 스캐너의 주소 범위에 포함되는 경우
                if ipScope1 <= ip < ipScope2:
                    self.ipAdds[ip].result = result
                    if result is not None:
                        self.ipAdds[ip].status = IpStatus.COMPLETE


        self.threadCount: int = threadCount # 사용하는 쓰레드 갯수
        self.ipPerThread: int = addPerThread # 쓰레드 하나당 할당할 주소 갯수

        self.globalProgress: Progress = Progress(len(self.ipAdds))
        self.globalProgress.count = len([0 for ipAdd in self.ipAdds.values() 
                                         if ipAdd.status == IpStatus.COMPLETE])
        self.oldProgress: int = 0

        self.isDone: int = False

        self.threads: list[Thread] = [Thread(self.globalProgress) for _ in range(threadCount)]

        self.timer: float = time.time()
        self.progressDisplayInterval: int = 1

    def update(self):
        '''
        새로운 스레드를 시작하거나 완료된 스레드의 결과를 적용하고 재실행하는  함수
        '''



        # 스레 하나하나 반복
        for thread in self.threads:

            # 스레드가 준비, 시작할수 있는 상태일시
            if thread.isWating:
                # 스레드가 실행 완료된 상태라면 결과 적용 (안해도됨)
                # if thread.status == ThreadStatus.DONE:
                #     result = thread.getResult()
                #     for ipAdd, response in result.items():
                #         self.ipResult[ipAdd] = response
                #         if response != None:
                #             self.ipStatus[ipAdd] = IpStatus.COMPLETE
                
                if self.setThreadTask(thread):
                    thread.run()


        if self.timer <= time.time():
            self.timer += self.progressDisplayInterval
            self.displayProgress()
        
        
        if self.isDone:
            print("")
            print("======================================")
            print("모든 작업이 완?료되었습니다. 모든 스레드를 종료합니다")
            print("======================================\n")
            time.sleep(1)
            self.waitAllThread()


    def displayProgress(self):
        speed = self.globalProgress.count - self.oldProgress
        self.oldProgress = self.globalProgress.count

        progressBarSize = int(os.get_terminal_size().columns * 0.9)
        displayProgress = int(progressBarSize * self.globalProgress.countRatio)
        invertDisplayProgress = progressBarSize - displayProgress
        
        print(f'전송 속도: {self.progressDisplayInterval}초당 {speed}개')
        print(f"진행도: {self.globalProgress.count}/{self.globalProgress.maxCount} |{'■'*displayProgress}{' '*invertDisplayProgress}|\n")



    # def applyResult(self, threadIndex: int):
    #     thread: Thread = self.threads[threadIndex]

    #     if thread.status == ThreadStatus.DONE:
    #         result = thread.getResult()
    #         for ipAdd, response in result.items():
    #             self.ipResult[ipAdd] = response
    #             if response != None:
    #                 self.ipStatus[ipAdd] = IpStatus.COMPLETE



    def setThreadTask(self, thread: Thread) -> bool: # 스레스 작업 설정 성공 여부 반환

        # 새 쓰레가 배정받을 ip 찾기
        ipAddsToAssign: list[IpElement] = list()

        for ipAdd in self.ipAdds.values():
            
            # 현재 확인하는 ip 가 대기상태라면
            if ipAdd.status == IpStatus.WAIT:
                ipAddsToAssign.append(ipAdd)

                # ipPerThread 갯수만큼 준비상태인 ip 를 찾음
                if len(ipAddsToAssign) == self.ipPerThread:
                    break
        
        # self.ipAdds 의 끝까지 순회했는데도 하나도 못찾았을경우
        # 완료됬아!
        if 0 == len(ipAddsToAssign): 
            self.isDone = True
            return False
        else: 
            thread.setTask(ipAddsToAssign)
            return True



    def stopAllThread(self):
        print("======================================")
        print("모든 쓰레드를 중단합니다...")
        print("======================================\n")


        for i, thread in enumerate(self.threads):
            print(f'{len(self.threads)}/{i}번 쓰레드를 중단중...')
            thread.stop()

        # for i, thread in enumerate(self.threads):
        #     print(f'{len(self.threads)}/{i}번 쓰레드가 끝나길 대기중...')
        #     thread.wait()


        print("")
        print("======================================")
        print("모든 쓰레드를 중단했습니다.")
        print("======================================\n")

    def waitAllThread(self):
        print("======================================")
        print("모든 쓰레드가 끝나길 대기합니다...")
        print("======================================\n")


        for i, thread in enumerate(self.threads):
            print(f'{len(self.threads)}/{i}번 쓰레드를 대기중...')
            thread.wait()


    # def applyAllThread(self):
    #     print("======================================")
    #     print("모든 스레드의 결과를 적용합니다...")
    #     print("======================================\n")

    #     for i in range(len(self.threads)):
    #         print(f'{len(self.threads)}/{i}번 쓰레드 결과 적용중...')
    #         self.applyResult(i)


    #     print("")
    #     print("======================================")
    #     print("모든 쓰레드의 결과를 적용했습니다")
    #     print("======================================\n")



    def saveResult(self, path: str, divisionUnit: int):
        print("======================================")
        print(f'"{path}"에 결과를 저장합니다...')
        print("======================================\n")

        fileCount = ceil(len(self.ipAdds)/divisionUnit)

        os.chdir(path)

        for i in range(fileCount):
            startIndex = i * divisionUnit
            endIndex = (i+1) * divisionUnit

            startIp = intToIP(startIndex).replace('.', '-')
            endIp = intToIP(endIndex).replace('.', '-')

            print(f"{startIp} ~ {endIp} 대역의 결과 저장중... ({i}/{fileCount} 번째 파일)")

            # 범위의 끝 인덱스가 self.ipAdds 의 범위를 벗어날 경우 안쪽으로 조정
            if endIndex > len(self.ipAdds):
                endIndex = len(self.ipAdds)
            
            partData: dict[str, bool | None] = {}
            doneIpCount = 0

            for i in range(startIndex, endIndex):
                partData[intToIP(i)] = self.ipAdds[i].result
                if self.ipAdds[i].result != None:
                    doneIpCount += 1
            
            if 0 < doneIpCount:
                with open(f"{startIp}~{endIp}-.json", 'w') as f:
                    json.dump(partData, f, indent=4)

        print("")
        print("======================================")
        print("모든 결과를 저장했습니다")
        print("======================================\n")



    # def monitorThreadStatus(self) -> None:
    #     doneIps = 0
    #     for ipStatus in self.ipStatus.values():
    #         if ipStatus == ipStatus.COMPLETE:
    #             doneIps += 1

    #     print('\n\n\n')
    #     print('===========================================')
    #     print(f'총 스래드 갯수: {self.threadCount}')
    #     print(f'총 IP {len(self.ipStatus)}개중 {doneIps}개 완료')
    #     print('===========================================\n\n')


    #     for i, thread in enumerate(self.threads):
    #         # print('================================\n')
    #         # print(f'{i}번 쓰레드')
    #         print('진행도 |'
    #               + ":"*int(thread.getProgress()[0] * 20) 
    #               + " "*(20-int(thread.getProgress()[0] * 20)) + '|')
            
    #         # print(' ')