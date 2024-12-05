# import pygame

# screen = pygame.display.set_mode((600, 600))
# pygame.display.set_caption("프랙탈 맵퍼")

# SIZE = 65536


class IpStatus:
    WAIT: int = 0
    PROCESSING: int = 1
    COMPLETE: int = 2

class IpElement():
    def __init__(self, address: int):
        if address < 0 or address > 0xFFFFFFFF:
            raise ValueError("주소는 0 ~ 4294967295 사이여야 합니다.")
    
        self.address: int = address
        self.status: int = IpStatus.WAIT
        self.result: bool | None = None
    
    @property
    def ipStr(self) -> str: return intToIP(self.address)
    
    @property
    def ifDone(self) -> str: return 

def maping(pos: list[int, int, int, int]):
    """IP 주소를 2D 평면상에 맵핑하는 함수입니다.

IP 주소는 리스트이며 주소가 a.b.c.d 라면 입력은 [a, b, c, d] 의 형태 입니다
맵핑은 왼쪽 위부터 프랙탈 형태로 맵핑되며 
좌표는 x, y 0 ~ 65,535 의 범위를 가집니다.
"""

    dpos = [4096 * (pos[0] % 16), 4096 * pos[0] // 16]

    dpos = [dpos[0] + 256 * (pos[1] % 16), dpos[1] + 256 * pos[1] // 16]

    dpos = [dpos[0] + 16 * (pos[2] % 16), dpos[1] + 16 * pos[2] // 16]

    dpos = [dpos[0] + (pos[3] % 16), dpos[1] + pos[3] // 16]

    return dpos

def nextIp(ip: list[int, int, int, int]):
    """입력받은 IP 주소를 한번 업카운트 하는 함수 입니다

IP 주소는 리스트이며 주소가 a.b.c.d 라면 입력은 [a, b, c, d] 의 형태 입니다
마지막 자리가 우선적으로 카운트 되며 
특정 자리가 255 를 넘을시 해당 자리는 0으로 초기화 하고 
그 이전 자리를 1만큼 올리는 방식입니다.
"""

    ip[3] += 1

    if ip[3] > 255:
        ip[3] = 0
        ip[2] += 1
    if ip[2] > 255:
        ip[2] = 0
        ip[1] += 1
    if ip[1] > 255:
        ip[1] = 0
        ip[0] += 1
    if ip[0] > 255:
        ip[0] = 0

    return ip



# def updateNasunwhanPos(pos: tuple[int, int]):
#     '''
#     0, 0 좌표로부터 시작하는 사각형 형태의 나선 경로를 가정하고
#     해당 경로상의 좌표를 입력받아 경로상에서 좌표가 다음에 있어야할 위치 반환함
#     '''


#     x, y = pos[0], pos[1]
#     #오른쪽 1 구역
#     if abs(y) < x:
#         return((x, y+1))
    
#     #아래쪽 2 구역
#     elif abs(x) <= -y:
#         return((x+1, y))
    
#     #위쪽 3 구역
#     elif abs(x-1) <= y:
#         return((x-1, y))
    
#     #왼족 4 구역
#     elif abs(y) <= -x:
#         return((x, y-1))


def intToIP(num: int) -> str:
    if num < 0 or num > 0xFFFFFFFF:
        raise ValueError("숫자는 0 ~ 4294967295 사이여야 합니다.")

    # 각 옥텟을 추출
    octet1 = (num >> 24) & 0xFF
    octet2 = (num >> 16) & 0xFF
    octet3 = (num >> 8) & 0xFF
    octet4 = num & 0xFF
    
    # 4개의 옥텟을 '.'로 연결하여 문자열로 반환
    return f"{octet1}.{octet2}.{octet3}.{octet4}"