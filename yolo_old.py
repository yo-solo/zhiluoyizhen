from ultralytics import YOLO
import cv2
import websocket
import json
import threading
import time
import numpy as np
import math
import os

# WebSocket URL
WEBSOCKET_URL = "ws://localhost:9000/ws/keypoints"

# 路径到仿射变换矩阵文件
AFFINE_MATRIX_PATH = 'affine_matrix_old.npy'

# YOLO模型路径
YOLO_MODEL_PATH = 'best_v8m.pt'

# RTSP视频流源
SOURCE = 'http://192.168.31.211/mjpeg/1'

# 图像尺寸（用于仿射变换计算）
IMAGE_WIDTH = 800
IMAGE_HEIGHT = 600

# 控制是否使用已保存的仿射变换矩阵
USE_SAVED_AFFINE_MATRIX = True  # 修改此变量以控制行为

def find_intersection(line1, line2):
    """
    计算两条线的交点
    每条线由四个坐标表示 [x1, y1, x2, y2]
    """
    x1, y1, x2, y2 = line1
    x3, y3, x4, y4 = line2

    denom = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    if denom == 0:
        return None  # 平行或重合

    px = ((x1*y2 - y1*x2)*(x3 - x4) - (x1 - x2)*(x3*y4 - y3*x4)) / denom
    py = ((x1*y2 - y1*x2)*(y3 - y4) - (y1 - y2)*(x3*y4 - y3*x4)) / denom
    return int(px), int(py)

def get_best_line(lines):
    """
    从线条列表中选择最长的线条
    """
    if not lines:
        return None
    best_line = max(lines, key=lambda line: math.hypot(line[2]-line[0], line[3]-line[1]))
    return best_line

def compute_affine_transform(src_pts, dst_pts):
    """
    计算仿射变换矩阵
    """
    src = np.array(src_pts, dtype=np.float32)
    dst = np.array(dst_pts, dtype=np.float32)
    matrix = cv2.getAffineTransform(src, dst)
    return matrix

def calculate_affine_matrix(calibration_frame, output_matrix_path=AFFINE_MATRIX_PATH):
    """
    使用校准帧计算仿射变换矩阵并保存
    """
    img = cv2.resize(calibration_frame, (IMAGE_WIDTH, IMAGE_HEIGHT))
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    # 红色在HSV中有两个范围
    lower_red1 = np.array([0, 70, 50])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170,70,50])
    upper_red2 = np.array([180,255,255])
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    mask = cv2.bitwise_or(mask1, mask2)

    # 使用Canny边缘检测
    edges = cv2.Canny(mask, 50, 150, apertureSize=3)

    # 使用HoughLinesP检测线条
    lines = cv2.HoughLinesP(edges, 1, np.pi / 180, threshold=100, minLineLength=100, maxLineGap=10)

    if lines is None:
        raise ValueError("未检测到任何线条。")

    # 分离水平和垂直线
    horizontal_lines = []
    vertical_lines = []

    for line in lines:
        for x1, y1, x2, y2 in line:
            # 计算线条角度
            angle = math.degrees(math.atan2((y2 - y1), (x2 - x1)))
            if -30 <= angle <= 30:
                horizontal_lines.append([x1, y1, x2, y2])
            elif 50 <= abs(angle) <= 130:
                vertical_lines.append([x1, y1, x2, y2])

    if not horizontal_lines or not vertical_lines:
        raise ValueError("未检测到足够的水平或垂直线条。")

    # 获取X轴和Y轴
    x_axis = get_best_line(horizontal_lines)
    y_axis = get_best_line(vertical_lines)

    if x_axis is None or y_axis is None:
        raise ValueError("无法找到代表性的X轴或Y轴。")

    # 计算原点为两条线的交点
    origin = find_intersection(x_axis, y_axis)
    if origin is None:
        raise ValueError("无法找到两条线的交点。")

    # 选择X轴的端点：选择距离原点更远的点
    dist_x1 = math.hypot(x_axis[0] - origin[0], x_axis[1] - origin[1])
    dist_x2 = math.hypot(x_axis[2] - origin[0], x_axis[3] - origin[1])
    if dist_x1 > dist_x2:
        x_end = (x_axis[0], x_axis[1])
    else:
        x_end = (x_axis[2], x_axis[3])

    # 选择Y轴的端点：选择距离原点更远的点
    dist_y1 = math.hypot(y_axis[0] - origin[0], y_axis[1] - origin[1])
    dist_y2 = math.hypot(y_axis[2] - origin[0], y_axis[3] - origin[1])
    if dist_y1 > dist_y2:
        y_end = (y_axis[0], y_axis[1])
    else:
        y_end = (y_axis[2], y_axis[3])

    # 定义坐标系B中的目标点（假设坐标系B的原点为(0,0)，X轴为(100,0)，Y轴为(0,100)）
    origin_B = (0, 0)
    x_end_B = (100, 0)
    y_end_B = (0, 100)

    # 计算仿射变换矩阵
    src_pts = [origin, x_end, y_end]
    dst_pts = [origin_B, x_end_B, y_end_B]
    affine_matrix = compute_affine_transform(src_pts, dst_pts)

    # 保存仿射变换矩阵为.npy文件
    np.save(output_matrix_path, affine_matrix)
    print(f"仿射变换矩阵已保存到 '{output_matrix_path}'。")

    return affine_matrix

