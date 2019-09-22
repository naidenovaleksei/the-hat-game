# Игра в шляпу

Вам предлагается поучаствовать в игре на загадывание и отгадывание слов. Один из игроков пытается объяснить вытянутое из шляпы слово с помощью набора неоднокоренных слов, которые называются по очереди. После каждого нового сказанного слова другие игроки предлагают несколько вариантов отгадок. Чем раньше игрок угадает вытянутое из шляпы слово, тем больше очков он получит. Чем больше игроков угадают вытянутое из шляпы слово и чем раньше они это сделают, тем больше очков получит объясняющий игрок.

# Правила игры

В рамках подготовке к игре участники разрабатывают свою модель, которая реализует логику загадывания и отгадывания. Для участия в общем соревновании участники разворачивают на удаленном сервере сервис с моделью, который должен быть доступен ведущим по сети интернет.

Игра проходит следующим образом:
- Ведущий вытягивает из шляпы слово `WORD` для команды `i` и отправляет его сервису команды с помощью REST API.
- Сервис команды `i` составляет для ведущего список из `N_EXPLAINING_WORDS` слов, которые ведущий будет сообщать другим участникам по одному.
- Отгадывание проходит `N_EXPLAINING_WORDS` итераций:
    - каждую итерацию `j` ведущий добавляет новую подсказку - новое слово и отправляет сервисам команд все сказанные на данный момент слова;
    - сервисы других игроков пытаются отгадать загаданное слово `WORD`, сообщая `N_GUESSING_WORDS` слов;
    - Как только загаданное слово оказывается в сообщенных ведущему словах, команда получает очки (чем раньше угадала - тем больше, например `N_EXPLAINING_WORDS - j`);
    - Загадывающая команда получает очки за каждую отгадавшую команду (например, столько же очков).

Для тренировки игроков, участвующих в соревновании, можно использовать *только* предоставленный набор данных. Несколько наборов слов для проведения тестовых игр между несколькими игроками предоставлены в папке vocabulary.

# Пример игры

