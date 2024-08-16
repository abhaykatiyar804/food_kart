#FROM akdocker528/food_kart
#RUN apt-get update
#RUN pip install poetry==1.7.1
#
#WORKDIR app/
#COPY src src/
#COPY README.md poetry.toml pyproject.toml poetry.lock ./
#
#RUN poetry install --no-root # Do not install the root package (your project).

#FROM akdocker528/food_kart as production
#RUN poetry install --no-interaction --no-ansi --without dev
#WORKDIR app/
#ENTRYPOINT poetry run python -m tdd_food_kart_1


FROM python as base
RUN apt update
RUN apt  install -y  git
RUN pip install poetry==1.7.1


#WORKDIR app/
#COPY src src/
#COPY README.md poetry.toml pyproject.toml poetry.lock ./

#RUN poetry install --no-root # Do not install the root package (your project).

#FROM base as production
#RUN poetry install --no-interaction --no-ansi --without dev
#WORKDIR app/
#ENTRYPOINT poetry run python -m sample_app
