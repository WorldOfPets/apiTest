# Публикация API через cloudpub

Для упражнения по перехвату нужен открытый HTTP, поэтому публикуйте API по HTTP (не HTTPS).

1. Установите cloudpub и войдите в него (по инструкции самого инструмента).
2. Сначала запустите API локально.

   Windows:

   ```
   scripts\run_server.bat
   ```

   macOS / Linux:

   ```
   bash scripts/run_server.sh
   ```

3. Откройте порт 8000 по HTTP:

   ```
   cloudpub http 8000
   ```

4. Скопируйте публичный URL, который выведет cloudpub, например
   `http://<random>.cloudpub.example`.

5. Пропишите этот URL в `BASE_URL` в `client/api.py`, затем пересоберите.

   Windows:

   ```
   scripts\build_client.bat
   ```

   macOS / Linux:

   ```
   bash scripts/build_client.sh
   ```

6. Передайте студентам собранный клиент и URL:
   - Windows: `client/dist/ApiClient.exe`
   - Linux: `client/dist/ApiClient`
   - macOS: `client/dist/ApiClient` и `client/dist/ApiClient.app`

Примечания:
- URL туннеля меняется между запусками. Пересобирайте клиент после каждого перезапуска
  либо оставьте URL настраиваемым и предложите студентам вводить его заново.
- Закрывайте туннель после окончания занятия.