Начнем с примера проведения игры. Для этого откроем ноутбук `GuessingWordByWordSequence.ipynb` и выполним его целиком. Для примера можно взять данные датасета 20 news groups -  их можно загрузить с помощью модуля [`sklearn.datasets`](http://scikit-learn.org/stable/modules/generated/sklearn.datasets.fetch_20newsgroups.html). Они также доступны на [kaggle](https://www.kaggle.com/crawford/20-newsgroups). В качестве примера также подойдет любой достаточно длинный файл с текстом (приблизительно 1 миллиона строк должно быть достаточно).

Данный пример позволяет проводить локальные игры между несколькими игроками в рамках юпитер ноутбука (нужно инициализировать объекты соответствующих классов в ноутбуке), а также тестировать развернутые удаленно сервисы (с помощью класса `RemotePlayer`).

# Как создать игрока

Удобно сначала создать локального игрока, реализовать желаемую логику по загадыванию и отгадыванию слов, а также отладить его работу локально, а затем перенести код и обученную модель в приложение на flask, которое можно запускать как полноценного удаленный сервис с реализованным игроком.

## Как реализовать локального игрока

Обратим внимание на класс `LocalFasttextPlayer` в ноутбуке `GuessingWordByWordSequence.ipynb`. Для описания локального игрока необходимо создать подобный класс с обязательным присутствием методов explain и guess, которые принимают на вход те же аргументы и возвращают объект того же типа. Предлагается инициализировать класс обученной моделью и другими необходимыми параметрами, описывающими логику загадывания и отгадывания. По умолчанию предлагается следующий подход:
1. Имеющийся корпус текстов предобрабатывается - например, удаляются специальные символы, слова приводятся к начальной форме, и так далее;
2. На текстах обучаются эмбеддинги;
3. Обученные эмбеддинги используются, чтобы находить ближайшие по косинусному расстоянию слова к загадываемому слову (`/explain`) и к предлагаемой для отгадывания последовательности слов (`/guess`);
4. Поверх найденных ближайших слов реализуется определенная логика - например, убрать из списка однокоренные слова или убрать слишком короткие/бессмысленные слова.

## Как реализовать сервис с удаленным игроком

Обратим внимание на класс `RemotePlayer` в ноутбуке `GuessingWordByWordSequence.ipynb`. Этот класс используется для коммуникации с сервисом, поднимаем на удаленной (или локальной) машине. Сам запускаемый сервис описан в папке docker-flask-app. Содержимое папки:

```
docker-flask-app
- templates
- Dockerfile
- app.py
- player.py
- requirements.txt
```

В скрипте app.py создается простое [Flask](https://palletsprojects.com/p/flask/)-приложение, отображающее на главной странице гифки с котами и умеющее обрабатывать два типа запросов: /explain и /guess. Запросы к приложению могут выглядеть следующим образом: `127.0.0.1:5000/explain?word=riddle&n_words=10`

В скрипте `player.py` находится класс, описывающий игрока (в примере класс `LocalFasttextPlayer`).

В requirements.txt перечислен список библиотек, необходимых для работы app.py и player.py

Dockerfile представляет собой файл, задающий параметры сборки докер-образа.

Для модификации сервиса должно быть достаточно переместить код класса своего игрока в `player.py`, скопировать необходимые для работы файлы в папку docker-flask-app, затем проинициализировать объект класса с использованием нужных файлов в скрипте `app.py`.

## Запуск созданного сервиса

Ниже рассматриваются две возможности запуска данного приложения:
1. Без использования docker-образа;
2. С помощью использования докер-образа.

Запускать сервис можно локально, на удаленном сервере и с помощью специализированных платформ для этого - например, heroku.

Использование docker является дополнительным этапом, обеспечивающим возможность подготовить самодостаточный образ, который можно запускать изолированно в контейнере на любой операционной системе. Другими словами, изменения, которые будут происходить внутри контейнера, никак не затронут саму операционную систему и файлы, к которым она имеет доступ. Это предоставляет возможности для простого масштабирования созданного сервиса. Дополнительным преимуществом такого подхода является возможность тестировать работу решения локально (например, проверяя, что внутри контейнера устанавливаются необходимые для работы сервиса зависимости), при этом гарантируя его работу на удаленном сервере.

### Без использования docker

При запуске непосредственно flask-приложения локально достаточно выполнить команду `python app.py`. Проверить работу приложения можно, зайдя в браузере на `127.0.0.1:5000`. Если приложение успешно запустилось, вы увидите гифки с котиками.

### С использованием docker

Запуск с помощью docker можно произвести следующим образом. Внутри папки docker-flask-app выполните две команды:
1. Собрать докер-образ, руководствуясь инструкцией в Dockerfile: `docker build -t hat_player .`
2. Запустить собранный образ, связав порт 5000 внутри докер-контейнера с портом 5000 на используемом сервере: `docker run --rm -it -p 5000:5000 hat_player`

При запуске контейнера с docker-образом выполняются команды, описанные в Dockerfile. В частности, внутри нашего докер-образа будет выполнена команда `python app.py`.

### Запуск на удаленном сервере и heroku

Если вы запускаете приложение на удаленном сервере, необходимо, чтобы порт 5000 был открыт для входящий соединений извне. При использовании aws, google cloud, azure или других облачных провайдеров эти параметры есть в панели управления созданным сервером.

Для запуска сервиса в рамках участия в соревновании предлагается воспользоваться сервисом heroku. Запуск с бесплатным аккаунтом обладает следующими особенностями:
- (+) Запущенный сервис будет существовать на heroku неограниченное время, в отличие от поднятых временно серверов на облачных провайдерах;
- (+) Поднятый сервис не требует вашего дальнейшего вмешательства а также не зависит от перезагрузок сервера, переустановок пакетов и так далее;
- (-) Сервис "засыпает" после получаса неиспользования;
- (-) В месяц доступно около 500 часов для работы запущенных сервисов;
- (-) На один сервис доступно 512мб RAM.

Приложение на heroku можно запустить [с помощью git](https://devcenter.heroku.com/articles/git) и [с помощью docker-образа](https://devcenter.heroku.com/articles/container-registry-and-runtime).

# Полезные ссылки
- an explanation of what is docker, container, dockerhub and etc https://www.freecodecamp.org/news/docker-simplified-96639a35ff36/
- a comprehensive guide about docker https://docker-curriculum.com
- how to run dockerized apps on heroku (short post) https://medium.com/travis-on-docker/how-to-run-dockerized-apps-on-heroku-and-its-pretty-great-76e07e610e22
- how to run docker on heroku (official docs) https://devcenter.heroku.com/articles/container-registry-and-runtime
- to install latest fasttext, follow the instructions here (pip install won't do it) https://github.com/facebookresearch/fastText
- what is Flask https://palletsprojects.com/p/flask/
