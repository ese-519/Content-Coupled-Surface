#include "mbed.h"


Serial pc(USBTX, USBRX);

#define MAXCOUNT 5
#define LEN 16

float prevPressureVal[LEN][LEN]={0};
float pressureMat[LEN][LEN] = {0};
int counterTable[LEN][LEN] = {0};

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
            pressureMat[rows][col] = analog_read_1.read();
            printf("%f ", pressureMat[rows][col]);
        
        }  
        printf("\n");
    }
    printf("********************************\n");
}

void ComparePressureVal(){
    
  for(int rows = 0; rows < LEN; rows++){
    for(int col = 0; col < LEN; col++){
       //TODO: the pressure might differ a bit but could be in same range. We might want to consider
       // this situation too.
       if(pressureMat[rows][col] == prevPressureVal[rows][col]){
                counterTable[rows][col] += 1;              
        }
        //Copy current pressure value
        prevPressureVal[rows][col] = pressureMat[rows][col];
        
        if(counterTable[rows][col] == MAXCOUNT){
            //call inflated func. 
            //TODO: Inflated func will will reset back
       }
    }
   }   
    
 }   
    
int main() {
    
    while(1) {
        
            
            wait(0.05); // read pressure value after each 0.05 seconds
            getPressureMatrix();
            ComparePressureVal();
            
        }
}
