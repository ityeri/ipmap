import asyncio
from aiocoap import *
from scapy.all import *

from blackboard.main import *

from progress import Progress
from iptools import IpElement, intToIP, IpStatus


def icmpPing(ip_address: str) -> bool:
    try:
        # Windows에서는 -n, Unix 계열에서는 -c 옵션 사용
        output = subprocess.run(["ping", "-n", "1", ip_address], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        return output.returncode == 0
    except Exception as e:
        return False




class ThreadStatus:
    WAIT: int = 0
    READY: int = 1
    RUNNING: int = 2
    DONE: int = 3

class Thread:
    '''
    이 클래스의 이름 Thread 는 이 객체가 핑을 보낼때 cpu 의 Thread 를 사용해서가 아님!
    '''
    def __init__(self, globalProgress: Progress) -> None:
        self.ipAdds: list[IpElement]

        self.globalProgress: Progress = globalProgress
        self.progress: Progress

        self.status: int = ThreadStatus.WAIT
        self.interrupt: bool = False

    def setTask(self, ipAdds: list[IpElement]):
        if self.isWating:
            for ipAdd in ipAdds: ipAdd.status = IpStatus.PROCESSING
            self.ipAdds = ipAdds

            self.progress = Progress(len(ipAdds))
            self.interrupt = False
            self.status = ThreadStatus.READY

        else: 
            raise ValueError("setTask 시에는 스레드가 대기 상태 또는 완료 상태여야 합니다")


    async def sendPing(self):
        self.status = ThreadStatus.RUNNING


        for i, ipAdd in enumerate(self.ipAdds):

            result: bool = False
            try:
                result = icmpPing(intToIP(ipAdd.address))
            except subprocess.TimeoutExpired:
                result = False  # 타임아웃 발생
            except Exception as e:
                print(f'IP {intToIP(ipAdd.address)} 에 핑 전송중 오류 발생! :')
                print(e)

            ipAdd.result = result
            ipAdd.status = IpStatus.COMPLETE
            self.progress.count = i
            self.globalProgress.count += 1

            if self.interrupt:
                self.interrupt = False
                break

        self.status = ThreadStatus.DONE

    def run(self):
        if self.isReady:
            self.sendPing()
        else: raise ValueError('스레드 실행시에는 스레드가 준비 상태여야 합니')

    def stop(self):
        if self.isRunning:
            self.interrupt = True
            self.wait()
        else: raise ValueError("쓰레드 안돌아가고있듬")

        while not self.isWating: pass

    def wait(self):
        while self.isRunning: pass


    def getProgress(self) -> tuple[float, int]:
        return self.progress.countRatio, self.progress.count

    # def getResult(self) -> dict[int, bool] | None:
    #     if self.status == ThreadStatus.DONE:
    #         return self.result
    #     else: return None


    @property
    def isRunning(self) -> bool: return self.status == ThreadStatus.RUNNING
    @property
    def isReady(self) -> bool: 
        '.run 으로 바로 실행 가능한지 여부'
        return self.status == ThreadStatus.READY
    @property
    def isWating(self) -> bool:
        return self.status == ThreadStatus.WAIT or self.status == ThreadStatus.DONE