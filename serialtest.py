import serial
import asyncio
import random

async def generate_data(ser):
    """生成并发送数据到串口"""
    for idx in range(3):  # 生成三个点
        x = random.randint(0, 99)  # 随机生成0到99之间的x坐标
        y = random.randint(0, 99)  # 随机生成0到99之间的y坐标
        data = f"{idx}{x:02}{y:02}"  # 格式化为 idx + x + y
        ser.write(data.encode('utf-8') + b'\n')  # 发送数据
        print(f"发送数据: {data.strip()}")
        await asyncio.sleep(1)  # 每秒发送一次

async def main():
    target_port = 'COM7'  # 串口号
    baud_rate = 115200    # 波特率
    timeout = 2           # 超时时间（秒）

    try:
        # 打开指定的串口
        ser = serial.Serial(target_port, baud_rate, timeout=timeout)
        print(f"成功连接到 {target_port}，波特率为 {baud_rate}")
    except serial.SerialException as e:
        print(f"错误: 无法打开串口 {target_port} - {str(e)}")
        return

    print("开始生成数据并发送到串口...")
    try:
        await generate_data(ser)
    except KeyboardInterrupt:
        print("\n程序中止，正在关闭串口连接...")
    finally:
        ser.close()
        print(f"串口 {target_port} 已关闭")

if __name__ == "__main__":
    asyncio.run(main())
