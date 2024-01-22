import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

# 첫 번째 모터
GPIO_RP_1 = 13
GPIO_RN_1 = 19
GPIO_EN_1 = 26

# 두 번째 모터
GPIO_RP_2 = 16
GPIO_RN_2 = 20
GPIO_EN_2 = 21

# 서보 모터
GPIO_SERVO = 18  # 예시로 GPIO 18을 사용했습니다. 실제로 사용할 GPIO 핀으로 변경해주세요.

# 속도 설정
NORMAL_SPEED = 100  # 원래 속도 (0 ~ 100 범위)
KID_SECTION_SPEED = 50 

# GPIO 핀 설정
GPIO.setup(GPIO_RP_1, GPIO.OUT)
GPIO.setup(GPIO_RN_1, GPIO.OUT)
GPIO.setup(GPIO_EN_1, GPIO.OUT)

GPIO.setup(GPIO_RP_2, GPIO.OUT)
GPIO.setup(GPIO_RN_2, GPIO.OUT)
GPIO.setup(GPIO_EN_2, GPIO.OUT)

GPIO.setup(GPIO_SERVO, GPIO.OUT)

# 조도센서와 LED 핀 설정
CDS_PIN = 21  # 예시로 GPIO 21을 사용했습니다. 실제로 사용할 GPIO 핀으로 변경해주세요.
LED_PIN = 23  # 예시로 GPIO 23을 사용했습니다. 실제로 사용할 GPIO 핀으로 변경해주세요.
GPIO.setup(CDS_PIN, GPIO.IN)  # 조도센서 핀 설정
GPIO.setup(LED_PIN, GPIO.OUT)  # LED 핀 설정

def read_light():
    return GPIO.input(CDS_PIN)

def control_led(status):
    GPIO.output(LED_PIN, status)



def control_dc_motors(direction, speed):
    # DC 모터 제어 코드 (forward, backward, stop 등)
    pwm_1 = GPIO.PWM(GPIO_EN_1, 1000)  # PWM 주파수를 1000Hz로 설정
    pwm_2 = GPIO.PWM(GPIO_EN_2, 1000)  # PWM 주파수를 1000Hz로 설정

    pwm_1.start(speed)
    pwm_2.start(speed)

    if direction == "forward":
        # 모터를 전진 방향으로 회전
        GPIO.output(GPIO_RP_1, True)
        GPIO.output(GPIO_RN_1, False)

        GPIO.output(GPIO_RP_2, True)
        GPIO.output(GPIO_RN_2, False)
    elif direction == "backward":
        # 모터를 후진 방향으로 회전
        GPIO.output(GPIO_RP_1, False)
        GPIO.output(GPIO_RN_1, True)

        GPIO.output(GPIO_RP_2, False)
        GPIO.output(GPIO_RN_2, True)
    elif direction == "stop":
        # 모터 정지
        GPIO.output(GPIO_RP_1, False)
        GPIO.output(GPIO_RN_1, False)

        GPIO.output(GPIO_RP_2, False)
        GPIO.output(GPIO_RN_2, False)
    # 추가적인 방향 설정이 필요하다면 여기에 코드를 추가하십시오.
"""
def angle_to_percent (angle) :
    if angle > 180 or angle < 0 :
        return False

    start = 4
    end = 12.5
    ratio = (end - start)/180 #Calcul ratio from angle to percent

    angle_as_percent = angle * ratio

    return start + angle_as_percent

"""

#반대로 동작하는 servo motor의 경우?
#음수의 값도 반영될 수 있는지 확인
def control_servo(angle):
    pwm = GPIO.PWM(GPIO_SERVO, 50)  # PWM 주파수를 50Hz로 설정
    pwm.start(7.5)  # 초기 위치 (90도)에 해당하는 duty cycle 설정

    try:
        duty_cycle = 7.5 + (angle / 18)  # 각도에 따른 duty cycle 계산
        pwm.ChangeDutyCycle(duty_cycle)
        time.sleep(1)  # 서보 모터가 해당 각도로 이동할 시간을 설정
    finally:
        pwm.stop()




