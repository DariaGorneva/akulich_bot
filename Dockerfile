FROM python:3.10-alpine as build

COPY req.txt req.txt
RUN pip install -r req.txt

COPY src/ src/


#FROM build AS development
#
#RUN poetry install --no-root
#
#FROM development AS linters
#
#CMD ["poetry", "run", "mypy"]
#
#FROM development AS tests
#
#COPY tests/ tests/
#
#CMD ["poetry", "run", "pytest"]
#
#
#FROM harbor.chatme.ai/parent-docker-images/python:3.9-alpine3.15 AS runtime
#
#ENV PATH="/build/.venv/bin/:${PATH}" \
#    PYTHONPATH="/build/.venv/lib/python3.9/site-packages/:${PYTHONPATH}" \
#    PYTHONOPTIMIZE=2
#
#WORKDIR /srv/
#
#COPY --from=build /build/.venv/ /build/.venv/
#COPY --from=build /build/app/ /srv/app/
#
#EXPOSE 80/tcp
#
#CMD ["python", "-m", "app"]
