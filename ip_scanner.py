import time
import json
import os
import glob

from progress import Progress
from iptools import intToIP, IPtoInt, IpElement, IpStatus
from math import ceil

# * threading 라이브러리를 사용하는 스레드를 사용할경우 다음 줄을 주석 해제 하세요
from thread_thread import Thread
# * asyncio 라이브러리를 사용하는 스레드를 사용할경우 다음 줄을 주석 해제 하세요 (현재는 작동 안함)
# from thread_asyncio import Thread



class IPscanner:
    def __init__(self, scanScope1: int, scanScope2: int,
                 threadCount: int, addPerThread: int,
                 data: dict[int, bool | None] | None=None) -> None:
        
        self.scanScope1: int = scanScope1
        self.scanScope2: int = scanScope2
        
        self.ipAdds: dict[int, IpElement] = {ipAdd: IpElement(ipAdd) for ipAdd in range(scanScope1, scanScope2)}

        # 미리 입력된 데이터를 ipResult 에 적용
        if data != None:
            for ip, result in data.items():
                # 미리 입력받은 데이터의 ip 주소가 
                # 스캐너의 주소 범위에 포함되는 경우
                if scanScope1 <= ip < scanScope2:
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

        if self.isDone == True: return

        # 스레 하나하나 반복
        for thread in self.threads:

            # 스레드가 준비, 시작할수 있는 상태일시
            if thread.isWating:
                if self.setThreadTask(thread):
                    thread.run()


        if self.timer <= time.time():
            self.timer += self.progressDisplayInterval
            self.displayProgress()
        
        # 작업 완료 여부 확인
        remmingIps = [... for ip in self.ipAdds.values() if not ip.isDone]
        
        # 남은 IP 가 없다면 완료된거인
        if len(remmingIps) == 0:
            self.isDone = True
            
            print("")
            print("======================================")
            print("모든 작업이 완?료되었습니다. 모든 스레드를 종료합니다")
            print("======================================\n")
            time.sleep(1)
            self.waitAllThread()

    def displayProgress(self):
        speed = self.globalProgress.count - self.oldProgress
        self.oldProgress = self.globalProgress.count

        print(f'전송 속도: {self.progressDisplayInterval}초당 {speed}개')

        maxCountStr = str(self.globalProgress.maxCount)
        progressStr = str(self.globalProgress.count)
        progressStr = ' ' * (len(maxCountStr) - len(progressStr)) + progressStr

        message = f"진행도: {progressStr}/{maxCountStr} | "

        # {'■'*displayProgress}{' '*invertDisplayProgress}|\n


        progressBarSize = int(os.get_terminal_size().columns - len(message) - 6)
        displayProgress = int(progressBarSize * self.globalProgress.countRatio)
        invertDisplayProgress = progressBarSize - displayProgress

        message += f"{'■'*displayProgress}{' '*invertDisplayProgress} |\n"

        print(message)



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
        # 작업 설정 실패를 알림
        if 0 == len(ipAddsToAssign):
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
            try: thread.stop()
            except: pass

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



    def loadResult(self, path: str):
        print("======================================")
        print(f'"{path}"에서 불러옵니다...')
        print("======================================\n")


        filePaths = glob.glob(f'{path}/*,*,*,* ~ *,*,*,*--.json')
        
        for i, filePath in enumerate(filePaths):
            fileName = os.path.basename(filePath)
            print(f'"{fileName}" 파일 불러오는중... ({i+1}/{len(filePaths)} 번째 파일)')
            
            scopeStr = fileName.split(" ~ ")
            scope1 = IPtoInt(scopeStr[0].replace(',', '.'))
            scope2 = IPtoInt(scopeStr[1].split('--')[0].replace(',', '.'))

            # 불러오는 파일의 ip 대역이 이 스캐너의 ip 대역에 포함되지 않을경우
            if  (scope1 < self.scanScope1 and scope2 < self.scanScope1) or\
                (self.scanScope2 < scope1 and self.scanScope2 < scope2): continue

            with open(filePath, 'r') as f:
                loadedData: dict[str, bool | None] = json.load(f)



            for ipStr, result in loadedData.items():
                ipAdd = IPtoInt(ipStr)
                if ipAdd < self.scanScope1 or self.scanScope2 < ipAdd: continue


                self.ipAdds[ipAdd].result = result

                if result != None: 
                    self.ipAdds[ipAdd].status = IpStatus.COMPLETE
                    self.globalProgress.count += 1



        print("")
        print("======================================")
        print("불러오기 완료")
        print("======================================\n")

    def saveResult(self, path: str, divisionUnit: int):
        print("======================================")
        print(f'"{path}"에 결과를 저장합니다...')
        print("======================================\n")

        fileCount = ceil(len(self.ipAdds)/divisionUnit)

        for i in range(fileCount):
            startIndex = i * divisionUnit
            endIndex = (i+1) * divisionUnit

            # 범위의 끝 인덱스가 self.ipAdds 의 범위를 벗어날 경우 안쪽으로 조정
            if endIndex > len(self.ipAdds):
                endIndex = len(self.ipAdds)

            startIp = intToIP(startIndex).replace('.', ',')
            endIp = intToIP(endIndex).replace('.', ',')

            print(f"{startIp} ~ {endIp} 대역의 결과 저장중... ({i+1}/{fileCount} 번째 파일)")
            
            partData: dict[str, bool | None] = {}
            doneIpCount = 0

            for i in range(startIndex, endIndex):
                partData[intToIP(i)] = self.ipAdds[i].result
                if self.ipAdds[i].result != None:
                    doneIpCount += 1
            
            if 0 < doneIpCount:
                with open(f"{path}/{startIp} ~ {endIp}--.json", 'w') as f:
                    json.dump(partData, f, indent=4)

        print("")
        print("======================================")
        print("모든 결과를 저장했습니다")
        print("======================================\n")