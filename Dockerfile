FROM gcr.io/kaniko-project/executor:v1.18.0 AS kaniko

FROM xarthisius/repo2docker:20241125

RUN apk add --no-cache skopeo coreutils img

COPY --from=kaniko /kaniko /kaniko
COPY . /src
RUN python3 -m pip install /src bdbag==1.6.1 repo2kaniko
COPY repo2docker_config.py /wholetale/repo2docker_config.py
