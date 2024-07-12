//
// Created by polya on 7/11/24.
//

#ifndef V2_READ_LOAD_RUN_MC_MC_READ_LOAD_COMPUTE_HPP
#define V2_READ_LOAD_RUN_MC_MC_READ_LOAD_COMPUTE_HPP
#include "../potentialFunction/potentialFunctionPrototype.hpp"
#include <boost/filesystem.hpp>
#include <chrono>
#include <cstdlib>
#include <cxxabi.h>
#include <fstream>
#include <initializer_list>
#include <iomanip>
#include <iostream>
#include <memory>
#include <random>
#include <regex>
#include <sstream>
#include <string>
#include <typeinfo>
#include <vector>

namespace fs = boost::filesystem;


class mc_computation {
public:
    mc_computation(const std::string &TStr,const std::string &coefsJsonStr,
                   const std::string &funcNameStr, const std::string &jsonToCppInitValsStr,
                   const std::string &loopToWriteStr, const std::string &newFlushNumStr,
                   const std::string &loopLastFileStr,const std::string&TDirRootStr,
                   const std::string &U_dist_dataDirStr) {
        //parse T
        try {
            this->T = std::stod(TStr); // Attempt to convert string to double

        } catch (const std::invalid_argument &e) {
            std::cerr << "Invalid argument: " << e.what() << std::endl;
            std::exit(1);
        } catch (const std::out_of_range &e) {
            std::cerr << "Out of range: " << e.what() << std::endl;
            std::exit(1);
        }

        if (T <= 0) {
            std::cerr << "T must be >0" << std::endl;
            std::exit(1);
        }

        std::cout << "T=" << T << std::endl;
        this->beta = 1 / T;
        double stepForT1 = 0.1;
        this->h = stepForT1 * T > 0.2 ? 0.2 : stepForT1 * T;//stepSize;
        std::cout << "h=" << h << std::endl;

        //set potential function
        this->potFuncPtr = createPotentialFunction(funcNameStr, coefsJsonStr);
        potFuncPtr->init();

        //parse json to get initial value
        this->parseJsonData(jsonToCppInitValsStr, this->LInit, this->y0Init, this->z0Init, this->y1Init);
        this->varNum = 5;
//
//        std::cout<<"LInit="<<LInit<<", y0Init="<<y0Init
//        <<", z0Init="<<z0Init<<", y1Init="<<y1Init<<std::endl;

        try {
            this->loopToWrite = std::stoull(loopToWriteStr);
        }
        catch (const std::invalid_argument &e) {
            std::cerr << "Invalid argument: " << e.what() << std::endl;
            std::exit(1);
        } catch (const std::out_of_range &e) {
            std::cerr << "Out of range: " << e.what() << std::endl;
            std::exit(1);
        }

//        std::cout<<"loopToWrite="<<loopToWrite<<std::endl;

//parse new flush number

        try {
            this->newFlushNum = std::stoull(newFlushNumStr);
        }
        catch (const std::invalid_argument &e) {
            std::cerr << "Invalid argument: " << e.what() << std::endl;
            std::exit(1);
        } catch (const std::out_of_range &e) {
            std::cerr << "Out of range: " << e.what() << std::endl;
            std::exit(1);
        }
//        std::cout<<"newFlushNum="<<newFlushNum<<std::endl;
//parse loop in last file
        try {
            //if loopLastFileStr is "-1", loopLastFile uses the overflowed value
            //and loopLastFile+1 will be 0
            this->loopLastFile = std::stoull(loopLastFileStr);

        }
        catch (const std::invalid_argument &e) {
            std::cerr << "Invalid argument: " << e.what() << std::endl;
            std::exit(1);
        } catch (const std::out_of_range &e) {
            std::cerr << "Out of range: " << e.what() << std::endl;
            std::exit(1);
        }

//        std::cout<<"loopLastFile+1="<<loopLastFile+1<<std::endl;



        this->TDirRoot = TDirRootStr;
        this->U_dist_dataDir = U_dist_dataDirStr;
//        std::cout<<"TDirRoot="<<TDirRoot<<std::endl;
//        std::cout<<"U_dist_dataDir="<<U_dist_dataDir<<std::endl;
        try {
            this->U_dist_ptr= std::shared_ptr<double[]>(new double[loopToWrite * varNum],
                                                  std::default_delete<double[]>());
        }
        catch (const std::bad_alloc &e) {
            std::cerr << "Memory allocation error: " << e.what() << std::endl;
            std::exit(2);
        } catch (const std::exception &e) {
            std::cerr << "Exception: " << e.what() << std::endl;
            std::exit(2);
        }


    }
public:
    ///
    /// @param coefsJsonStr json data containing initial values of distances
    /// @param LVal
    /// @param y0Val
    /// @param z0Val
    /// @param y1Val
    void parseJsonData(const std::string &coefsJsonStr, double &LVal, double &y0Val, double &z0Val, double &y1Val);


    ///
    /// @param LCurr current value of L
    /// @param y0Curr current value of y0
    /// @param z0Curr current value of z0
    /// @param y1Curr current value of y1
    /// @param LNext  next value of L
    /// @param y0Next next value of y0
    /// @param z0Next next value of z0
    /// @param y1Next next value of y1
    void proposal(const double &LCurr, const double& y0Curr,const double& z0Curr, const double& y1Curr,
                  double & LNext, double & y0Next, double & z0Next, double & y1Next);



    ///
    /// @param x
    /// @param sigma
    /// @return a value around x, from a  normal distribution
    static double generate_nearby_normal(const double & x, const double &sigma){
        std::random_device rd;  // Random number generator
        std::mt19937 gen(rd()); // Mersenne Twister engine
        std::normal_distribution<> d(x, sigma); // Normal distribution with mean rCurr and standard deviation sigma

        double xNext = d(gen);


        return xNext;


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
    double acceptanceRatio(const double &LCurr,const double &y0Curr,
                           const double &z0Curr, const double& y1Curr,const double& UCurr,
                           const double &LNext, const double& y0Next,
                           const double & z0Next, const double & y1Next,
                           double &UNext);

    void execute_mc(const double& L,const double &y0, const double &z0, const double& y1, const size_t & loopInit, const size_t & flushNum);

    static void saveArrayToCSV(const std::shared_ptr<double[]>& array, const  size_t& arraySize, const std::string& filename, const size_t& numbersPerRow) ;

    void init_and_run();
public:
    double T;// temperature
    double beta;
    double h;// step size
    size_t loopToWrite;
    size_t newFlushNum;
    size_t loopLastFile;
    std::shared_ptr<potentialFunction> potFuncPtr;
    std::string TDirRoot;
    std::string U_dist_dataDir;
    std::shared_ptr<double[]> U_dist_ptr;
    size_t varNum;
    double LInit;
    double y0Init;
    double z0Init;
    double y1Init;
};

























#endif //V2_READ_LOAD_RUN_MC_MC_READ_LOAD_COMPUTE_HPP
