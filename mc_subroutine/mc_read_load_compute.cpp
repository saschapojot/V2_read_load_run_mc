//
// Created by polya on 7/11/24.
//

#include "mc_read_load_compute.hpp"


///
/// @param coefsJsonStr json data containing initial values of distances
/// @param LVal
/// @param y0Val
/// @param z0Val
/// @param y1Val
void mc_computation::parseJsonData(const std::string &coefsJsonStr, double &LVal, double &y0Val, double &z0Val, double &y1Val){
    std::stringstream ss;
    ss << coefsJsonStr;
    boost::property_tree::ptree pt;

    try {
        boost::property_tree::read_json(ss, pt);
        // Access data from the property tree
        LVal=pt.get<double>("L");
        y0Val=pt.get<double>("y0");
        z0Val=pt.get<double>("z0");
        y1Val=pt.get<double>("y1");


    }
    catch (boost::property_tree::json_parser_error &e) {
        std::cerr << "Error parsing JSON: " << e.what() << std::endl;
        std::exit(1);
    }


}




///
/// @param LCurr current value of L
/// @param y0Curr current value of y0
/// @param z0Curr current value of z0
/// @param y1Curr current value of y1
/// @param LNext  next value of L
/// @param y0Next next value of y0
/// @param z0Next next value of z0
/// @param y1Next next value of y1
void mc_computation::proposal(const double &LCurr, const double& y0Curr,const double& z0Curr, const double& y1Curr,
              double & LNext, double & y0Next, double & z0Next, double & y1Next){


    //next L
    LNext= generate_nearby_normal(LCurr,this->h);

//next y0
    y0Next= generate_nearby_normal(y0Curr,this->h);

//next z0
    z0Next= generate_nearby_normal(z0Curr,this->h);

//next y1
    y1Next= generate_nearby_normal(y1Curr,this->h);

}



///
/// @param LCurr
/// @param y0Curr
/// @param z0Curr
/// @param y1Curr
/// @param LNext
/// @param y0Next
/// @param z0Next
/// @param y1Next
/// @param UNext
/// @return
double mc_computation::acceptanceRatio(const double &LCurr,const double &y0Curr,
                       const double &z0Curr, const double& y1Curr,const double& UCurr,
                       const double &LNext, const double& y0Next,
                       const double & z0Next, const double & y1Next,
                       double &UNext){

    UNext=((*potFuncPtr)(LNext,y0Next,z0Next,y1Next));

    double numerator = -this->beta*UNext;

    double denominator=-this->beta*UCurr;

    double ratio = std::exp(numerator - denominator);

    return std::min(1.0, ratio);



}

void mc_computation::execute_mc(const double& L,const double &y0, const double &z0, const double& y1, const size_t & loopInit, const size_t & flushNum){



    double LCurr = L;
    double y0Curr = y0;
    double z0Curr = z0;
    double y1Curr = y1;
    std::cout<<"Before mc: "<<"LCurr="<<LCurr<<", y0Curr="<<y0Curr<<", z0Curr="<<z0Curr<<", y1Curr="<<y1Curr<<std::endl;
    double UCurr;// = (*potFuncPtr)(LCurr, y0Curr, z0Curr, y1Curr);
    std::random_device rd;
    std::ranlux24_base e2(rd());
    std::uniform_real_distribution<> distUnif01(0, 1);//[0,1)
    size_t loopStart = loopInit;
    for (size_t fls = 0; fls < flushNum; fls++) {
        const auto tMCStart{std::chrono::steady_clock::now()};
        for (size_t j = 0; j < loopToWrite; j++) {
            //propose a move
            double LNext;
            double y0Next;
            double z0Next;
            double y1Next;
            this->proposal(LCurr, y0Curr, z0Curr, y1Curr, LNext, y0Next, z0Next, y1Next);
            UCurr=(*potFuncPtr)(LCurr, y0Curr, z0Curr, y1Curr);
//            std::cout<<"UCurr="<<UCurr<<std::endl;
            double UNext;
            double r = acceptanceRatio(LCurr, y0Curr, z0Curr, y1Curr, UCurr, LNext, y0Next, z0Next, y1Next, UNext);
            double u = distUnif01(e2);
            if (u <= r) {
                LCurr = LNext;
                y0Curr = y0Next;
                z0Curr = z0Next;
                y1Curr = y1Next;
                UCurr = UNext;

            }//end of accept-reject
            U_dist_ptr[varNum*j+0]=UCurr;
            U_dist_ptr[varNum*j+1]=LCurr;
            U_dist_ptr[varNum*j+2]=y0Curr;
            U_dist_ptr[varNum*j+3]=z0Curr;
            U_dist_ptr[varNum*j+4]=y1Curr;

        }//end for loop

        size_t loopEnd = loopStart + loopToWrite - 1;
        std::string fileNameMiddle = "loopStart" + std::to_string(loopStart) + "loopEnd" + std::to_string(loopEnd);
        std::string out_U_distPickleFileName = this->U_dist_dataDir + "/" + fileNameMiddle + ".U_dist.csv";

        //save U_dist_ptr
        saveArrayToCSV(U_dist_ptr,varNum * loopToWrite,out_U_distPickleFileName,varNum);
        const auto tMCEnd{std::chrono::steady_clock::now()};
        const std::chrono::duration<double> elapsed_secondsAll{tMCEnd - tMCStart};
        std::cout << "loop " + std::to_string(loopStart) + " to loop " + std::to_string(loopEnd) + ": "
                  << elapsed_secondsAll.count() / 3600.0 << " h" << std::endl;

        loopStart = loopEnd + 1;

    }//end flush for loop
    std::cout<<"mc executed for "<<flushNum<<" flushes."<<std::endl;



}


void mc_computation::saveArrayToCSV(const std::shared_ptr<double[]>& array, const  size_t& arraySize, const std::string& filename, const size_t& numbersPerRow) {

    std::ofstream outFile(filename);

    if (!outFile.is_open()) {
        std::cerr << "Error opening file: " << filename << std::endl;
        return;
    }
    outFile<<"U,"<<"L,"<<"y0,"<<"z0,"<<"y1"<<"\n";
    for (size_t i = 0; i < arraySize; ++i) {
        outFile << array[i];
        if ((i + 1) % numbersPerRow == 0) {
            outFile << '\n';
        } else {
            outFile << ',';
        }
    }

    // If the last row isn't complete, end the line
    if (arraySize % numbersPerRow != 0) {
        outFile << '\n';
    }

    outFile.close();


}

void mc_computation::init_and_run(){
    this->execute_mc(LInit,y0Init,z0Init,y1Init,loopLastFile+1,newFlushNum);


}