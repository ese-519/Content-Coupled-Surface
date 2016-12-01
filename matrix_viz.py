from mpl_toolkits.mplot3d import Axes3D
import matplotlib.pyplot as plt, mpld3
import numpy as np
from matplotlib import cm
import sys

def initZerosMatrix(rows, columns):
	return [[0 for i in range(0, columns)] for j in range(0, rows)]


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
# setRowColumn(int(sys.argv[1]), int(sys.argv[2]), 0.1, matrix)

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
# plt.savefig('gen.png', bbox_inches='tight')
# plt.show()
# mpld3.show()