def load_affine_matrix(matrix_path=AFFINE_MATRIX_PATH):
    """
    从.npy文件加载仿射变换矩阵
    """
    if os.path.exists(matrix_path):
        affine_matrix = np.load(matrix_path)
        print(f"仿射变换矩阵已从 '{matrix_path}' 加载。")
        return affine_matrix
    else:
        raise FileNotFoundError(f"未找到仿射变换矩阵文件: {matrix_path}")

def apply_affine_transform(x, y, M):
    """
    应用仿射变换矩阵 M 到点 (x, y)。
    """
    point = np.array([x, y, 1], dtype=np.float32)
    transformed_point = M @ point
    return int(transformed_point[0]), int(transformed_point[1])

def on_open(ws):
    print("WebSocket 连接已打开。")
    # 在单独的线程中开始发送关键点
    threading.Thread(target=send_keypoints, args=(ws,), daemon=True).start()

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket 连接已关闭: {close_status_code} - {close_msg}")
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

def on_error(ws, error):
    print(f"WebSocket 错误: {error}")

def on_ping(ws, message):
    print("收到来自服务器的 ping。")
    # websocket-client 库会自动响应 pong

def on_pong(ws, message):
    print("收到来自服务器的 pong。")

def send_keypoints(ws):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误：无法从视频流读取帧。")
            break
        try:
            # 执行推理
            results = model(frame)

            if results:
                for result in results:
                    keypoints = result.keypoints
                    if keypoints is not None:
                        # 将张量移动到 CPU 并转换为 NumPy 数组
                        keypoints_xy = keypoints.xy.cpu().numpy()
                        keypoints_data = {}
                        for obj_idx in range(keypoints_xy.shape[0]):
                            for kp_idx in range(keypoints_xy.shape[1]):
                                keypoint = keypoints_xy[obj_idx, kp_idx]
                                if len(keypoint) >= 2:
                                    x, y = keypoint[:2]
                                    # 应用仿射变换
                                    x_b, y_b = apply_affine_transform(x, y, affine_matrix)
                                    keypoint_id = f"keypoint_{kp_idx}"
                                    keypoints_data[keypoint_id] = {'x': x_b, 'y': y_b}
                                    # 在原图上绘制原始关键点
                                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), 2)
                                    # 可选：在转换后的坐标上绘制关键点
                                    # cv2.circle(frame, (x_b, y_b), 3, (255, 0, 0), 2)
                        # 发送所有关键点数据到后端
                        ws.send(json.dumps({'keypoints': keypoints_data}))
            else:
                print("当前帧未检测到任何对象。")

            # 显示推理结果
            cv2.imshow('Pose Estimation', frame)
        except Exception as e:
            print(f"发生错误: {e}")
            # 为了避免 WebSocket 连接因单帧错误而关闭，建议继续循环
            continue

        # 按 'q' 键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

        # 可选：短暂休眠以避免过度发送
        # time.sleep(0.05)  # 根据需要调整

    # 释放资源
    cap.release()
    cv2.destroyAllWindows()
    ws.close()

def run_websocket():
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error,
        on_ping=on_ping,
        on_pong=on_pong
    )
    # 启用 run_forever 以处理传入的消息和 ping
    ws.run_forever(ping_interval=60, ping_timeout=10)

if __name__ == "__main__":
    # 打开视频流
    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        print("错误：无法打开视频流。")
        exit()

    # 捕获一帧用于校准
    ret, calibration_frame = cap.read()
    if not ret:
        print("错误：无法从视频流读取校准帧。")
        cap.release()
        exit()

    # 根据布尔变量决定计算或加载仿射矩阵
    try:
        if USE_SAVED_AFFINE_MATRIX:
            affine_matrix = load_affine_matrix()
        else:
            affine_matrix = calculate_affine_matrix(calibration_frame)
    except Exception as e:
        print(f"仿射变换计算或加载失败: {e}")
        cap.release()
        exit()

    # 加载YOLO模型，明确指定在 GPU 上运行
    try:
        model = YOLO(YOLO_MODEL_PATH, task='pose')  # 确保模型在 GPU 上运行
        print("成功加载YOLO模型。")
    except Exception as e:
        print(f"错误：无法加载YOLO模型。详情: {e}")
        cap.release()
        exit()

    # 运行WebSocket
    run_websocket()
