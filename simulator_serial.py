import serial
import serial.tools.list_ports
import time

def find_com_port(target_port):
    """查找目标串口号是否存在于当前可用串口列表中"""
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    return target_port in available_ports

def generate_star_pattern():
    """生成一个星形图案的坐标"""
    star_points = [
        (5, 0), (6, 2), (8, 2), (7, 4), (8, 6), (6, 5), (5, 7), (4, 5), (2, 6), (3, 4), (2, 2), (4, 2)
    ]
    return star_points

def main():
    # 设置目标串口号
    target_port = 'COM7'  # 将其替换为你的设备路径
    baud_rate = 115200    # 波特率
    timeout = 2           # 设置超时时间（秒）

    print(f"正在查找串口 {target_port}...")
    if not find_com_port(target_port):
        print(f"错误: 串口 {target_port} 未找到，请检查设备连接或串口路径是否正确。")
        print("当前可用的串口设备为：")
        for port in serial.tools.list_ports.comports():
            print(f"- {port.device} ({port.description})")
        return

    try:
        # 打开指定的串口
        ser = serial.Serial(target_port, baud_rate, timeout=timeout)
        print(f"成功连接到 {target_port}，波特率为 {baud_rate}")
    except serial.SerialException as e:
        print(f"错误: 无法打开串口 {target_port} - {str(e)}")
        return

    # 生成星形图案的坐标
    star_points = generate_star_pattern()

    # 打开日志文件
    with open("serial_log.txt", "w") as log_file:
        print("开始发送串口数据... 按 Ctrl+C 终止程序")
        try:
            while True:
                for x, y in star_points:
                    data_to_send = f"{x:02d}{y:02d}\n".encode('utf-8')
                    ser.write(data_to_send)
                    data_str = data_to_send.decode('utf-8').strip()
                    print(f"已发送: {data_str}")
                    log_file.write(f"{data_str}\n")
                    # time.sleep(0.5)  # 每隔0.5秒发送一次数据
        except KeyboardInterrupt:
            print("\n程序中止，正在关闭串口连接...")
        finally:
            ser.close()
            print(f"串口 {target_port} 已关闭")

if __name__ == "__main__":
    main()
