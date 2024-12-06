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
    def strAdd(self) -> str: return intToIP(self.address)
    
    @property
    def isDone(self) -> str: return self.status == IpStatus.COMPLETE

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

def IPtoInt(ip: str) -> int:
    octets = ip.split('.')
    
    octet1 = int(octets[0])
    octet2 = int(octets[1])
    octet3 = int(octets[2])
    octet4 = int(octets[3])

    return octet1*256**3 + octet2*256**2 + octet3*256**1 + octet4