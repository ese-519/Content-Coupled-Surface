#include "mbed.h"


Serial pc(USBTX, USBRX);
// serial pins for communication with Raspberry
Serial mySerial(p9, p10);

#define MAXCOUNT 10
#define LEN 16
#define THRESHOLD 10 // if user hasn't moved above this point inflate
#define WINDOW 4
#define PRESSURE_THRESHOLD 30.0 // if the pressure is less than this set 0
#define AVERAGE_PRESSURE_THRESHOLD 10.0 // if the average of a WINDOW*WINDOW is less than this don't consider it to inflate
#define HEAT_THRESH 5

int sendCounter = 0;
float prevPressureVal[LEN][LEN]={0};
float pressureMat[LEN][LEN] = {0};
int counterTable[LEN][LEN] = {0};

// For the 4*4 grid logic

int previousRead[WINDOW][WINDOW] = {0};
int counterRead[WINDOW][WINDOW] = {0};

// mux
DigitalOut select0_mux1(p24);
DigitalOut select1_mux1(p23);
DigitalOut select2_mux1(p22);
DigitalOut select3_mux1(p21);

// demux
DigitalOut select0_demux1(p28);
DigitalOut select1_demux1(p27);
DigitalOut select2_demux1(p26);
DigitalOut select3_demux1(p25);

AnalogIn analog_read_1(p20);

int getBit(int num, int bitNo) {
        return ((num&(1<<bitNo)) > 0)?1:0;
}


void getPressureMatrix(){

    printf("******************************\n");
    for (int rows = 0; rows < LEN; rows++) {
    
        select0_demux1 = getBit(rows,0);
        select1_demux1 = getBit(rows,1);
        select2_demux1 = getBit(rows,2);
        select3_demux1 = getBit(rows,3);
    

     for (int col = 0; col < LEN; col++) {
            //pc.printf("Select Line: %d ", col);
            
            // This code will select the select lines on the mbed
            select0_mux1 = getBit(col, 0);
            select1_mux1 = getBit(col, 1);
            select2_mux1 = getBit(col, 2);
            select3_mux1 = getBit(col, 3);
            //wait(0.05);
            float x = analog_read_1.read()*100;
            float val = x;
            if(val < PRESSURE_THRESHOLD) {
                val = 0.0;
            }
            pressureMat[rows][col] = val;
//            if(abs((int)pressureMat[rows][col] - (int)prevPressureVal[rows][col]) > HEAT_THRESH) {
//                mySerial.printf("H %d %d %d\n", rows, col, (int)pressureMat[rows][col]);
//                printf("Sent for heat map\n");
//            }
            if( sendCounter == 0) {
                mySerial.printf("%d\n", (int)x);
            }
        
        }  
//        printf("\n");
    }
    sendCounter  = (sendCounter + 1)%4;
    printf("********************************\n");
}

// for comparison, we form a 4*4 current matrix and compare it with the 4*4 previous matrix
// If the average of one is almost equal to the average of previous, we increment the not moved matrix by 1
// This is how we get to control the final inflation and deflation of the layer

void ComparePressureVal(){

  for(int rows = 0; rows < LEN; rows++){
    for(int col = 0; col < LEN; col++){
       //TODO: the pressure might differ a bit but could be in same range. We might want to consider
       // this situation too.
       if(abs((int)pressureMat[rows][col] - (int)prevPressureVal[rows][col]) > HEAT_THRESH) {
            //mySerial.printf("H %d %d %d\n", rows, col, (int)pressureMat[rows][col]);
        }
            prevPressureVal[rows][col] = pressureMat[rows][col];
    }
}
}


 void comparePressureOnAnAverage() {
    for(int rows = 0; rows < LEN; rows = rows + WINDOW) {
        for(int col = 0; col < LEN; col = col + WINDOW) {
            float avg = 0;
            for (int i = rows; i < rows + WINDOW; i++) {
                for (int j = col; j < col + WINDOW; j++) {
                        avg += pressureMat[i][j];
                }
            }
            avg = (avg/(WINDOW*WINDOW))*1.3;
            if(avg > AVERAGE_PRESSURE_THRESHOLD) {
            if(abs(previousRead[rows/4][col/4] - avg) < THRESHOLD) {
                counterRead[rows/4][col/4] += 1;
                if(counterRead[rows/4][col/4] == MAXCOUNT) {
                    // the person is really lazy and has not moved
                    // inflate the area automatically
                    // send signal to the pins of the mbed to actually infalte that area for row/4 and col/4
                    // reset the matrix back to zeros since this node has been inflated
                    pc.printf("Sent to RaspPi %d %d\n", rows/4, col/4);
                    mySerial.printf("%d %d\n", rows/4, col/4);
                    counterRead[rows/4][col/4] = 0;                }
            } else {
                counterRead[rows/4][col/4] = 0;
            }
            } else {
                avg = 0.0;    
            }
            printf("%f ", avg);
            previousRead[rows/4][col/4] = avg;
        }
        printf("\n");
    }
    printf("********************************\n");
 }   
    
int main() {
    mySerial.baud(9600);
    while(1) {
            wait(0.5); // read pressure value after each 0.05 seconds
            getPressureMatrix();
//            ComparePressureVal();
            comparePressureOnAnAverage();
        }
}