//
// Created by polya on 7/11/24.
//
#include "potentialFunctionPrototype.hpp"

class V2 : public potentialFunction {

public:
    V2(const std::string &coefsJson):potentialFunction(){


    }
    void json2Coefs(const std::string &coefsJson){
        std::stringstream ss;
        ss<<coefsJson;
        boost::property_tree::ptree pt;
        try {
            boost::property_tree::read_json(ss, pt);
            // Access data from the property tree
        }

    }


public:
    double a1;
    double a2;
    double c1;
    double c2;
};