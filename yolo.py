from ultralytics import YOLO
import cv2
import websocket
import json
import threading
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
# USE_SAVED_AFFINE_MATRIX = False  # 修改此变量以控制行为

def compute_affine_transform(src_pts, dst_pts):
    """
    计算仿射变换矩阵
    """
    src = np.array(src_pts, dtype=np.float32)
    dst = np.array(dst_pts, dtype=np.float32)
    matrix = cv2.getAffineTransform(src, dst)
    return matrix

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

def manual_select_affine_matrix(frame, output_matrix_path=AFFINE_MATRIX_PATH):
    """
    手动选择三个点计算仿射变换矩阵
    """
    clicked_points = []

    def mouse_callback(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            clicked_points.append((x, y))
            print(f"已选择点：({x}, {y})")
            if len(clicked_points) == 3:
                cv2.destroyAllWindows()

    print("请依次点击：原点 (0,0)，X轴参考点 (100,0)，Y轴参考点 (0,100)。")
    print("如需重置，关闭窗口并重新运行。")

    cv2.namedWindow('Select Points')
    cv2.setMouseCallback('Select Points', mouse_callback)

    while len(clicked_points) < 3:
        cv2.imshow('Select Points', frame)
        cv2.waitKey(1)

    dst_points = [(0, 0), (100, 0), (0, 100)]
    affine_matrix = compute_affine_transform(clicked_points, dst_points)

    np.save(output_matrix_path, affine_matrix)
    print(f"仿射变换矩阵已保存到 '{output_matrix_path}'。")

    return affine_matrix

def apply_affine_transform(x, y, M):
    """
    应用仿射变换矩阵 M 到点 (x, y)。
    """
    point = np.array([x, y, 1], dtype=np.float32)
    transformed_point = M @ point
    return int(transformed_point[0]), int(transformed_point[1])

def on_open(ws):
    print("WebSocket 连接已打开。")
    threading.Thread(target=send_keypoints, args=(ws,), daemon=True).start()

def on_close(ws, close_status_code, close_msg):
    print(f"WebSocket 连接已关闭: {close_status_code} - {close_msg}")
    cap.release()
    cv2.destroyAllWindows()

def on_error(ws, error):
    print(f"WebSocket 错误: {error}")

def send_keypoints(ws):
    while True:
        ret, frame = cap.read()
        if not ret:
            print("错误：无法从视频流读取帧。")
            break

        try:
            results = model(frame)
            if results:
                for result in results:
                    keypoints = result.keypoints
                    if keypoints is not None:
                        keypoints_xy = keypoints.xy.cpu().numpy()
                        keypoints_data = {}
                        for obj_idx in range(keypoints_xy.shape[0]):
                            for kp_idx in range(keypoints_xy.shape[1]):
                                keypoint = keypoints_xy[obj_idx, kp_idx]
                                if len(keypoint) >= 2:
                                    x, y = keypoint[:2]
                                    x_b, y_b = apply_affine_transform(x, y, affine_matrix)
                                    keypoint_id = f"keypoint_{kp_idx}"
                                    keypoints_data[keypoint_id] = {'x': x_b, 'y': y_b}
                                    cv2.circle(frame, (int(x), int(y)), 3, (0, 0, 255), 2)
                        ws.send(json.dumps({'keypoints': keypoints_data}))
            else:
                print("当前帧未检测到任何对象。")

            cv2.imshow('Pose Estimation', frame)
        except Exception as e:
            print(f"发生错误: {e}")
            continue

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()
    ws.close()

def run_websocket():
    ws = websocket.WebSocketApp(
        WEBSOCKET_URL,
        on_open=on_open,
        on_close=on_close,
        on_error=on_error
    )
    ws.run_forever(ping_interval=60, ping_timeout=10)

if __name__ == "__main__":
    cap = cv2.VideoCapture(SOURCE)
    if not cap.isOpened():
        print("错误：无法打开视频流。")
        exit()

    ret, calibration_frame = cap.read()
    if not ret:
        print("错误：无法从视频流读取帧。")
        cap.release()
        exit()

    try:
        if USE_SAVED_AFFINE_MATRIX:
            affine_matrix = load_affine_matrix()
        else:
            affine_matrix = manual_select_affine_matrix(calibration_frame)
    except Exception as e:
        print(f"仿射变换失败: {e}")
        cap.release()
        exit()

    try:
        model = YOLO(YOLO_MODEL_PATH, task='pose')
        print("成功加载YOLO模型。")
    except Exception as e:
        print(f"错误：无法加载YOLO模型。详情: {e}")
        cap.release()
        exit()

    run_websocket()
