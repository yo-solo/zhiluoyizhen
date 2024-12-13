import serial
import serial.tools.list_ports
import asyncio

def find_com_port(target_port):
    """查找目标串口号是否存在于当前可用串口列表中"""
    available_ports = [port.device for port in serial.tools.list_ports.comports()]
    return target_port in available_ports

async def send_periodic_data(ser):
    """每隔 0.1 秒发送一次数据到串口"""
    data = '111122223333\r'
    while True:
        ser.write(data.encode('utf-8'))
        print(f"已发送数据: {data.strip()}")
        await asyncio.sleep(0.1)

async def main():
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

    print("开始每隔 0.1 秒发送数据到串口... 按 Ctrl+C 终止程序")
    try:
        await send_periodic_data(ser)
    except KeyboardInterrupt:
        print("\n程序中止，正在关闭串口连接...")
    finally:
        ser.close()
        print(f"串口 {target_port} 已关闭")

if __name__ == "__main__":
    asyncio.run(main())