try:
    while True:
        # 두 모터를 동시에 전진
        # -->현재 전진하는 것이 default임.
        # -->차선인식을 했을 때 따라가도록 코드 많은 추가와 변경 필요
        GPIO.output(GPIO_RP_1, True)
        GPIO.output(GPIO_RN_1, False)
        GPIO.output(GPIO_EN_1, True)

        GPIO.output(GPIO_RP_2, True)
        GPIO.output(GPIO_RN_2, False)
        GPIO.output(GPIO_EN_2, True)

        print("직진 중")

        user_input = input(" 숫자를 입력하세요 \n")

        # 동적 장애물(어린이 보호구역)이 있을 시 정지
        if user_input == '1':
            print("차량 정지")
            # 정지를 위해 모든 핀을 비활성화
            GPIO.output(GPIO_EN_1, False)
            GPIO.output(GPIO_EN_2, False)
    
            # 5초간 정지-->동적 장애물이 있을 동안만 정지하게 해야함
            time.sleep(5)
    
            # 다시 default 상태로 돌아가기
            GPIO.output(GPIO_EN_1, True)
            GPIO.output(GPIO_EN_2, True)

        # 정적 장애물 피하기(많은 수정, 추가 필요)
        elif user_input == '2':
            print("서보 45도 회전")
            control_servo(45)
            time.sleep(5)  # 5초 동안 서보 모터가 회전한 상태 유지
            print("서보 45도 회전 해제")
            control_servo(0)  # 서보 모터를 다시 초기 위치로 회전

        # 어린이 보호구역 시작
        elif user_input == '3':
            print("DC 모터 속도 낮춤")
            control_dc_motors("forward", KID_SECTION_SPEED)

        # 어린이 보호구역 종료
        elif user_input == '4':
            print("DC 모터 속도 원래대로")
            control_dc_motors("forward", NORMAL_SPEED)

        # 터널 표지판 인식
        elif user_input == '5':
            print("터널 표지판 인식: LED 켬")
            control_led(GPIO.HIGH)
            
            # 조도가 높아질 때까지 대기
            while read_light() == GPIO.HIGH:
                time.sleep(1)

            print("조도가 높아져 LED 끔")
            control_led(GPIO.LOW)


        # 빨간 신호등 또는 최종 라인 (정차)
        elif user_input == 's':
            print("신호등 또는 최종 라인 감지, 차량 정차")
            # 정차를 위해 모든 핀을 비활성화
            GPIO.output(GPIO_EN_1, False)
            GPIO.output(GPIO_EN_2, False)

        # 좌측 차선 변경
        elif user_input == 'l':
            print("좌측 차선 변경, 서보 45도 회전 후 0.2초 대기 후 반대 방향으로 45도 회전")
            control_servo(45)
            time.sleep(0.2)  # 0.2초 동안 서보 모터가 회전한 상태 유지
            control_servo(-45)  # 반대 방향으로 45도 회전
            time.sleep(0.2)  # 0.2초 대기
            control_servo(0)  # 서보 모터를 다시 초기 위치로 회전

        # 우측 차선 변경
        elif user_input == 'r':
            print("우측 차선 변경, 서보 -45도 회전 후 0.2초 대기 후 반대 방향으로 45도 회전")
            control_servo(-45)
            time.sleep(0.2)  # 0.2초 동안 서보 모터가 회전한 상태 유지
            control_servo(45)  # 반대 방향으로 45도 회전
            time.sleep(0.2)  # 0.2초 대기
            control_servo(0)  # 서보 모터를 다시 초기 위치로 회전

        else:
            # 사용자가 1, 2, 3, 4, s, l, r를 입력하지 않은 경우 계속 직진
            pass

except KeyboardInterrupt:
    print("프로그램 종료")
finally:
    # 정지를 위해 모든 핀을 비활성화
    GPIO.output(GPIO_EN_1, False)
    GPIO.output(GPIO_EN_2, False)
    GPIO.cleanup()