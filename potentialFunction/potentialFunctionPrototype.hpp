//
// Created by polya on 7/11/24.
//

#ifndef V2_READ_LOAD_RUN_MC_POTENTIALFUNCTIONPROTOTYPE_HPP
#define V2_READ_LOAD_RUN_MC_POTENTIALFUNCTIONPROTOTYPE_HPP
#include <boost/property_tree/json_parser.hpp>
#include <boost/property_tree/ptree.hpp>
#include <fstream>
#include <iostream>
#include <math.h>
#include <memory>
#include <string>

class potentialFunction {
//base class for potential function
public:
    virtual double operator()(const double&L,const double &y0, const double &z0, const double& y1) const = 0;
    virtual std::string getParamStr() const = 0;
    virtual void json2Coefs(const std::string &coefsJson)=0;
    virtual ~ potentialFunction() {};

};

std::shared_ptr<potentialFunction>  createPotentialFunction(const std::string& funcName, const std::string &) ;


#endif //V2_READ_LOAD_RUN_MC_POTENTIALFUNCTIONPROTOTYPE_HPP
