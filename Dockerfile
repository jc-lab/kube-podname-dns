FROM alpine:3.9.4
MAINTAINER Jichan <development@jc-lab.net>

RUN apk add --no-cache python3 py3-pip libffi py3-cffi py3-cryptography py3-netifaces py3-dnspython py3-requests py3-future py3-setuptools py3-pillow py3-cryptography py3-jsonschema py3-attrs py3-ipaddress py3-yaml zlib zlib-dev jpeg jpeg-dev

RUN pip3 install --ignore-installed https://files.pythonhosted.org/packages/53/3e/beed7bc7005ccb1419cc6429219cbb44bac4cb1a1dd8b4f2fcc707432e1c/logging_helper-1.8.7-py2.py3-none-any.whl

RUN pip3 install --ignore-installed https://files.pythonhosted.org/packages/bb/10/44230dd6bf3563b8f227dbf344c908d412ad2ff48066476672f3a72e174e/wheel-0.33.4-py2.py3-none-any.whl

RUN pip3 install --ignore-installed --no-deps https://files.pythonhosted.org/packages/8d/34/88a5db858c9981b4ae80b50120248748e58c546d5eebbcab62dfebaa2921/networkutil-1.19.8-py2.py3-none-any.whl

RUN pip3 install --ignore-installed --no-deps https://files.pythonhosted.org/packages/2d/b3/093b159d49c72c75fc83dc10a4cb65c229feadceb062164bc168afd23766/classutils-1.18.0-py2.py3-none-any.whl

RUN pip3 install --ignore-installed --no-deps https://files.pythonhosted.org/packages/7c/2b/05b87a2701cd1563c0d34995767e9576cdd3ed8e48b038a0e32ec42d5726/fdutil-1.15.0-py2.py3-none-any.whl

RUN pip3 install --ignore-installed timingsutil appdirs ruamel.yaml

ENV DEFAULT_CA_BUNDLE_PATH /secret/ca.crt
ENV REQUESTS_CA_BUNDLE /secret/ca.crt
ENV SERVICEACCOUNT_PATH /secret/
ENV KUBEAPI_URL https://kubernetes.default.svc.cluster.local

ADD ["run.py", "pydnserver.tar", "/"]

CMD ["python3", "/run.py"]




