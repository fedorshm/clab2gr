Здесь находится актуальная версия модели YOLO11s (best.pt) с кастомной аугментацией, которая обучена на 3 версии датасета и спользуется в веб сервисе.  
Для начала мы обучили YOLOv8s на второй версии датасета без кастомной аугментации, метрики которой представлены в файле (YOLOv8s datasetv2 no aug)  
Мы получили следующие метрики на валидационном наборе данных, так как вторая версия датасета не имела тестовой выборки:  
Precision: 0.7920323169907539  
Recall: 0.7560062727200952  
F1 Score: 0.7736000947545945  
mIoU (mAP50-95): 0.667667239187264  
Fitness: 0.6772798539360997  
  
Разработав третью версию датасета, в котором было делением на train:8000, val:1000, test:1000, в ограниченных временных рамках было принято решение обучить модель YOLOv8n datasetv3 без кастомной аугментации для сравнения с прошлой моделью, чтобы убедится в повышении качетсва датасета. Так были получены следующие метрики на валидационном наборе:  
Precision: 0.9178949611065826  
Recall: 0.905449894925233  
F1 Score: 0.9116299567105631  
mIoU (mAP50-95): 0.8611769247661971  
Fitness: 0.8679499326086586  
  
И на тестовом:  
Precision: 0.9251046987669514  
Recall: 0.9009499875730863  
F1 Score: 0.9128675861602142  
mIoU (mAP50-95): 0.8572217963696294  
Fitness: 0.863697800406339  
  
Что свидетельствует о повышении качсетва датасета, так как была использована модель версии ниже, но метрики качества получены лучше в файле (YOLOv8n datasetv3 no aug). Также стоит отметить совсем незначительное изменение метрик на валидационном и тестовом наборах, что означает, что ваша модель хорошо обобщает на новые данные, и не переобучилась.  
После этого было принято решение перейти к обучению YOLO11s с кастомной аугментацией (YOLO11s datasetv3 aug) и без неё (YOLO11s datasetv3 no aug). Так были получены следующие метрки (YOLO11s datasetv3 no aug):  
На валидационном наборе:  
Precision: 0.9307130452447772  
Recall: 0.9325349599174734  
F1 Score: 0.9316231118319964  
mIoU (mAP50-95): 0.8729714141592846  
Fitness: 0.8806306033457634  
  
На тестотов наборе:  
Precision: 0.9384431100332997  
Recall: 0.9408006413105365  
F1 Score: 0.9396203968978849  
mIoU (mAP50-95): 0.8650026508642005  
Fitness: 0.8720242549809656  
  
Данные метрики свидетельствуют о целесообразности перехода от YOLO8n к YOLO11s. Также стоит отметить то, что метрики на валидационной и тестовой выборках почти не отличны, что свидетельствует о высоком качетсве обобщения модели.  
  
Далее представлены настройки YOLO11s с кастомной аугментацией:  
        "flipud": 0.0,  # Вертикальное отражение  
        "fliplr": 0.0,  # Горизонтальное отражение  
        "mosaic": 0.0,  # Mosaic  
        "mixup": 0.0,   # MixUp  
        "perspective": 0.0,  # Перспективное искажение  
        "scale": 0.0,  # Масштабирование  
        "shear": 0.0,  # Сдвиг  
        "rotation": 0.015,  # Максимальный угол поворота ±15° (в долях от 1)  
        "rotate90": True,  # Разрешены повороты на 90°  
        "brightness": 0.1,  # Небольшие изменения яркости  
        "contrast": 0.1,    # Небольшие изменения контраста  
  
Метрики на валидационном наборе:  
Precision: 0.9307568298029705  
Recall: 0.9327242493993069  
F1 Score: 0.9317395010234168  
mIoU (mAP50-95): 0.8724979847312644  
Fitness: 0.8802158255795718  
  
И метрики на тестовом наборе:  
Precision: 0.9380473582704963  
Recall: 0.9408674650583878  
F1 Score: 0.9394552952826358  
mIoU (mAP50-95): 0.8652408130635052  
Fitness: 0.8722626922069484  
  
Данные метрики изменились крайне незначительно по сравнению с версией без кастомной аугментации, но даже незначительное улучшение метрик может быть целесообразно. После этого было принято решение обучить эту же модель, но увеличив imgsz до 960. После были получены следующие метрики:  
  
Метрики на валидационном наборе:  
Precision: 0.9710033947119321  
Recall: 0.9225413194072026  
F1 Score: 0.9461522046213046  
mIoU (mAP50-95): 0.9534837961529748  
Fitness: 0.9550608515954393  
  
И метрики на тестовом наборе:  
Precision: 0.966216471665268  
Recall: 0.9193137020030303  
F1 Score: 0.9421817310669728  
mIoU (mAP50-95): 0.9338875015065237  
Fitness: 0.9355054868752979  
  
Модель с imgsz=960 выглядит предпочтительнее, поскольку она имеет лучшее качество локализации (mIoU), высокую точность и более сбалансированные метрики (F1 и Fitness). Выбор прошлого варианта модели имеет смысл только в случае, если мы работаем в условиях ограниченных вычислительных ресурсов или с задачей, где пропуски объектов недопустимы, поэтому было принято решение остановится на этой версии модели, настроить confidrnce и iou. Так методом перебора были оптимально подобраны следущие параметры:  
Обший порог для всех классов conf=0.4, iou=0.51  
  
А также индивидуальный для определённых классов:  
    0: 0.3,  # title  
    1: 0.1,  # paragraph  
    9: 0.15, # footer  
    11: 0.1,  # formula  
    10: 0.88, # footnote  
    6: 0.9, # numbered_list  
    7: 0.9 # marked_list  
  
Ссылка на гугл диск с папками runs для всеж перечисленных моделей:  
https://drive.google.com/drive/folders/1fXM9wnptK66hw0_CUtLNPypN0U9ws4-Q?usp=sharing  

Файл annotated_document1.pdf содержит детектированные элементы документа с учётом всех настроек актуальной модели, код для использования модели представлен в файле Сonfidence.ipynb.  
Файл Predict.ipynb содержит результаты работы модели на тестовых датасетах команд.  
Ссылка на результаты работы модели на тестовых датасетах других команд со всеми данными для оценки: 
https://drive.google.com/drive/folders/1tuWEuzW_-BF-v7A-2mkPZVMTdjPCp_jT?usp=drive_link  
