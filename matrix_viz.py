from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt
import numpy as np
from matplotlib import cm

def initZerosMatrix(rows, columns):
	matrix = []
	for i in range(0, rows):
		newRow = []
		for j in range(0, columns):
			newRow.append(0)
		matrix.append(newRow)
	return matrix


def setRowColumn(row, column, value, matrix):
	matrix[row][column] = value


def plot3DMatrix(matrix):
	rows = len(matrix)
	columns = len(matrix[0])
	# print rows
	# print columns
	xRows = []
	yCols =[]
	height = []
	for i in range(0, rows):
		for j in range(0, columns):
			# put the rows and columns 
			xRows.append(i)
			yCols.append(j)
			height.append(matrix[i][j]) 
	return xRows, yCols, height

fig = plt.figure()
ax1 = fig.add_subplot(111, projection='3d')

matrix = initZerosMatrix(4, 4)
setRowColumn(0, 0, 0.1, matrix)
setRowColumn(3, 3, 0.4, matrix)

xPos, yPos, dz = plot3DMatrix(matrix)

zPos = [0 for i in range(0, len(dz))]
dx = np.ones(len(xPos))
dy = np.ones(len(yPos))
ax1.set_zlim(0, 0.5)

colors = []
for i in range(0, len(zPos)):
	if dz[i] > 0.3:
		colors.append('b')
	elif dz[i] > 0:
		colors.append('r')
	else:
		colors.append('g')

ax1.bar3d(xPos, yPos, zPos, dx, dy, dz, color=colors)
plt.show()
