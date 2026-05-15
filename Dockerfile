FROM python:3.13-bullseye


WORKDIR /app

COPY . .

RUN pip install --upgrade pip
RUN pip install "poetry==2.1.4" requests pytz
RUN poetry self add poetry-plugin-export

RUN apt update \
    && apt install -y wget gnupg2 \
    && wget -O - https://packages.adoptium.net/artifactory/api/gpg/key/public | gpg --dearmor -o /usr/share/keyrings/adoptium.gpg \
    && echo "deb [signed-by=/usr/share/keyrings/adoptium.gpg] https://packages.adoptium.net/artifactory/deb $(awk -F= '/^VERSION_CODENAME/{print$2}' /etc/os-release) main" | tee /etc/apt/sources.list.d/adoptium.list \
    && apt update \
    && apt install -y temurin-21-jre apt-transport-https ca-certificates gnupg jq \
    && echo "deb [signed-by=/usr/share/keyrings/cloud.google.gpg] https://packages.cloud.google.com/apt cloud-sdk main" | tee -a /etc/apt/sources.list.d/google-cloud-sdk.list \
    && curl https://packages.cloud.google.com/apt/doc/apt-key.gpg | apt-key --keyring /usr/share/keyrings/cloud.google.gpg add - \
    && apt update \
    && apt install -y google-cloud-cli \
    && apt install -y google-cloud-cli-datastore-emulator \
    && apt install -y wait-for-it \
    && apt clean \
    && rm -rf /var/lib/apt/lists/*