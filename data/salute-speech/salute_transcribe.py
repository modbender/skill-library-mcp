#!/usr/bin/env python3
"""
Скрипт для транскрибации аудио через Salute Speech API

Автоматически выполняет все 5 шагов:
1. Получение токена доступа
2. Загрузка аудиофайла
3. Создание задания на транскрибацию
https://developers.sber.ru/docs/ru/salutespeech/rest/post-async-speech-recognition
4. Проверка статуса задания
5. Получение результата транскрибации
"""

import requests
import base64
import uuid
import time
import json
import sys
import os
import argparse
from pathlib import Path
from typing import Dict
from datetime import datetime


class SaluteSpeechClient:
    """Клиент для работы с Salute Speech API"""

    def __init__(
        self,
        auth_data: str | tuple[str, str],
        scope: str = "SALUTE_SPEECH_PERS",
        verify_ssl=False
    ):
        """
        Инициализация клиента

        Args:
            auth_data: или пара (client_id, client_secret) или сразу готовый authorization_key из личного кабинета
                https://developers.sber.ru/docs/ru/salutespeech/api/authentication
            scope: Тип доступа (SALUTE_SPEECH_PERS для физлиц, SALUTE_SPEECH_CORP для юрлиц)
            verify_ssl: Флаг проверки SSL
        """
        if type(auth_data) == str:
            self.auth_data = auth_data
        else:
            # значит нам на вход подали client_id и client_secret
            auth_string = f"{auth_data[0]}:{auth_data[1]}"
            self.auth_data = base64.b64encode(auth_string.encode()).decode()

        self.scope = scope

        # URL endpoints
        self.oauth_url = "https://ngw.devices.sberbank.ru:9443/api/v2/oauth"
        self.upload_url = "https://smartspeech.sber.ru/rest/v1/data:upload"
        self.recognize_url = (
            "https://smartspeech.sber.ru/rest/v1/speech:async_recognize"
        )
        self.task_status_url = "https://smartspeech.sber.ru/rest/v1/task:get"
        self.download_url = "https://smartspeech.sber.ru/rest/v1/data:download"
        self.verify_ssl = verify_ssl
        if not self.verify_ssl:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    def get_access_token(self) -> str:
        """
        Получение токена доступа

        Returns:
            str: Токен доступа
        """
        print("Получение токена доступа...")

        # Генерация уникального ID запроса
        rq_uid = str(uuid.uuid4())

        headers = {
            "RqUID": rq_uid,
            "Authorization": f"Basic {self.auth_data}",
            "Content-Type": "application/x-www-form-urlencoded",
        }

        data = {"scope": self.scope}

        try:
            response = requests.post(
                self.oauth_url, headers=headers, data=data, verify=self.verify_ssl
            )
            response.raise_for_status()

            result = response.json()
            self.access_token = result.get("access_token") or result.get(
                "Токен доступа"
            )

            if not self.access_token:
                raise ValueError("Токен не найден в ответе сервера")

            print(f"Токен получен успешно")
            print(
                f"   Истекает в: {datetime.fromtimestamp(result.get('expires_at',1000)/1000).strftime('%Y-%m-%d %H:%M:%S')}"
            )
            return self.access_token

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении токена: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"   Ответ сервера: {e.response.text}")
            raise

    def upload_file(
        self, audio_file_path: str, content_type: str = "audio/mpeg"
    ) -> str:
        """
        Загрузка аудиофайла для транскрибации

        Args:
            audio_file_path: Путь к аудиофайлу
            content_type: MIME-тип файла (audio/mpeg, audio/wav и т.д.)

        Returns:
            str: ID загруженного файла (request_file_id)
        """
        print(f"\nЗагрузка файла '{audio_file_path}'...")

        if not self.access_token:
            raise ValueError("Сначала нужно получить токен доступа")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": content_type,
            "Accept": "application/json",
        }

        try:
            with open(audio_file_path, "rb") as audio_file:
                response = requests.post(
                    self.upload_url,
                    headers=headers,
                    data=audio_file,
                    verify=self.verify_ssl,
                )
                response.raise_for_status()

            result = response.json()
            request_file_id = result["result"]["request_file_id"]

            print(f"Файл загружен успешно")
            print(f"   File ID: {request_file_id}")
            return request_file_id

        except FileNotFoundError:
            print(f"Файл не найден: {audio_file_path}")
            raise
        except requests.exceptions.RequestException as e:
            print(f"Ошибка при загрузке файла: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"   Ответ сервера: {e.response.text}")
            raise

    def create_recognition_task(
        self,
        request_file_id: str,
        model: str = "general",
        audio_encoding: str = "MP3",
        language: str = "ru-RU",
        **kwargs,
    ) -> str:
        """
        Шаг 3: Создание задания на транскрибацию

        Args:
            request_file_id: ID загруженного файла
            model: Модель распознавания (general, callcenter)
            audio_encoding: Кодек (PCM_S16LE, OPUS, MP3, FLAC, ALAW, MULAW)
            language: Язык распознавания (ru-RU, en-US, kk-KZ, ky-KG, uz-UZ)
            **kwargs: Дополнительные параметры (enable_profanity_filter, hypotheses_count и т.д.)
                https://developers.sber.ru/docs/ru/salutespeech/rest/post-async-speech-recognition

        Returns:
            str: ID созданной задачи
        """
        print(f"\nСоздание задания на транскрибацию...")

        if not self.access_token:
            raise ValueError("Сначала нужно получить токен доступа")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

        # Базовые параметры
        payload = {
            "options": {
                "model": model,
                "audio_encoding": audio_encoding,
                "language": language,
                "enable_profanity_filter": kwargs.get("enable_profanity_filter", False),
                "hypotheses_count": kwargs.get("hypotheses_count", 1),
                "channels_count": kwargs.get("channels_count", 1),
            },
            "request_file_id": request_file_id,
        }

        # Добавляем дополнительные параметры, если они есть
        if "hints" in kwargs:
            payload["options"]["hints"] = kwargs["hints"]
        if "speaker_separation_options" in kwargs:
            payload["options"]["speaker_separation_options"] = kwargs[
                "speaker_separation_options"
            ]

        try:
            response = requests.post(
                self.recognize_url,
                headers=headers,
                json=payload,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            result = response.json()
            task_id = result["result"]["id"]
            task_status = result["result"]["status"]

            print(f"Задание создано успешно")
            print(f"   Task ID: {task_id}")
            print(f"   Статус: {task_status}")
            return task_id

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при создании задания: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"   Ответ сервера: {e.response.text}")
            raise

    def check_task_status(self, task_id: str) -> tuple[str, str | None]:
        """
        Проверка статуса задания

        Args:
            task_id: ID задания

        Returns:
            tuple: Статус задания (NEW, DONE, RUNNING,ERROR, CANCELED),  response_file_id - id выходного файла,
            или None, если задание в работе

        """
        if not self.access_token:
            raise ValueError("Сначала нужно получить токен доступа")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/octet-stream",
        }

        params = {"id": task_id}

        try:
            response = requests.get(
                self.task_status_url,
                headers=headers,
                params=params,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            result = response.json()
            #  {'status': 200,
            #  'result': {'id': 'eb38d809fc71d8926c9d7d10dabc05fb',
            #   'created_at': '2025-12-12T15:26:36.52494+03:00',
            #   'updated_at': '2025-12-12T15:27:48.212184+03:00',
            #   'status': 'DONE',
            #   'response_file_id': 'f4dd46c8-ac2c-42a8-8338-532c23025f99'}}
            status = result.get("result").get("status")
            if status == "DONE":
                return status, result.get("result").get("response_file_id")

            return status, None

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при проверке статуса: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"   Ответ сервера: {e.response.text}")
            raise

    def wait_for_completion(
        self, task_id: str, max_wait_time: int = 300, check_interval: int = 5
    ) -> tuple[str, str | None]:
        """
        Ожидание завершения задания

        Args:
            task_id: ID задания
            max_wait_time: Максимальное время ожидания в секундах
            check_interval: Интервал проверки в секундах

        Returns:
            tuple - cтатус задания (NEW, DONE, RUNNING, ERROR, CANCELED) , response_file_id - id выходного файла
        """
        print(f"\nОжидание завершения обработки...")

        elapsed_time = 0
        while elapsed_time < max_wait_time:
            status, response_file_id = self.check_task_status(task_id)

            if status in ["DONE", "ERROR", "CANCELED"]:
                print(f"Обработка завершена со статусом {status} за {elapsed_time}сек")
                return status, response_file_id
            else:
                print(f"   Статус: {status} (прошло {elapsed_time}с)")
                time.sleep(check_interval)
                elapsed_time += check_interval

        print(f"Превышено время ожидания ({max_wait_time}с)")
        return "ERROR", None

    def download_result(self, response_file_id: str) -> list[Dict]:
        """
        Получение результата транскрибации

        Args:
            response_file_id: ID выходного файла

        Returns:
            dict: JSON с результатом транскрибации
        """
        print(f"\nПолучение результата транскрибации...")

        if not self.access_token:
            raise ValueError("Сначала нужно получить токен доступа")

        headers = {
            "Authorization": f"Bearer {self.access_token}",
            "Accept": "application/json",
        }

        params = {"response_file_id": response_file_id}

        try:
            response = requests.get(
                self.download_url,
                headers=headers,
                params=params,
                verify=self.verify_ssl,
            )
            response.raise_for_status()

            result = response.json()

            print(f"Результат получен успешно")
            return result

        except requests.exceptions.RequestException as e:
            print(f"Ошибка при получении результата: {e}")
            if hasattr(e, "response") and e.response is not None:
                print(f"   Ответ сервера: {e.response.text}")
            raise

    def transcribe_audio(
        self,
        audio_file_path: str,
        content_type: str = "audio/mpeg",
        model: str = "general",
        audio_encoding: str = "MP3",
        language: str = "ru-RU",
        max_wait_time: int = 300,
        **kwargs,
    ) -> list[Dict]:
        """
        Полный цикл транскрибации аудио

        Args:
            audio_file_path: Путь к аудиофайлу
            content_type: MIME-тип файла
            model: Модель распознавания
            audio_encoding: Кодек
            language: Язык распознавания
            save_to_file: Путь для сохранения результата в JSON файл
            max_wait_time: Таймаут ожидания транскрибации в секундах
            **kwargs: Дополнительные параметры

        Returns:
            dict: Результат транскрибации
        """
        print("=" * 70)
        print("Транскрибация аудио через Salute Speech API")
        print("=" * 70)

        try:
            # Шаг 1: Получение токена
            self.get_access_token()

            # Шаг 2: Загрузка файла
            request_file_id = self.upload_file(audio_file_path, content_type)

            # Шаг 3: Создание задания
            task_id = self.create_recognition_task(
                request_file_id,
                model=model,
                audio_encoding=audio_encoding,
                language=language,
                **kwargs,
            )

            # Шаг 4: Ожидание завершения
            status, response_file_id = self.wait_for_completion(task_id, max_wait_time)
            if not response_file_id:
                raise RuntimeError("Возникла ошибка во время обработки")

            # Шаг 5: Получение результата
            result = self.download_result(response_file_id)
            return result

        except Exception as e:
            print(f"\nОшибка: {e}")
            raise

    @classmethod
    def format_transcript(cls, chunks: list[dict], use_normalized: bool = True) -> str:
        """Форматируем результаты распознавания Sber Salute Speech в нормальный текст.

        Args:
            chunks: оригинальный формат возвращаемых данных, который нигде не описан.
            use_normalized: использовать нормализованный текст или оригинальный

        Returns:
            Красивый текст в виде:
            [00:01 - 00:20]:
            Ну, даже если сосредоточиться на идее узкой щели
        """

        def _parse_seconds(raw: str) -> float:
            """ '123.456s' или '123.456000512s' в секунды float"""
            return float(raw.rstrip("s"))

        def _format_time(raw: str) -> str:
            """ '63.237001216s' -> '01:03' """
            total = int(_parse_seconds(raw))
            hours, remainder = divmod(total, 3600)
            minutes, seconds = divmod(remainder, 60)
            if hours:
                return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
            return f"{minutes:02d}:{seconds:02d}"


        def _speaker_label(speaker_id: int) -> str:
            """ Проекция speaker_id 0,1,2... -> Speaker A, Speaker B, ..."""
            if speaker_id < 26:
                return f"Speaker {chr(65 + speaker_id)}"
            return f"Speaker {speaker_id}"

        text_key = "normalized_text" if use_normalized else "text"
        paragraphs = []

        for chunk in chunks:
            for segment in chunk.get("results", []):
                text = segment.get(text_key, "").strip()
                if not text:
                    continue

                start = _format_time(segment.get("start", "0s"))
                end = _format_time(segment.get("end", "0s"))

                speaker_id = chunk.get("speaker_info", {}).get("speaker_id", -1)
                if speaker_id >= 0:
                    speaker = _speaker_label(speaker_id)
                    paragraphs.append(f"[{start} - {end}] {speaker}:\n{text}")
                else:
                    paragraphs.append(f"[{start} - {end}]:\n{text}")

        return "\n\n".join(paragraphs)




