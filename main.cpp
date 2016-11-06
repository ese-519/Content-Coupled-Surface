#include "mbed.h"


Serial pc(USBTX, USBRX);

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


void getPressureMatrix(float matrix[16][16]){

    printf("******************************\n");
    for (int rows = 0; rows <= 15; rows++) {
    
        select0_demux1 = getBit(rows,0);
        select1_demux1 = getBit(rows,1);
        select2_demux1 = getBit(rows,2);
        select3_demux1 = getBit(rows,3);
    

     for (int col = 0; col<= 15; col++) {
            //pc.printf("Select Line: %d ", col);
            
            // This code will select the select lines on the mbed
            select0_mux1 = getBit(col, 0);
            select1_mux1 = getBit(col, 1);
            select2_mux1 = getBit(col, 2);
            select3_mux1 = getBit(col, 3);
            //wait(0.05);
            matrix[rows][col] = analog_read_1.read();
            printf("%f ", matrix[rows][col]);
        
        }  
        printf("\n");
    }
    printf("********************************\n");
}
    
int main() {
    float pressureMat[16][16];
    while(1) {
        
            
            //ait(3);
            getPressureMatrix(pressureMat);
        }
}
