# import eel
# eel.init("/Users/estyle-086/Desktop/Project-01/submit00/task_3/web")
# eel.start("main.html")

import eel
import numpy as np

eel.init("web")
eel.js_function(np.random.rand(4).tolist()) # JSON serializableでないとダメ
eel.start("main.html")