def main():
    parser = argparse.ArgumentParser(
        description="Transcribe audio/video file using Salute Speech API"
    )
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument(
        "--file", help="Audio/video file path to transcribe")
    parser.add_argument("--output_dir", default="~/.openclaw/workspace/transcribations", help="Output directory (default: ~/.openclaw/workspace/transcribations)")
    parser.add_argument(
        "--lang",
        default="ru-RU",
        help="Language code (default: ru-RU) or ru-RU, en-US, kk-KZ, ky-KG, uz-UZ",
    )
    parser.add_argument("--audio-encoding", default="MP3", help="Audio encoding MP3, PCM_S16LE, OPUS, FLAC, ALAW, MULAW")
    parser.add_argument("--model", default="general", help="Audio model - general or callcenter")
    parser.add_argument("--print", action="store_true", help="Print transcription to stdout")
    parser.add_argument("--hyp-count", type=int, default=1, help="Number of alternative translations 1 or 2 ")
    parser.add_argument("--max-wait-time", type=int, default=300, help="Max seconds to wait for result")
    args = parser.parse_args()

    # Получаем ключ авторизации
    AUTH_DATA = os.environ.get("SALUTE_AUTH_DATA")

    if not AUTH_DATA:
        print("ERROR: SALUTE_AUTH_DATA environment variable not set.")
        sys.exit(1)

    # Создание клиента
    client = SaluteSpeechClient(auth_data=AUTH_DATA)

    # Create output directory
    Path(args.output_dir).mkdir(parents=True, exist_ok=True)

    # Параметры транскрибации
    result = client.transcribe_audio(
        audio_file_path=args.file,
        content_type="audio/mpeg",  # Измените в соответствии с вашим форматом
        model=args.model,  # или "callcenter"
        audio_encoding=args.audio_encoding,  # MP3, PCM_S16LE, OPUS, FLAC, ALAW, MULAW
        language=args.lang,  # ru-RU, en-US, kk-KZ, ky-KG, uz-UZ
        max_wait_time = args.max_wait_time,
        # Дополнительные параметры:
        enable_profanity_filter=False,
        hypotheses_count=args.hyp_count
    )

    # Сохранение в файл оригинального распознавания
    save_to_file = Path(args.output_dir) / f"{Path(args.file).stem}_recognition_orig.json"
    with open(save_to_file, "w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)
    
    # Сохранение в файл полотна текста
    save_to_file = Path(args.output_dir) / f"{Path(args.file).stem}_pretty.txt"
    with open(save_to_file, "w", encoding="utf-8") as f:
        f.write(SaluteSpeechClient.format_transcript(result))

    if args.print:
        print(SaluteSpeechClient.format_transcript(result))

if __name__ == "__main__":
    main()
