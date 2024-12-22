import numpy as np

test = [[1,2,3,4], [6,7,8,9]]
print(np.mean(test))

avg = np.sum(test, axis=0) / len(test)
print(avg)