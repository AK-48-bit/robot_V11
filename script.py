from __future__ import annotations

import json
import math
from base64 import b64decode
from datetime import datetime
from pathlib import Path
import asyncio, asyncssh, sys
import paramiko

import asyncssh
import matplotlib.pyplot as plt
import numpy as np
from fastapi import HTTPException
from PIL import Image
from pydantic import BaseModel

#from config import settings

ROBOT_HOST="192.168.11.10"

JETSON_HOST="192.168.11.12"
JETSON_USER="jetadmin"
JETSON_PASSWORD="JetPass123!"

class Coordinate(BaseModel):
    top: list[float]
    bottom: list[float]
    left: list[float]
    right: list[float]
    center: list[float]


class CucumberResponse(BaseModel):
    image_path: str
    found_cucumbers: int
    coordinates: list[Coordinate] | None


GET_CUCUMBERS_CURL_COMMAND_old = """
    curl -X POST \
    -H 'Content-Type: application/json' \
    -d '{"output_folder": "/mnt/DATA/output", "brighten": 0}' \
    'http://[::1]:80/capture_segment_locate'
    """
GET_CUCUMBERS_CURL_COMMAND = """
    curl -X POST \
    -H 'Content-Type: application/json' \
    -d '{"brighten": 0}' \
    'http://[::1]:8080/capture_segment_locate'
    """



def save_image(base64_data: str, output_dir: str = './images') -> str:
    """
    Декодирует изображение из base64 и сохраняет его в директории.
    :param base64_data: Строка base64 изображения.
    :param output_dir: Путь к директории, куда будет сохранено изображение.
    :return: Полный путь к сохраненному изображению.
    """
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().strftime('%Y%m%d_%H-%M-%S')
    output_path = Path(output_dir) / f'r.png'

    image_array = arr_from_b64_str(base64_data)
    image = Image.fromarray(image_array)
    image.save(output_path)

    return str(output_path)


def arr_from_b64_str(
        b64_str: str,
        shape: tuple[int, int, int] = (1440, 2560, 3),
):
    return np.frombuffer(bytearray(b64decode(b64_str)), np.uint8).reshape(shape)


def display_image(image_path: str) -> None:
    """
    Отображает изображение, используя matplotlib.
    :param image_path: Путь к изображению.
    """
    img = plt.imread(image_path)
    plt.imshow(img)
    plt.axis('off')
    plt.show()

def get_cucumbers_coordinates() -> CucumberResponse:
    #print("result")
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(hostname=JETSON_HOST, username=JETSON_USER, password=JETSON_PASSWORD)
    stdin, stdout, stderr = client.exec_command(GET_CUCUMBERS_CURL_COMMAND)
    data = stdout.read()
    try:
        data = json.loads(data)
    except json.JSONDecodeError:
        raise HTTPException(
            status_code=500,
            detail=f'Error decoding: {data.stdout}',
        )

    coordinates = data['all_coordinates']['pixel_coordinates']
    metric_coordinates = data['all_coordinates']['metric_coordinates_centered']
    #print(coordinates)
    image_base64 = data['image']

    image_path = save_image(image_base64)
    # display_image(image_path)
    #print(len(coordinates))
    client.close()
    return coordinates, metric_coordinates

#print(get_cucumbers_coordinates())
